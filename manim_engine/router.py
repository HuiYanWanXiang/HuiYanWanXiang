import os
import sys
import uuid
import threading
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db, SessionLocal
from models import User
from auth import get_current_user

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
RENDER_PY = BASE_DIR / "render.py"
RUNS_DIR = (BASE_DIR.parent / "runs_video")
RUNS_DIR.mkdir(parents=True, exist_ok=True)

VIDEO_API_KEY = os.getenv("VIDEO_API_KEY", "").strip()
VIDEO_BASE_URL = os.getenv("VIDEO_BASE_URL", "https://api.apishop.qzz.io/v1").strip()
VIDEO_MODEL = os.getenv("VIDEO_MODEL", "gpt-5.4").strip()

router = APIRouter(prefix="/api", tags=["manim"])


# --------------- models ---------------
class VideoRequest(BaseModel):
    prompt: str
    duration: float = 12.0
    quality: str = "m"             # l/m/h/k
    fps: int = 30
    resolution: str = "1920,1080"  # width,height


# --------------- in-memory jobs ---------------
jobs_lock = threading.Lock()
jobs: Dict[str, Dict[str, Any]] = {}

VIDEO_ERROR_LOGS = []
MAX_VIDEO_ERROR_LOGS = 200


def _mask_api_key(api_key: str) -> str:
    if not api_key:
        return "<empty>"
    api_key = api_key.strip()
    if len(api_key) <= 12:
        return api_key[:4] + "***"
    return f"{api_key[:8]}...{api_key[-4:]}"


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


def _check_user_quota(user: User):
    if user.is_root:
        return
    if user.used_count >= user.free_quota:
        raise HTTPException(status_code=403, detail="免费次数已用完")


def _increase_user_quota(username: str):
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
        print(f"[VIDEO_QUOTA] failed to increase quota for {username}: {e}")
    finally:
        db.close()


def _run_job(job_id: str, username: str, payload: VideoRequest) -> None:
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
    env["OPENAI_API_KEY"] = VIDEO_API_KEY
    env["OPENAI_BASE_URL"] = VIDEO_BASE_URL
    env["OPENAI_MODEL"] = VIDEO_MODEL

    with jobs_lock:
        jobs[job_id]["status"] = "running"
        jobs[job_id]["cmd"] = " ".join(cmd)

    print(
        f"[VIDEO_JOB:{job_id}] llm_config | base_url={VIDEO_BASE_URL} | model={VIDEO_MODEL} | api_key={_mask_api_key(VIDEO_API_KEY)}"
    )

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

            # 成功后扣次数
            _increase_user_quota(username)

        else:
            jobs[job_id]["status"] = "error"
            jobs[job_id]["video_url"] = None
            record_video_error(
                message=(
                    f"render failed (returncode={proc.returncode})"
                    if proc.returncode != 0
                    else "render ok but mp4 not found"
                ),
                detail=f"job_id={job_id} | prompt={payload.prompt} | model={VIDEO_MODEL} | base_url={VIDEO_BASE_URL}\n{_tail(stderr, 2000)}"
            )


@router.post("/generate-video")
def generate_video(
    payload: VideoRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    prompt = (payload.prompt or "").strip()
    if not prompt:
        return JSONResponse({"error": "prompt is empty"}, status_code=400)

    if not VIDEO_API_KEY:
        raise HTTPException(status_code=500, detail="服务端未配置 VIDEO_API_KEY")

    _check_user_quota(current_user)

    job_id = uuid.uuid4().hex
    with jobs_lock:
        jobs[job_id] = {
            "status": "queued",
            "prompt": prompt,
            "video_url": None,
            "username": current_user.username,
        }

    t = threading.Thread(target=_run_job, args=(job_id, current_user.username, payload), daemon=True)
    t.start()

    return {"job_id": job_id, "status": "queued"}


@router.get("/video-status/{job_id}")
def video_status(
    job_id: str,
    current_user: User = Depends(get_current_user),
):
    with jobs_lock:
        job = jobs.get(job_id)

    if not job:
        return JSONResponse({"error": "job not found"}, status_code=404)

    if job.get("username") != current_user.username and not current_user.is_root:
        return JSONResponse({"error": "无权查看该任务"}, status_code=403)

    return {
        "job_id": job_id,
        "status": job.get("status"),
        "video_url": job.get("video_url"),
        "stdout_tail": _tail(job.get("stdout", "")),
        "stderr_tail": _tail(job.get("stderr", "")),
        "cmd": job.get("cmd"),
    }


@router.get("/video-errors")
def video_errors(current_user: User = Depends(get_current_user)):
    return {"items": VIDEO_ERROR_LOGS}


def mount_runs(app):
    app.mount("/video/runs", StaticFiles(directory=str(RUNS_DIR)), name="video_runs")
