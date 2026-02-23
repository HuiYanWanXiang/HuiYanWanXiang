#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
================================================================================
项目名称: 绘演万象：Web端交互式物理仿真实验平台
Project Name: HuiyanWanxiang Web Interactive Physics Simulation Platform
文件名称: main.py
创建日期: 2026-02-06
作者: 大连理工大学开发团队
版本: V1.0.0
================================================================================
"""

import os
import datetime
import re
import asyncio
import uuid
from typing import Dict, Any, Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from openai import AsyncOpenAI

from prompts.loader import load_system_prompt
from prompts.physics_knowledge import get_physics_prompt
from utils.logger import setup_logger
from utils.exceptions import LLMConnectionError, PromptEmptyError, HuiyanError

from manim_engine.router import router as manim_router, mount_runs

# ==============================================================================
# 1. 系统初始化与配置
# ==============================================================================

logger = setup_logger()

app = FastAPI(
    title="绘演万象后端引擎",
    description="基于 LLM 的物理仿真网页生成服务",
    version="1.0.0"
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# Manim 渲染结果静态挂载（/video/runs/...）
mount_runs(app)
# Manim API 路由（/api/generate-video, /api/video-status/{job_id}）
app.include_router(manim_router)

SAVE_DIR = "saved_projects"
os.makedirs(SAVE_DIR, exist_ok=True)

# ==============================================================================
# 2. 数据模型
# ==============================================================================

class GenRequest(BaseModel):
    prompt: str
    api_key: str
    base_url: str
    model: str

# ==============================================================================
# 3. HTML 异步任务管理（内存版）
# ==============================================================================

# job_id -> job_info
# job_info: {status, created_at, prompt, model, saved_path, html, error}
html_jobs: Dict[str, Dict[str, Any]] = {}
html_jobs_lock = asyncio.Lock()

def _mask_key(k: str) -> str:
    if not k:
        return "***"
    return k[:6] + "******" if len(k) > 6 else "***"

def _now_ts() -> str:
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

async def _set_job(job_id: str, patch: Dict[str, Any]) -> None:
    async with html_jobs_lock:
        job = html_jobs.get(job_id)
        if not job:
            return
        job.update(patch)

async def _get_job(job_id: str) -> Optional[Dict[str, Any]]:
    async with html_jobs_lock:
        job = html_jobs.get(job_id)
        return dict(job) if job else None

def _build_system_prompt(user_prompt: str) -> str:
    base_system_prompt = load_system_prompt()

    knowledge_augmentation = ""
    if "振动" in user_prompt or "oscillation" in user_prompt.lower():
        knowledge_augmentation = get_physics_prompt("mechanics_damped_oscillation")
    elif "波" in user_prompt or "wave" in user_prompt.lower():
        knowledge_augmentation = get_physics_prompt("wave_double_slit_interference")

    final_system_prompt = base_system_prompt
    if knowledge_augmentation:
        final_system_prompt += "\n\n【补充物理领域知识】\n" + knowledge_augmentation
    return final_system_prompt

async def _html_worker(job_id: str, req: GenRequest) -> None:
    """
    后台执行 HTML 生成，写回 html_jobs[job_id]
    """
    prompt = (req.prompt or "").strip()
    masked_key = _mask_key(req.api_key)
    logger.info(f"[HTML_JOB:{job_id}] start | prompt='{prompt}' | model={req.model} | key={masked_key}")

    await _set_job(job_id, {"status": "running"})

    client = AsyncOpenAI(api_key=req.api_key, base_url=req.base_url, timeout=None)

    try:
        final_system_prompt = _build_system_prompt(prompt)
        if "【补充物理领域知识】" in final_system_prompt:
            logger.info(f"[HTML_JOB:{job_id}] knowledge augmentation enabled")

        logger.info(f"[HTML_JOB:{job_id}] calling LLM...")
        resp = await client.chat.completions.create(
            model=req.model,
            messages=[
                {"role": "system", "content": final_system_prompt},
                {"role": "user", "content": f"教学主题：{prompt}。请生成中文网页。"}
            ],
            temperature=0.7,
            max_tokens=8192,
            stream=False
        )

        raw_content = (resp.choices[0].message.content or "")
        clean_html = raw_content.replace("```html", "").replace("```", "").strip()
        if not clean_html.endswith("</html>"):
            logger.warning(f"[HTML_JOB:{job_id}] html truncated, auto append </html>")
            clean_html += "\n\n</body></html>"

        ts = _now_ts()
        safe_prompt = re.sub(r'[\\/*?:"<>|]', "", prompt)[:15]
        filename = f"{ts}_{safe_prompt}.html"
        file_path = os.path.join(SAVE_DIR, filename)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(clean_html)

        await _set_job(job_id, {
            "status": "done",
            "html": clean_html,
            "saved_path": filename,
            "timestamp": ts,
        })

        logger.info(f"[HTML_JOB:{job_id}] done | saved={file_path}")

    except HuiyanError as e:
        # 业务可预期错误
        await _set_job(job_id, {"status": "error", "error": str(e)})
        logger.error(f"[HTML_JOB:{job_id}] HuiyanError: {e}")

    except Exception as e:
        # LLM/网络/未知错误
        # 你也可以更精细：遇到 openai 的认证错误、超时等都归到 LLMConnectionError
        msg = str(e)
        await _set_job(job_id, {"status": "error", "error": msg})
        logger.error(f"[HTML_JOB:{job_id}] Exception: {msg}")

    finally:
        try:
            await client.close()
        except Exception:
            pass

# ==============================================================================
# 4. 路由
# ==============================================================================

@app.get("/")
async def read_index():
    index_path = "web_interface/index.html"
    if not os.path.exists(index_path):
        return "System Error: index.html not found."
    return FileResponse(index_path)

@app.post("/api/generate-html")
async def generate_html(request: GenRequest):
    """
    异步提交：秒回 job_id，后台生成
    """
    user_prompt = (request.prompt or "").strip()
    if not user_prompt:
        raise HTTPException(status_code=400, detail="Prompt 不能为空")

    job_id = uuid.uuid4().hex[:12]
    async with html_jobs_lock:
        html_jobs[job_id] = {
            "status": "queued",
            "created_at": datetime.datetime.now().isoformat(),
            "prompt": user_prompt,
            "model": request.model,
            "saved_path": None,
            "timestamp": None,
            "html": None,
            "error": None,
        }

    masked_key = _mask_key(request.api_key)
    logger.info(f"[HTML_JOB:{job_id}] queued | model={request.model} | key={masked_key}")

    # 后台启动任务（不阻塞请求）
    asyncio.create_task(_html_worker(job_id, request))

    return JSONResponse(content={"status": "queued", "job_id": job_id})

@app.get("/api/html-status/{job_id}")
async def html_status(job_id: str):
    job = await _get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job_id 不存在")

    # 返回给前端：done 时带 html / saved_path；error 时带 error
    return JSONResponse(content=job)

# ==============================================================================
# 5. 入口
# ==============================================================================

if __name__ == "__main__":
    logger.info("========================================")
    logger.info("   绘演万象 (Huiyan) 引擎正在启动...   ")
    logger.info("   Port: 8000 | Env: Production         ")
    logger.info("========================================")

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")