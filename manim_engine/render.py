import argparse
import ast
import os
import re
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional

from openai import OpenAI

# ============================================================
# 0) 配置：从环境变量读取（由 router.py 注入）
# ============================================================
MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
BASE_URL = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")

# ============================================================
# 1) 系统指令：强约束 LLM 生成 manim==0.19.x 可运行代码
# ============================================================
SYSTEM_INSTRUCTIONS = """You write MANIM Community Edition (manimce) Python code targeting manim==0.19.x.

Return ONLY a single Python file as plain text (no Markdown fences).

Hard rules:
- Must start with: from manim import *
- Must define exactly: class GeneratedScene(Scene): and a construct(self) method
- Do not import anything else (no os/sys/subprocess/pathlib/requests/etc.).
- No file/network access. No reading/writing files. No open(), eval(), exec().
- Keep it short and robust. Avoid rare plugins.

Manim API constraints (IMPORTANT):
- For plotting functions, ALWAYS use Axes.plot(func, x_range=[a, b, step?]) or NumberPlane.plot.
- DO NOT use Axes.get_graph(..., x_range=...). (That breaks on manim 0.19.x.)
- Prefer standard objects: Text/MathTex, Axes, Dot, Line, ValueTracker, always_redraw.

VERY IMPORTANT (Tex strings):
- All Tex/MathTex strings MUST be raw strings: MathTex(r"...") / Tex(r"...").
  This avoids Python escapes like \\t turning into a TAB (which causes 'extmass' etc).

Chinese text rendering rules (CRITICAL):
- For Chinese on-screen labels/titles, DO NOT use Text(...).
- Use Tex(r"中文...") / MathTex(r"...") instead, so xelatex+ctex can render reliably.
- Text(...) may be used only for non-Chinese strings.

Goal: produce a clean educational animation matching the user's request.

Language rules (STRICT):
- All human-readable on-screen narration/labels/titles must be Simplified Chinese.
- Keep Python identifiers/API/class names in English.
- Prefer Chinese text in Tex/MathTex raw strings, e.g. Tex(r"速度").
- If Chinese is used in Text(...), set a CJK-safe font explicitly to avoid missing glyph issues.
"""

# ============================================================
# 1.5) 扩写提示词（先扩写，再写代码）
# ============================================================
EXPAND_INSTRUCTIONS = """You are a prompt expander for Manim educational animations.

Task:
- Expand the user's request into a clear, structured, detailed animation plan.
- Include: concept breakdown, scene steps, key objects, equations, timing notes.
- Keep it concise and actionable for a code generator.
- Add strict layout constraints to keep all objects inside frame, avoid overlaps, and prevent drifting text/equations.
- Write all narration/content in Simplified Chinese.

Output rules:
- Output plain text only.
- Do NOT output code.
- Do NOT use markdown fences.
"""

# ============================================================
# 2) 安全检查：双保险（regex + AST）
# ============================================================
BANNED_PATTERNS = [
    r"\bimport\s+os\b", r"\bimport\s+sys\b", r"\bimport\s+subprocess\b",
    r"\bimport\s+pathlib\b", r"\bimport\s+shutil\b", r"\bimport\s+socket\b",
    r"\bimport\s+requests\b", r"\burllib\b",
    r"\bopen\(", r"\beval\(", r"\bexec\(",
]

CJK_SAFE_FONT = "Noto Sans CJK SC"

