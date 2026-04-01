#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
================================================================================
项目名称: 绘演万象:Web端交互式物理仿真实验平台
Project Name: HuiyanWanxiang Web Interactive Physics Simulation Platform
文件名称: main.py
创建日期: 2026-02-06
作者: 大连理工大学数学科学学院绘演万象开发团队
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
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from openai import AsyncOpenAI
from sqlalchemy.orm import Session

from prompts.loader import load_system_prompt
from prompts.physics_knowledge import get_physics_prompt
from utils.logger import setup_logger
from utils.exceptions import HuiyanError

from database import Base, engine, get_db
from models import User
from auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)
from manim_engine.router import router as manim_router, mount_runs
from preset_matcher import match_preset, reload_presets

# ==============================================================================
# 1. 系统初始化与配置
# ==============================================================================

logger = setup_logger()
load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="绘演万象后端引擎",
    description="基于 LLM 的物理仿真网页生成服务",
    version="2.0.0"
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# Manim 渲染结果静态挂载（/video/runs/...）
mount_runs(app)
# Manim API 路由（/api/generate-video, /api/video-status/{job_id}）
app.include_router(manim_router)

SAVE_DIR = "saved_projects"
os.makedirs(SAVE_DIR, exist_ok=True)

VIDEO_API_KEY = os.getenv("VIDEO_API_KEY", "").strip()
VIDEO_BASE_URL = os.getenv("VIDEO_BASE_URL", "https://api.deepseek.com").strip()
VIDEO_MODEL = os.getenv("VIDEO_MODEL", "deepseek-coder").strip()

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

