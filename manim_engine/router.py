import os
import sys
import uuid
import threading
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent
RENDER_PY = BASE_DIR / "render.py"
RUNS_DIR = (BASE_DIR.parent / "runs_video")
RUNS_DIR.mkdir(parents=True, exist_ok=True)

router = APIRouter(prefix="/api", tags=["manim"])

# --------------- models ---------------
class VideoRequest(BaseModel):
    prompt: str
    api_key: str
    base_url: str = "https://api.openai.com/v1"  # DeepSeek 用 https://api.deepseek.com
    model: str = "gpt-4o-mini"
    duration: float = 12.0
    quality: str = "m"             # l/m/h/k
    fps: int = 30
    resolution: str = "1920,1080"  # width,height

# --------------- in-memory jobs ---------------
jobs_lock = threading.Lock()
jobs: Dict[str, Dict[str, Any]] = {}

# 运行期视频错误记录（用于前端展示）
VIDEO_ERROR_LOGS = []
MAX_VIDEO_ERROR_LOGS = 200

def record_video_error(message: str, detail: Optional[str] = None):
    VIDEO_ERROR_LOGS.append({
        "time": __import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "message": message,
        "detail": detail or "",
    })
    if len(VIDEO_ERROR_LOGS) > MAX_VIDEO_ERROR_LOGS:
        del VIDEO_ERROR_LOGS[: len(VIDEO_ERROR_LOGS) - MAX_VIDEO_ERROR_LOGS]

def _tail(text: str, n: int = 4000) -> str:
    return (text or "")[-n:]

def _extract_video_path(stdout: str) -> Optional[Path]:
    if not stdout:
        return None
    for line in stdout.splitlines():
        if line.strip().startswith("Video:"):
            p = line.split("Video:", 1)[1].strip()
            if p:
                return Path(p)
    return None

def _find_latest_mp4(root: Path) -> Optional[Path]:
    if not root.exists():
        return None
    mp4s = list(root.rglob("*.mp4"))
    if not mp4s:
        return None
    mp4s.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return mp4s[0]

def _run_job(job_id: str, payload: VideoRequest) -> None:
    outdir = RUNS_DIR / job_id
    outdir.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable, str(RENDER_PY),
        payload.prompt,
        "--duration", str(payload.duration),
        "--quality", str(payload.quality),
        "--resolution", str(payload.resolution),
        "--fps", str(payload.fps),
        "--outdir", str(outdir),
    ]

    env = dict(os.environ)
    env["OPENAI_API_KEY"] = payload.api_key
    env["OPENAI_BASE_URL"] = payload.base_url or env.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    env["OPENAI_MODEL"] = payload.model or env.get("OPENAI_MODEL", "gpt-4o-mini")

    with jobs_lock:
        jobs[job_id]["status"] = "running"
        jobs[job_id]["cmd"] = " ".join(cmd)

    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env=env,
        encoding="utf-8",
        errors="replace",
    )

    stdout = proc.stdout or ""
    stderr = proc.stderr or ""
    video_path = _extract_video_path(stdout)
    if proc.returncode == 0 and (not video_path or not video_path.exists()):
        # 兜底：渲染成功但 stdout 没有 Video: 行时，直接扫描输出目录
        fallback_mp4 = _find_latest_mp4(outdir)
        if fallback_mp4:
            video_path = fallback_mp4

    with jobs_lock:
        jobs[job_id]["returncode"] = proc.returncode
        jobs[job_id]["stdout"] = stdout
        jobs[job_id]["stderr"] = stderr

        if proc.returncode == 0 and video_path and video_path.exists():
            try:
                rel = video_path.relative_to(RUNS_DIR)
                video_url = f"/video/runs/{rel.as_posix()}"
            except Exception:
                video_url = None

            jobs[job_id]["status"] = "done"
            jobs[job_id]["video_url"] = video_url
        else:
            jobs[job_id]["status"] = "error"
            jobs[job_id]["video_url"] = None
            record_video_error(
                message=(
                    f"render failed (returncode={proc.returncode})"
                    if proc.returncode != 0
                    else "render ok but mp4 not found"
                ),
                detail=f"job_id={job_id} | prompt={payload.prompt} | model={payload.model} | base_url={payload.base_url}\n{_tail(stderr, 2000)}"
            )

@router.post("/generate-video")
def generate_video(payload: VideoRequest):
    prompt = (payload.prompt or "").strip()
    if not prompt:
        return JSONResponse({"error": "prompt is empty"}, status_code=400)

    job_id = uuid.uuid4().hex
    with jobs_lock:
        jobs[job_id] = {
            "status": "queued",
            "prompt": prompt,
            "video_url": None,
        }

    t = threading.Thread(target=_run_job, args=(job_id, payload), daemon=True)
    t.start()

    return {"job_id": job_id, "status": "queued"}

@router.get("/video-status/{job_id}")
def video_status(job_id: str):
    with jobs_lock:
        job = jobs.get(job_id)

    if not job:
        return JSONResponse({"error": "job not found"}, status_code=404)

    return {
        "job_id": job_id,
        "status": job.get("status"),
        "video_url": job.get("video_url"),
        "stdout_tail": _tail(job.get("stdout", "")),
        "stderr_tail": _tail(job.get("stderr", "")),
        "cmd": job.get("cmd"),
    }

@router.get("/video-errors")
def video_errors():
    """
    返回最近的视频生成错误日志
    """
    return {"items": VIDEO_ERROR_LOGS}

# --------------- helper to mount runs ---------------
def mount_runs(app):
    # expose generated mp4 under /video/runs/...
    app.mount("/video/runs", StaticFiles(directory=str(RUNS_DIR)), name="video_runs")