def strip_code_fences(text: str) -> str:
    """去掉 LLM 可能返回的 ``` ``` 围栏"""
    text = (text or "").strip()
    text = re.sub(r"^\s*```(?:python)?\s*\n", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\n\s*```\s*$", "", text)
    return text.strip()

def ast_safety_check(code: str) -> None:
    """
    只允许：from manim import *
    禁止任何其它 import / from xxx import y
    """
    tree = ast.parse(code)
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            if isinstance(node, ast.ImportFrom):
                if node.module != "manim":
                    raise ValueError("Forbidden import detected (only `from manim import *` allowed).")
                # 必须是 star import
                if not (len(node.names) == 1 and node.names[0].name == "*" and node.level == 0):
                    raise ValueError("Must use exactly `from manim import *`.")
            else:
                raise ValueError("Forbidden `import ...` detected. Only `from manim import *` is allowed.")

def basic_safety_check(code: str) -> None:
    """结构检查 + 黑名单检查 + AST 检查"""
    if not code.lstrip().startswith("from manim import *"):
        raise ValueError("Generated code must start with `from manim import *`.")
    if "class GeneratedScene(Scene)" not in code:
        raise ValueError("Generated code must contain `class GeneratedScene(Scene)`.")
    for pat in BANNED_PATTERNS:
        if re.search(pat, code):
            raise ValueError(f"Generated code matched a banned pattern: {pat}")
    ast_safety_check(code)

# ============================================================
# 3) 兼容补丁：修你遇到过的 manim API 差异
# ============================================================
def patch_common_manim_api_issues(code: str) -> str:
    """
    典型崩溃点：Axes.get_graph(..., x_range=...) 在 0.19.x 不兼容
    → 替换为 .plot(
    """
    code = re.sub(r"\.get_graph\s*\(", ".plot(", code)
    # 对残留的中文 Text 自动补齐 CJK 字体，避免缺字乱码。
    code = _ensure_cjk_font_for_chinese_text(code)
    # 中文 Text 容易依赖系统字体导致乱码：优先转为 Tex
    code = _convert_chinese_text_to_tex(code)
    # 处理中文 MathTex 在 pdfLaTeX 下报错：优先将纯中文 MathTex 改为 Tex
    code = _downgrade_chinese_mathtex(code)
    # 若出现中文 Tex/MathTex，则注入 xelatex + ctex 支持
    code = _inject_xelatex_ctex(code)
    return code

def _has_chinese(text: str) -> bool:
    if not text:
        return False
    if re.search(r"[\u4e00-\u9fff]", text):
        return True
    # 识别 unicode 转义形式，例如 "\u5149\u6e90"
    return bool(re.search(r"\\u[0-9a-fA-F]{4}", text))


def _convert_chinese_text_to_tex(code: str) -> str:
    """
    将 Text("中文...") 转换为 Tex(r"中文...")，避免 Pango 字体链导致乱码。
    保留 color/font_size 等常见参数，移除 Tex 不支持的 font 参数。
    """
    def _replace_call(match: re.Match) -> str:
        quote = match.group(1)
        content = match.group(2)
        tail = match.group(3) or ""

        if not _has_chinese(content):
            return match.group(0)

        # 移除 Text 专属 font 参数，避免传给 Tex 报错
        tail = re.sub(r",?\s*font\s*=\s*(['\"]).*?\1", "", tail)
        tail = re.sub(r"^\s*,\s*", ", ", tail)

        escaped = content.replace('"', '\\"')
        return f'Tex(r"{escaped}"{tail})'

    # 匹配形如 Text("...", ...)
    pattern = r"\bText\(\s*([\"'])(.*?)\1\s*(,\s*[^\)]*)?\)"
    return re.sub(pattern, _replace_call, code, flags=re.DOTALL)

def _ensure_cjk_font_for_chinese_text(code: str) -> str:
    """
    为 Text("中文...") 自动补充 CJK 字体，避免系统默认字体缺字。
    """
    def _replace_call(match: re.Match) -> str:
        quote = match.group(1)
        content = match.group(2)
        tail = match.group(3) or ""

        if not _has_chinese(content):
            return match.group(0)

        if re.search(r"\bfont\s*=", tail):
            return match.group(0)

        clean_tail = tail.rstrip()
        if clean_tail:
            return f'Text({quote}{content}{quote}{clean_tail}, font="{CJK_SAFE_FONT}")'
        return f'Text({quote}{content}{quote}, font="{CJK_SAFE_FONT}")'

    pattern = r"\bText\(\s*([\"'])(.*?)\1\s*(,\s*[^\)]*)?\)"
    return re.sub(pattern, _replace_call, code, flags=re.DOTALL)

def _downgrade_chinese_mathtex(code: str) -> str:
    """
    将明显为纯中文标题的 MathTex(...) 替换为 Tex(...)
    避免 math 模式下的中文导致 LaTeX 报错。
    """
    def _repl(m):
        raw = m.group(1)
        if _has_chinese(raw) and (not re.search(r"[0-9=+\-*/^_{}\\\\]", raw)):
            return f'Tex(r"{raw}")'
        return m.group(0)
    return re.sub(r'MathTex\(r"([^"]*)"\)', _repl, code)

def _inject_xelatex_ctex(code: str) -> str:
    """
    当代码中出现中文且使用 Tex/MathTex 时，注入 xelatex + ctex 配置。
    """
    if not _has_chinese(code):
        return code
    if not re.search(r"\b(Tex|MathTex)\s*\(", code):
        return code
    inject = (
        "config.tex_compiler = \"xelatex\"\n"
        "config.tex_template = TexTemplate()\n"
        "config.tex_template.add_to_preamble(r\"\\usepackage{ctex}\")\n"
        f"Text.set_default(font=\"{CJK_SAFE_FONT}\")\n"
    )
    if inject in code:
        return code
    lines = code.splitlines()
    if lines and lines[0].startswith("from manim import *"):
        return "\n".join([lines[0], inject] + lines[1:])
    return code


def _extract_render_text_literals(code: str) -> list[str]:
    """
    提取 Text/Tex/MathTex 的首个字符串参数，供语言一致性检查使用。
    """
    patterns = [
        r"\bText\(\s*r?\"([^\"]*)\"",
        r"\bText\(\s*r?'([^']*)'",
        r"\bTex\(\s*r\"([^\"]*)\"",
        r"\bTex\(\s*r'([^']*)'",
        r"\bMathTex\(\s*r\"([^\"]*)\"",
        r"\bMathTex\(\s*r'([^']*)'",
    ]
    out: list[str] = []
    for pat in patterns:
        out.extend(re.findall(pat, code))
    return out


def language_check(code: str) -> None:
    """
    轻量语言门槛：确保可见文案包含足量中文，避免生成全英文动画文案。
    """
    literals = _extract_render_text_literals(code)
    visible_text = "\n".join(literals)
    zh_count = len(re.findall(r"[\u4e00-\u9fff]", visible_text))
    escaped_zh_count = len(re.findall(r"\\u[0-9a-fA-F]{4}", visible_text))
    if zh_count + escaped_zh_count < 4:
        raise ValueError("Language check failed: on-screen text is not sufficiently Chinese.")

# ============================================================
# 4) 质量门槛（重点）：把“看起来很烂/跑偏”的输出挡掉
# ============================================================
GRAPH_KEYWORDS = [
    "plot", "graph", "curve", "function", "axes", "coordinate", "坐标",
    "函数", "曲线", "图像", "坐标系", "作图", "画图"
]
DERIVE_KEYWORDS = [
    "derive", "derivation", "prove", "deduce", "theorem",
    "推导", "证明", "定理", "公式推导", "推演"
]

def quality_check(code: str, original_request: str) -> None:
    req = (original_request or "").lower()

    wants_graph = any(k.lower() in req for k in [x.lower() for x in GRAPH_KEYWORDS])
    if (not wants_graph) and re.search(r"\b(Axes|NumberPlane|ComplexPlane)\b", code):
        raise ValueError("Quality check failed: used Axes/NumberPlane but request did not ask for graphs/coordinates.")

    # Tex/MathTex 必须 raw string
    if re.search(r"\b(MathTex|Tex)\(\s*(?!r['\"])\s*['\"]", code):
        raise ValueError("Quality check failed: Tex/MathTex must use raw strings: MathTex(r'...') / Tex(r'...').")

    # 中文文案禁止走 Text，避免服务器字体链导致乱码
    if re.search(r"\bText\(\s*(?:r)?[\"'][^\"']*(?:[\u4e00-\u9fff]|\\u[0-9a-fA-F]{4})[^\"']*[\"']", code):
        # 允许中文 Text，但必须显式设置 CJK 安全字体。
        if not re.search(r"\bText\([^\)]*\bfont\s*=\s*[\"'](?:Noto Sans CJK SC|Noto Serif CJK SC|Source Han Sans CN|WenQuanYi Zen Hei|SimHei|Microsoft YaHei)[\"']", code):
            raise ValueError("Quality check failed: Chinese Text(...) must set an explicit CJK-safe font.")

    is_derivation = any(k in req for k in [x.lower() for x in DERIVE_KEYWORDS])
    if is_derivation:
        mathtex_count = len(re.findall(r"\bMathTex\s*\(", code))
        if mathtex_count < 2:
            raise ValueError("Quality check failed: derivation request but too few MathTex steps (need >= 2).")
        if not re.search(r"(\\int|\\frac|=)", code):
            raise ValueError("Quality check failed: derivation request but missing core math tokens (\\int / \\frac / '=').")

    if ("kinetic" in req) or ("动能" in (original_request or "")) or ("work-energy" in req) or ("功" in (original_request or "") and "能" in (original_request or "")):
        if not re.search(r"\bK\b", code):
            raise ValueError("Quality check failed: kinetic/work-energy topic but missing symbol K.")
        if not re.search(r"\\frac\{1\}\{2\}", code):
            raise ValueError("Quality check failed: kinetic/work-energy topic but missing \\frac{1}{2}.")

# ============================================================
# 5) LLM 调用：改为 chat.completions（兼容 DeepSeek 等 OpenAI-compatible）
# ============================================================
def call_llm_raw(client: OpenAI, input_text: str) -> str:
    """
    只负责调用模型拿文本，不做检查
    注意：这里用 chat.completions.create（兼容 /chat/completions）
    """
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_INSTRUCTIONS},
            {"role": "user", "content": input_text},
        ],
        temperature=0.6,
        max_tokens=4096,
        stream=False,
    )
    content = resp.choices[0].message.content if resp.choices else ""
    return strip_code_fences(content or "")

def expand_prompt(client: OpenAI, original_request: str, duration: float) -> str:
    """
    第一次调用 LLM：扩写提示词（不产出代码）。
    """
    user_text = (
        "Expand this user request into a detailed Manim animation plan.\n"
        f"Target duration: about {duration:.1f} seconds.\n"
        "User request:\n"
        f"{original_request}\n"
    )
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": EXPAND_INSTRUCTIONS},
            {"role": "user", "content": user_text},
        ],
        temperature=0.6,
        max_tokens=2048,
        stream=False,
    )
    content = resp.choices[0].message.content if resp.choices else ""
    return strip_code_fences(content or "")

def validate_and_patch(code: str, original_request: str, enable_quality: bool) -> str:
    if not code:
        raise ValueError("LLM returned empty code.")
    code = patch_common_manim_api_issues(code)
    basic_safety_check(code)
    language_check(code)
    if enable_quality:
        quality_check(code, original_request)
    return code

def generate_code_with_retries(
    client: OpenAI,
    original_request: str,
    initial_prompt: str,
    max_attempts: int,
    enable_quality: bool
) -> str:
    prompt = initial_prompt
    last_err = None
    last_code = ""

    for _ in range(max_attempts):
        code = call_llm_raw(client, prompt)
        last_code = code
        try:
            return validate_and_patch(code, original_request, enable_quality)
        except Exception as e:
            last_err = str(e)
            prompt = (
                "Your previous output did NOT pass validation.\n"
                f"Failure reason:\n{last_err}\n\n"
                "Rewrite the COMPLETE Python file from scratch so it passes ALL constraints.\n"
                "Hard rules reminder:\n"
                "- Start with: from manim import *\n"
                "- Define: class GeneratedScene(Scene): with construct(self)\n"
                "- No imports besides manim\n"
                "- All MathTex/Tex must be raw strings: MathTex(r\"...\")\n\n"
                "Original user request:\n"
                f"{original_request}\n\n"
                "Previous (bad) code:\n"
                f"{last_code}\n"
            )

    raise RuntimeError(f"Failed to generate valid code after {max_attempts} attempts. Last error: {last_err}")

# ============================================================
# 6) 渲染：支持分辨率/帧率
# ============================================================
def render_with_manim(py_file: Path, quality: str, media_dir: Path, resolution: str, fps: int) -> subprocess.CompletedProcess:
    qflag = f"-q{quality}"
    cmd = [
        sys.executable, "-m", "manim",
        qflag,
        "--media_dir", str(media_dir),
        "--resolution", resolution,
        "--fps", str(fps),
        str(py_file),
        "GeneratedScene",
    ]
    return subprocess.run(cmd, capture_output=True, text=True)

def find_latest_mp4(media_dir: Path) -> Optional[Path]:
    if not media_dir.exists():
        return None
    mp4s = list(media_dir.rglob("*.mp4"))
    if not mp4s:
        return None
    mp4s.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return mp4s[0]

# ============================================================
# 7) 主流程：生成 -> 渲染 -> 失败自动修复
# ============================================================
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("prompt", help="Natural language request (Chinese/English both ok).")

    parser.add_argument("--quality", default="l", choices=["l", "m", "h", "k"], help="l/m/h/k => -ql/-qm/-qh/-qk")
    parser.add_argument("--resolution", default="1920,1080", help="width,height e.g. 1920,1080 or 1080,1920")
    parser.add_argument("--fps", type=int, default=30, help="Frames per second, e.g. 30")

    parser.add_argument("--duration", type=float, default=12.0, help="Target duration in seconds (soft constraint).")

    parser.add_argument("--outdir", default="runs", help="Output directory (scripts/logs/videos per run).")
    parser.add_argument("--max-fix", type=int, default=2, help="Max render-fix attempts when render fails.")
    parser.add_argument("--max-gen", type=int, default=2, help="Max generation retries before first render (quality/safety).")
    parser.add_argument("--no-quality-check", action="store_true", help="Disable quality checks (not recommended).")

    args = parser.parse_args()

    if not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit("Missing OPENAI_API_KEY.")

    enable_quality = not args.no_quality_check

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = outdir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    (run_dir / "prompt.txt").write_text(args.prompt, encoding="utf-8")

    # ✅ 关键：把 base_url 传给 OpenAI 客户端（兼容 deepseek / moonshot / aliyun 等）
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"], base_url=BASE_URL)

    # 第一次调用：扩写提示词
    expanded_prompt = expand_prompt(client, args.prompt, args.duration)
    if not expanded_prompt.strip():
        expanded_prompt = args.prompt
    (run_dir / "expanded_prompt.txt").write_text(expanded_prompt, encoding="utf-8")

    initial_user_prompt = (
        "Generate a ManimCE educational animation in Simplified Chinese.\n"
        f"Target total duration: about {args.duration:.1f} seconds.\n"
        "Style constraints:\n"
        "- Clear visuals, not cluttered.\n"
        "- Keep everything inside frame.\n"
        "- Enforce stable layout: anchor groups, avoid overlaps, avoid drifting text, keep titles/top labels fixed.\n"
        "- Use aligned positioning (shift/next_to/arrange) and avoid absolute coords that push objects off-screen.\n"
        "- Use MathTex for equations and animate steps cleanly.\n"
        "- IMPORTANT: All Tex/MathTex strings must be RAW strings: MathTex(r\"...\").\n"
        "- IMPORTANT: All on-screen narration/labels/titles must be Simplified Chinese.\n"
        "Expanded request:\n"
        f"{expanded_prompt}\n"
    )

    code = generate_code_with_retries(
        client=client,
        original_request=args.prompt,
        initial_prompt=initial_user_prompt,
        max_attempts=max(1, args.max_gen),
        enable_quality=enable_quality
    )

    py_file = run_dir / "generated_scene.py"
    py_file.write_text(code, encoding="utf-8")

    media_dir = run_dir / "media"

    last_proc: Optional[subprocess.CompletedProcess] = None

    for attempt in range(args.max_fix + 1):
        proc = render_with_manim(py_file, args.quality, media_dir, args.resolution, args.fps)
        last_proc = proc

        (run_dir / f"render_stdout_{attempt}.txt").write_text(proc.stdout or "", encoding="utf-8")
        (run_dir / f"render_stderr_{attempt}.txt").write_text(proc.stderr or "", encoding="utf-8")

        if proc.returncode == 0:
            break

        if attempt >= args.max_fix:
            break

        fix_prompt = (
            "The following Manim code failed to render on manimce==0.19.x.\n"
            "Output ONLY the fixed complete Python file.\n"
            "Hard rules:\n"
            "- start with 'from manim import *'\n"
            "- define class GeneratedScene(Scene) with construct(self)\n"
            "- no imports besides manim\n"
            "- all MathTex/Tex must be raw strings: MathTex(r\"...\")\n\n"
            "- all on-screen narration/labels/titles must be Simplified Chinese\n\n"
            "ORIGINAL USER REQUEST:\n"
            f"{args.prompt}\n\n"
            "CURRENT CODE:\n"
            f"{code}\n\n"
            "RENDER ERROR (stderr):\n"
            f"{proc.stderr}\n"
        )

        code = generate_code_with_retries(
            client=client,
            original_request=args.prompt,
            initial_prompt=fix_prompt,
            max_attempts=max(1, args.max_gen),
            enable_quality=enable_quality
        )
        py_file.write_text(code, encoding="utf-8")

    mp4 = find_latest_mp4(media_dir)
    if last_proc and last_proc.returncode == 0:
        print("[OKKK] Render success")
        print(f"BaseURL: {BASE_URL}")
        print(f"Model: {MODEL}")
        print(f"Resolution: {args.resolution}  FPS: {args.fps}  Quality: -q{args.quality}")
        print(f"Code:  {py_file.resolve()}")
        if mp4:
            print(f"Video: {mp4.resolve()}")
        else:
            print("Rendered but no mp4 found under run media dir (check run_dir/media).")
    else:
        print("[ERROR] Render failed (logs saved under runs/...)")
        print(f"BaseURL: {BASE_URL}")
        print(f"Model: {MODEL}")
        print(f"Code:  {py_file.resolve()}")
        if last_proc:
            print(f"Last returncode={last_proc.returncode}")
            print((last_proc.stderr or "")[:2000])

if __name__ == "__main__":
    main()