class RegisterRequest(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class GenRequest(BaseModel):
    prompt: str


class PresetMatchRequest(BaseModel):
    prompt: str


# ==============================================================================
# 3. HTML 异步任务管理（内存版）
# ==============================================================================

# job_id -> job_info
# job_info: {
#   status, created_at, prompt, model, saved_path, html, error,
#   username, charged
# }
html_jobs: Dict[str, Dict[str, Any]] = {}
html_jobs_lock = asyncio.Lock()


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
    """
    if not html:
        return html

    html = re.sub(r"<footer\b[^>]*>.*?</footer>", "", html, flags=re.IGNORECASE | re.DOTALL)

    html = html.replace("受迫振动交互式演示 | 理论力学与Web可视化 | 使用HTML5 Canvas构建", "")
    html = html.replace("受迫振动交互式演示|理论力学与Web可视化|使用HTML5 Canvas构建", "")

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


def _check_user_quota(user: User):
    if user.is_root:
        return
    if user.used_count >= user.free_quota:
        raise HTTPException(status_code=403, detail="免费次数已用完")


def _increase_user_quota(username: str):
    """
    HTML 后台异步任务成功后扣次数
    """
    from database import SessionLocal

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return
        if user.is_root:
            return
        user.used_count += 1
        db.commit()
    except Exception as e:
        logger.error(f"[HTML_QUOTA] failed to increase quota for {username}: {e}")
    finally:
        db.close()


async def _html_worker(job_id: str, prompt: str, username: str, api_key: str, base_url: str, model: str) -> None:
    """
    后台执行 HTML 生成，写回 html_jobs[job_id]
    成功后扣次数
    """
    logger.info(f"[HTML_JOB:{job_id}] start | prompt='{prompt}' | model={model} | username={username}")

    await _set_job(job_id, {"status": "running"})

    client = AsyncOpenAI(api_key=api_key, base_url=base_url, timeout=None)

    try:
        final_system_prompt = _build_system_prompt(prompt)
        if "【补充物理领域知识】" in final_system_prompt:
            logger.info(f"[HTML_JOB:{job_id}] knowledge augmentation enabled")

        logger.info(f"[HTML_JOB:{job_id}] calling LLM...")
        resp = await client.chat.completions.create(
            model=model,
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

        clean_html = _normalize_html_footer(clean_html)

        ts = _now_ts()
        safe_prompt = re.sub(r'[\\/*?:"<>|]', "", prompt)[:15]
        filename = f"{ts}_{safe_prompt}.html"
        file_path = os.path.join(SAVE_DIR, filename)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(clean_html)

        # 成功后扣次数
        _increase_user_quota(username)

        await _set_job(job_id, {
            "status": "done",
            "html": clean_html,
            "saved_path": filename,
            "timestamp": ts,
            "charged": True,
        })

        logger.info(f"[HTML_JOB:{job_id}] done | saved={file_path}")

    except HuiyanError as e:
        await _set_job(job_id, {"status": "error", "error": str(e)})
        logger.error(f"[HTML_JOB:{job_id}] HuiyanError: {e}")
        record_error("html", str(e), f"job_id={job_id} | prompt={prompt} | model={model} | base_url={base_url}")

    except Exception as e:
        msg = str(e)
        await _set_job(job_id, {"status": "error", "error": msg})
        logger.error(f"[HTML_JOB:{job_id}] Exception: {msg}")
        record_error("html", msg, f"job_id={job_id} | prompt={prompt} | model={model} | base_url={base_url}")

    finally:
        try:
            await client.close()
        except Exception:
            pass


# ==============================================================================
# 4. 认证路由
# ==============================================================================

@app.post("/api/auth/register")
async def register(data: RegisterRequest, db: Session = Depends(get_db)):
    username = (data.username or "").strip()
    password = (data.password or "").strip()

    if len(username) < 3:
        raise HTTPException(status_code=400, detail="用户名至少 3 位")
    if len(password) < 6:
        raise HTTPException(status_code=400, detail="密码至少 6 位")

    existing = db.query(User).filter(User.username == username).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")

    user = User(
        username=username,
        password_hash=hash_password(password),
        is_root=False,
        is_active=True,
        used_count=0,
        free_quota=3,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": user.username})
    return {
        "access_token": token,
        "token_type": "bearer",
        "username": user.username,
        "is_root": user.is_root,
        "used_count": user.used_count,
        "free_quota": user.free_quota,
    }


@app.post("/api/auth/login")
async def login(data: LoginRequest, db: Session = Depends(get_db)):
    username = (data.username or "").strip()
    password = (data.password or "").strip()

    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=400, detail="用户名或密码错误")

    token = create_access_token({"sub": user.username})
    return {
        "access_token": token,
        "token_type": "bearer",
        "username": user.username,
        "is_root": user.is_root,
        "used_count": user.used_count,
        "free_quota": user.free_quota,
    }


@app.get("/api/auth/me")
async def me(current_user: User = Depends(get_current_user)):
    remaining = -1 if current_user.is_root else max(current_user.free_quota - current_user.used_count, 0)
    return {
        "username": current_user.username,
        "is_root": current_user.is_root,
        "used_count": current_user.used_count,
        "free_quota": current_user.free_quota,
        "remaining_count": remaining,
    }


# ==============================================================================
# 5. 页面路由
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


@app.get("/learning-profile")
async def learning_profile_page():
    """
    学习画像演示页：/learning-profile -> web_interface/learning_profile.html
    """
    page_path = "web_interface/learning_profile.html"
    if not os.path.exists(page_path):
        return "System Error: learning_profile.html not found."
    return FileResponse(page_path)


# ==============================================================================
# 6. 预设匹配路由
# ==============================================================================

@app.post("/api/preset-match")
async def api_preset_match(
    payload: PresetMatchRequest,
    current_user: User = Depends(get_current_user),
):
    prompt = (payload.prompt or "").strip()
    if not prompt:
        return {"matched": False}

    result = match_preset(prompt)
    logger.info(
        f"[PRESET_MATCH] username={current_user.username} | prompt='{prompt}' | matched={result.get('matched', False)}"
    )
    return result


@app.post("/api/preset-reload")
async def api_preset_reload(current_user: User = Depends(get_current_user)):
    if not current_user.is_root:
        raise HTTPException(status_code=403, detail="只有管理员可以刷新预设")
    reload_presets()
    logger.info(f"[PRESET_RELOAD] username={current_user.username}")
    return {"ok": True, "message": "presets reloaded"}


# ==============================================================================
# 7. HTML 生成相关路由
# ==============================================================================

@app.post("/api/generate-html")
async def generate_html(
    request: GenRequest,
    current_user: User = Depends(get_current_user),
):
    """
    异步提交：秒回 job_id，后台生成
    """
    user_prompt = (request.prompt or "").strip()
    if not user_prompt:
        raise HTTPException(status_code=400, detail="Prompt 不能为空")

    if not VIDEO_API_KEY:
        raise HTTPException(status_code=500, detail="服务端未配置 VIDEO_API_KEY")

    _check_user_quota(current_user)

    job_id = uuid.uuid4().hex[:12]
    async with html_jobs_lock:
        html_jobs[job_id] = {
            "status": "queued",
            "created_at": datetime.datetime.now().isoformat(),
            "prompt": user_prompt,
            "model": VIDEO_MODEL,
            "saved_path": None,
            "timestamp": None,
            "html": None,
            "error": None,
            "username": current_user.username,
            "charged": False,
        }

    logger.info(f"[HTML_JOB:{job_id}] queued | model={VIDEO_MODEL} | username={current_user.username}")

    asyncio.create_task(_html_worker(
        job_id=job_id,
        prompt=user_prompt,
        username=current_user.username,
        api_key=VIDEO_API_KEY,
        base_url=VIDEO_BASE_URL,
        model=VIDEO_MODEL,
    ))

    return JSONResponse(content={"status": "queued", "job_id": job_id})


@app.get("/api/html-status/{job_id}")
async def html_status(
    job_id: str,
    current_user: User = Depends(get_current_user),
):
    job = await _get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job_id 不存在")

    # 防止别人查别人的任务
    if job.get("username") != current_user.username and not current_user.is_root:
        raise HTTPException(status_code=403, detail="无权查看该任务")

    public_job = dict(job)
    public_job.pop("saved_path", None)
    public_job.pop("timestamp", None)

    if job.get("status") == "done":
        public_job["download_url"] = f"/api/html-download/{job_id}"

    return JSONResponse(content=public_job)


@app.get("/api/html-download/{job_id}")
async def html_download(
    job_id: str,
    current_user: User = Depends(get_current_user),
):
    job = await _get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job_id 不存在")

    if job.get("username") != current_user.username and not current_user.is_root:
        raise HTTPException(status_code=403, detail="无权下载该任务")

    if job.get("status") != "done":
        raise HTTPException(status_code=400, detail="任务未完成，无法下载")

    filename = job.get("saved_path")
    if not filename:
        raise HTTPException(status_code=500, detail="生成文件缺失")

    file_path = os.path.join(SAVE_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")

    download_name = "huiyanwanxiang_generated.html"
    return FileResponse(file_path, media_type="text/html", filename=download_name)


@app.get("/api/errors")
async def get_errors(current_user: User = Depends(get_current_user)):
    return {"items": ERROR_LOGS}


# ==============================================================================
# 8. 入口
# ==============================================================================

if __name__ == "__main__":
    logger.info("========================================")
    logger.info("   绘演万象 (Huiyan) 引擎正在启动...   ")
    logger.info("   Port: 8000 | Env: Production         ")
    logger.info("========================================")

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")