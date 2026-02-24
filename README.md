# 绘演万象
基于大模型的物理/数学教学内容生成平台：输入自然语言指令，生成交互式教学网页（HTML/JS），并可选生成 Manim 讲解视频。

## 功能概览
- Web 控制台：填写 Prompt、选择模型配置、实时预览生成网页
- HTML 生成接口：`POST /api/generate-html`
- Manim 视频生成接口：`POST /api/generate-video`
- 视频状态查询：`GET /api/video-status/{job_id}`
- 视频访问：`GET /video/runs/<job_id>/.../*.mp4`

## 技术原理
本项目围绕“自然语言 -> 教学网页/动画”两条主链路构建，分别是 HTML 教学页生成与 Manim 视频生成。

### 1. HTML 教学页生成链路
1. 前端（`web_interface/index.html` + `static/js/app.js`）收集用户输入的 Prompt、API Key、Base URL、Model。
2. 前端向后端 `POST /api/generate-html` 发起请求。
3. 后端在 `main.py` 中处理请求：
   - 读取系统提示词（`prompts/system_instruction.txt`），强约束输出格式、语言、结构与必备模块。
   - 根据关键词对 Prompt 进行增强（`prompts/physics_knowledge.py`），为常见物理主题注入专业背景、公式和可视化要求。
   - 调用兼容 OpenAI 的 LLM（DeepSeek / Moonshot / Qwen / 其他兼容接口），生成完整 HTML。
   - 对输出进行基础清洗：移除代码块围栏、补齐 `</html>`。
   - 将结果保存到 `saved_projects/`，并返回 HTML 供前端即时预览。
4. 前端将返回的 HTML 放入 iframe（`srcdoc`），做到“所见即所得”实时预览。

### 2. Manim 视频生成链路
1. 前端向 `POST /api/generate-video` 提交任务。
2. `manim_engine/router.py` 接收请求并创建后台线程：
   - 把任务信息记录在内存字典中（状态、日志、输出）。
   - 通过子进程调用 `manim_engine/render.py`，异步生成视频。
3. `render.py` 的核心逻辑：
   - 用系统级强约束提示词让 LLM 只输出一份 ManimCE 代码文件（`GeneratedScene`）。
   - 进行安全/结构检查（禁用除 `from manim import *` 外的 import、禁止 `open/eval/exec` 等）。
   - 进行质量检查（如避免无关坐标系、强制 MathTex 使用 raw string、推导题需多步公式等）。
   - 如校验失败，会把错误原因回传给 LLM 进行重写，最多多次尝试。
   - 生成通过校验的代码后，调用 `manim` 渲染出 mp4。
4. 渲染完成后，`router.py` 解析输出路径并暴露为 `/video/runs/...` 静态资源。
5. 前端通过轮询 `GET /api/video-status/{job_id}` 获取状态，并加载视频到播放器。

### 3. Prompt 体系设计
- `prompts/system_instruction.txt` 负责强约束：
  - 必须输出完整 HTML
  - 必须中文
  - 必须包含知识卡片、Canvas、控制面板、JS 结构（init/loop/bindEvents）
- `prompts/physics_knowledge.py` 负责领域增强：
  - 预置物理/数学专题的公式、参数范围、可视化要求
  - 通过关键词简单匹配触发（如“振动”“波”）

### 4. 安全与鲁棒性
- LLM 生成 HTML 的输出被限定为完整网页结构，减少不可用输出。
- Manim 生成链路包含：
  - 正则黑名单 + AST 解析双重安全检查
  - 质量规则过滤明显不合格输出
  - 渲染失败自动修复并重试

### 5. 为什么是“前端 HTML + 后端 LLM + Manim”
- HTML 教学页解决“交互演示 + 解释文本 + 控件逻辑”问题，面向课堂/学习场景。
- Manim 视频解决“可剪辑、可复用的讲解动画”问题，面向教学视频与课件输出。
- 两条链路共享同一个 Prompt，但输出媒介不同，使得同一个教学主题可同时拥有“交互版 + 视频版”。

## 目录结构
- `main.py`：FastAPI 服务入口，提供页面与 HTML 生成接口
- `manim_engine/`：Manim 视频生成与路由
- `prompts/`：系统提示词与物理知识库
- `web_interface/`：前端页面
- `static/`：前端样式与脚本
- `utils/`：日志与异常
- `tests/`：基础测试

## 快速开始
1) 安装依赖
```bash
pip install -r requirements.txt
```

2) 启动服务（二选一）
```bash
python main.py
```
或
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

3) 访问
- 本机：`http://127.0.0.1:8000/`
- 服务器：`http://<服务器公网IP>:8000/`

## 生成视频（Manim 依赖）
视频生成功能依赖 Manim 和系统库（如 ffmpeg、cairo、pango）。  
Linux 可参考：
```bash
sudo apt-get update
sudo apt-get install -y ffmpeg libcairo2 libpango-1.0-0 libglib2.0-0
```
若使用 `MathTex`，需安装 LaTeX：
```bash
sudo apt-get install -y texlive-latex-extra texlive-fonts-recommended
```

## 基本测试
```bash
python -m unittest tests/test_core.py
```

