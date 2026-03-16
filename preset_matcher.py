from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Optional, Dict, Any, List

BASE_DIR = Path(__file__).resolve().parent
PRESETS_DIR = BASE_DIR / "static" / "presets"


def normalize_text(text: str) -> str:
    if not text:
        return ""
    text = text.strip().lower()
    text = text.replace("（", "(").replace("）", ")")
    text = text.replace("：", ":").replace("，", ",").replace("。", ".")
    # 去掉空白和常见标点，方便匹配
    text = re.sub(r"[\s\-_—,，。.!！?？:：;；/\\]+", "", text)
    return text


def _safe_read_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _static_url_exists(url: Optional[str]) -> bool:
    if not url or not isinstance(url, str):
        return False
    if not url.startswith("/static/"):
        return False
    rel = url[len("/static/"):]
    fs_path = BASE_DIR / "static" / rel
    return fs_path.exists()


def _build_presets_signature() -> str:
    """
    基于目录和 meta 文件的修改时间生成签名，目录发生变更时自动触发缓存失效。
    """
    if not PRESETS_DIR.exists():
        return "missing"

    chunks: List[str] = []
    for subdir in sorted(PRESETS_DIR.iterdir(), key=lambda p: p.name):
        if not subdir.is_dir():
            continue

        meta_path = subdir / "meta.json"
        if meta_path.exists():
            mtime_ns = meta_path.stat().st_mtime_ns
        else:
            mtime_ns = subdir.stat().st_mtime_ns
        chunks.append(f"{subdir.name}:{mtime_ns}")

    return "|".join(chunks)


@lru_cache(maxsize=8)
def _load_presets_by_signature(_signature: str) -> List[Dict[str, Any]]:
    presets: List[Dict[str, Any]] = []

    if not PRESETS_DIR.exists():
        return presets

    for subdir in PRESETS_DIR.iterdir():
        if not subdir.is_dir():
            continue

        meta_path = subdir / "meta.json"
        meta = _safe_read_json(meta_path)
        if not meta:
            continue

        if not meta.get("enabled", True):
            continue

        aliases = meta.get("aliases", [])
        keywords = meta.get("keywords", [])

        meta["_normalized_title"] = normalize_text(meta.get("title", ""))
        meta["_normalized_aliases"] = [normalize_text(x) for x in aliases if x]
        meta["_normalized_keywords"] = [normalize_text(x) for x in keywords if x]

        if not _static_url_exists(meta.get("html_url")):
            continue

        # 资源不存在时返回 None，避免前端加载 404 文件。
        if not _static_url_exists(meta.get("video_url")):
            meta["video_url"] = None
        if not _static_url_exists(meta.get("cover_url")):
            meta["cover_url"] = None

        presets.append(meta)

    return presets


def load_presets() -> List[Dict[str, Any]]:
    signature = _build_presets_signature()
    return _load_presets_by_signature(signature)


def reload_presets() -> None:
    _load_presets_by_signature.cache_clear()


def build_preset_response(meta: Dict[str, Any], match_type: str, score: int) -> Dict[str, Any]:
    return {
        "matched": True,
        "preset_id": meta.get("id"),
        "title": meta.get("title"),
        "description": meta.get("description", ""),
        "html_url": meta.get("html_url"),
        "video_url": meta.get("video_url"),
        "cover_url": meta.get("cover_url"),
        "match_type": match_type,
        "score": score,
    }


def match_preset(prompt: str) -> Dict[str, Any]:
    prompt_norm = normalize_text(prompt)
    if not prompt_norm:
        return {"matched": False}

    presets = load_presets()

    best_match: Optional[Dict[str, Any]] = None
    best_score = -1

    for meta in presets:
        title_norm = meta.get("_normalized_title", "")
        aliases = meta.get("_normalized_aliases", [])
        keywords = meta.get("_normalized_keywords", [])

        # 1) 标题精确匹配
        if title_norm and prompt_norm == title_norm:
            return build_preset_response(meta, match_type="title_exact", score=100)

        # 2) 别名精确匹配
        for alias in aliases:
            if alias and prompt_norm == alias:
                return build_preset_response(meta, match_type="alias_exact", score=100)

        # 3) 标题/别名被包含
        if title_norm and title_norm in prompt_norm:
            score = 90
            if score > best_score:
                best_score = score
                best_match = build_preset_response(meta, match_type="title_contains", score=score)

        for alias in aliases:
            if alias and alias in prompt_norm:
                score = 88
                if score > best_score:
                    best_score = score
                    best_match = build_preset_response(meta, match_type="alias_contains", score=score)

        # 4) 关键词命中
        hit_keywords = [kw for kw in keywords if kw and kw in prompt_norm]
        if len(hit_keywords) >= 2:
            score = 70 + min(len(hit_keywords), 5)
            if score > best_score:
                best_score = score
                best_match = build_preset_response(meta, match_type="keyword", score=score)

    if best_match:
        return best_match

    return {"matched": False}