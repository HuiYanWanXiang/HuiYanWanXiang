# 绘演万象：HTML + Manim 合并说明（已内置）

本项目已在 `HuiYanWanXiang` 基础上合并 Manim 渲染服务：

- HTML 生成接口：`POST /api/generate-html`
- 视频生成接口：`POST /api/generate-video`
- 视频任务查询：`GET /api/video-status/{job_id}`
- 视频文件访问：`GET /video/runs/<job_id>/.../*.mp4`

## 最小运行

```bash
pip install -r requirements.txt
python main.py
# 或 uvicorn main:app --host 0.0.0.0 --port 8000
```

## Linux (Ubuntu) 需要的系统依赖

Manim 依赖 ffmpeg/cairo/pango 等：

```bash
sudo apt-get update
sudo apt-get install -y ffmpeg libcairo2 libpango-1.0-0 libglib2.0-0
```

如你的视频里大量使用 `MathTex`，可能需要 LaTeX（否则会报错）：

```bash
sudo apt-get install -y texlive-latex-extra texlive-fonts-recommended
```

## 前端怎么调用

1) 调 `/api/generate-video` 提交任务，拿到 `job_id`
2) 轮询 `/api/video-status/{job_id}`，直到 `status == done`
3) 用返回的 `video_url` 在网页里 `<video src="..." controls>` 播放
