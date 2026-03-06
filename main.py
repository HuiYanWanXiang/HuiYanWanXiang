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
from utils.exceptions import HuiyanError

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

# 运行期错误记录（用于前端展示）
ERROR_LOGS = []
MAX_ERROR_LOGS = 200


def record_error(kind: str, message: str, detail: Optional[str] = None):
    ERROR_LOGS.append({
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "kind": kind,
        "message": message,
        "detail": detail or "",
    })
    if len(ERROR_LOGS) > MAX_ERROR_LOGS:
        del ERROR_LOGS[: len(ERROR_LOGS) - MAX_ERROR_LOGS]


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


def _normalize_html_footer(html: str) -> str:
    """
    统一把生成网页的页脚替换为：@ 绘演万象 版权所有
    兼容：LLM 可能生成的各种 footer 文案（例如“受迫振动交互式演示 | 理论力学与Web可视化 ...”）
    """
    if not html:
        return html

    # 1) 删除已有 footer（粗暴但有效：删掉 <footer ...>...</footer>）
    html = re.sub(r"<footer\b[^>]*>.*?</footer>", "", html, flags=re.IGNORECASE | re.DOTALL)

    # 2) 删除你点名的遗留文案（即使不是 footer，也做兜底清理）
    html = html.replace("受迫振动交互式演示 | 理论力学与Web可视化 | 使用HTML5 Canvas构建", "")
    html = html.replace("受迫振动交互式演示|理论力学与Web可视化|使用HTML5 Canvas构建", "")

    # 3) 注入统一 footer（尽量插到 </body> 前）
    footer_block = """
<footer style="
  margin-top: 18px;
  padding: 14px 10px;
  text-align: center;
  font-size: 12px;
  color: rgba(255,255,255,0.55);
  border-top: 1px solid rgba(255,255,255,0.08);
">
  @ 绘演万象 版权所有
</footer>
""".strip()

    if re.search(r"</body\s*>", html, flags=re.IGNORECASE):
        html = re.sub(r"</body\s*>", footer_block + "\n</body>", html, flags=re.IGNORECASE)
    else:
        html += "\n" + footer_block + "\n"

    return html


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

        # ✅ 强制统一页脚
        clean_html = _normalize_html_footer(clean_html)

        ts = _now_ts()
        safe_prompt = re.sub(r'[\\/*?:"<>|]', "", prompt)[:15]
        filename = f"{ts}_{safe_prompt}.html"
        file_path = os.path.join(SAVE_DIR, filename)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(clean_html)

        # ✅ 内部记录 saved_path（仅供服务端下载接口使用），但不回传前端
        await _set_job(job_id, {
            "status": "done",
            "html": clean_html,
            "saved_path": filename,
            "timestamp": ts,
        })

        logger.info(f"[HTML_JOB:{job_id}] done | saved={file_path}")

    except HuiyanError as e:
        await _set_job(job_id, {"status": "error", "error": str(e)})
        logger.error(f"[HTML_JOB:{job_id}] HuiyanError: {e}")
        record_error("html", str(e), f"job_id={job_id} | prompt={prompt} | model={req.model} | base_url={req.base_url}")

    except Exception as e:
        msg = str(e)
        await _set_job(job_id, {"status": "error", "error": msg})
        logger.error(f"[HTML_JOB:{job_id}] Exception: {msg}")
        record_error("html", msg, f"job_id={job_id} | prompt={prompt} | model={req.model} | base_url={req.base_url}")

    finally:
        try:
            await client.close()
        except Exception:
            pass


# ==============================================================================
# 4. 路由
# ==============================================================================

@app.get("/")
async def login_page():
    """
    登录页：/  -> web_interface/login.html
    """
    login_path = "web_interface/login.html"
    if not os.path.exists(login_path):
        return "System Error: login.html not found."
    return FileResponse(login_path)


@app.get("/app")
async def app_page():
    """
    控制台页：/app -> web_interface/index.html
    """
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
            "saved_path": None,     # 内部字段，不回传前端
            "timestamp": None,      # 可选内部字段
            "html": None,
            "error": None,
        }

    masked_key = _mask_key(request.api_key)
    logger.info(f"[HTML_JOB:{job_id}] queued | model={request.model} | key={masked_key}")

    asyncio.create_task(_html_worker(job_id, request))

    return JSONResponse(content={"status": "queued", "job_id": job_id})


@app.get("/api/html-status/{job_id}")
async def html_status(job_id: str):
    job = await _get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job_id 不存在")

    # ✅ 输出路径清理：前端永远拿不到 saved_path / timestamp
    public_job = dict(job)
    public_job.pop("saved_path", None)
    public_job.pop("timestamp", None)

    # ✅ 给专业下载链接（不暴露服务器路径）
    if job.get("status") == "done":
        public_job["download_url"] = f"/api/html-download/{job_id}"

    return JSONResponse(content=public_job)


@app.get("/api/html-download/{job_id}")
async def html_download(job_id: str):
    job = await _get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job_id 不存在")
    if job.get("status") != "done":
        raise HTTPException(status_code=400, detail="任务未完成，无法下载")

    filename = job.get("saved_path")
    if not filename:
        raise HTTPException(status_code=500, detail="生成文件缺失")

    file_path = os.path.join(SAVE_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")

    # 下载名：更产品化，不泄露内部命名规则
    download_name = "huiyanwanxiang_generated.html"
    return FileResponse(file_path, media_type="text/html", filename=download_name)


@app.get("/api/errors")
async def get_errors():
    return {"items": ERROR_LOGS}


# ==============================================================================
# 5. 入口
# ==============================================================================

if __name__ == "__main__":
    logger.info("========================================")
    logger.info("   绘演万象 (Huiyan) 引擎正在启动...   ")
    logger.info("   Port: 8000 | Env: Production         ")
    logger.info("========================================")

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")