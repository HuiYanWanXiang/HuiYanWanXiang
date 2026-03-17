# 绘演万象

基于大模型的物理 / 数学教学内容生成平台。  
用户输入自然语言教学需求，系统即可生成**交互式教学网页（HTML/JS）**，并可选生成 **Manim 讲解视频**。  
平台支持**本地部署**与**本地知识增强 / 本地知识库扩展**，适用于学校、实验室、教学团队和教育科技场景的私有化落地。

---

## 项目简介

绘演万象面向物理、数学等教学场景，围绕“**自然语言输入 -> 教学内容自动生成**”构建。  
当前版本已经实现两条核心内容生产链路：

- **HTML 教学页生成链路**：自动生成可交互的教学网页
- **Manim 视频生成链路**：自动生成讲解动画视频

同时，系统支持在本地服务器、实验室电脑或校内环境中运行，便于实现**私有化部署、内容本地保存、知识长期沉淀**。

---

## 项目亮点

### 1. 支持本地部署，适合私有化落地
绘演万象可部署在个人电脑、实验室服务器或校内部署环境中。  
前端页面、后端接口、生成结果与视频文件均可保存在本地，适合对数据安全、教学资料保密和系统可控性有要求的使用场景。

### 2. 支持本地知识增强，输出更贴合课程需求
系统当前已支持基于本地提示词与领域知识模块的内容增强。  
可围绕课程讲义、教材内容、题库资料、实验指导等资源构建本地知识目录，在此基础上持续扩展为课程专属知识库体系。

### 3. 双模态输出，兼顾交互与讲解
同一教学主题下，平台既可生成交互式教学网页，也可生成 Manim 动画视频，适用于：

- 课堂演示
- 微课制作
- 课件辅助
- 自主学习
- 科普传播
- 教学资源建设

### 4. 架构清晰，便于二次开发和产品化扩展
系统采用前后端分离的 Web 架构，后端基于 FastAPI，前端通过网页控制台发起内容生成请求。  
整体结构清晰，便于后续扩展用户系统、权限控制、数据库、知识检索、私有模型接入等能力。

---

## 功能概览

- Web 控制台：输入教学需求，实时预览生成网页
- HTML 生成接口：`POST /api/generate-html`
- Manim 视频生成接口：`POST /api/generate-video`
- 视频状态查询：`GET /api/video-status/{job_id}`
- 视频访问：`GET /video/runs/<job_id>/.../*.mp4`
- 本地部署：支持单机、实验室服务器、局域网环境运行
- 本地知识增强：支持本地提示词与领域知识注入
- 本地结果保存：生成内容自动保存到本地目录

---

## 典型应用场景

- 学校或学院部署教学内容生成平台
- 教师团队搭建课程专属知识增强系统
- 根据教材章节快速生成交互式网页
- 自动制作物理 / 数学教学视频
- 面向竞赛、科普和课程建设批量生成教学素材
- 在校内 / 内网环境中进行私有化运行，避免资料外流

---

## 系统架构

本项目围绕“**自然语言 -> 教学网页 / 教学视频**”构建两条主链路，并逐步向“**本地部署 + 本地知识沉淀**”方向扩展。

### 1. HTML 教学页生成链路

1. 前端页面收集用户输入的教学需求。
2. 前端向后端 `POST /api/generate-html` 发起请求。
3. 后端读取系统提示词与领域知识增强模块。
4. 后端调用兼容 OpenAI 协议的大模型服务生成完整 HTML 页面。
5. 对生成结果进行清洗与补全。
6. 将结果保存到本地目录。
7. 前端实时预览生成结果。

### 2. Manim 视频生成链路

1. 前端向 `POST /api/generate-video` 提交任务。
2. 后端创建渲染任务并记录状态。
3. 通过 Manim 渲染引擎生成讲解动画。
4. 渲染完成后返回视频访问路径。
5. 前端轮询任务状态并加载视频。

### 3. 本地知识增强链路

当前版本采用“**本地提示词 + 领域知识模块增强**”的方式，提升特定教学主题下的输出质量。  
围绕本地课程资源，后续可继续扩展为“**本地知识库 + 检索增强生成**”的完整体系。

---

## 当前仓库结构

```text
.
├── main.py                    # FastAPI 服务入口
├── manim_engine/              # Manim 视频生成与任务路由
├── prompts/                   # 系统提示词与领域知识增强模块
├── static/                    # 前端静态资源（CSS / JS / 图片等）
├── tests/                     # 测试目录
├── utils/                     # 日志与异常工具
├── web_interface/             # 前端页面
├── saved_projects/            # 生成结果保存目录（运行时自动创建）
├── requirements.txt           # Python 依赖
└── README.md
```

---

## 技术栈

### 后端
- FastAPI
- Uvicorn
- Pydantic
- OpenAI Compatible API
- SQLAlchemy（可用于后续数据库扩展）
- python-jose（可用于后续鉴权扩展）
- passlib[bcrypt]（可用于后续用户密码管理）
- python-dotenv（可用于后续环境变量配置）

### 前端
- HTML
- CSS
- JavaScript

### 内容生成
- 大模型生成 HTML 教学页
- Manim 生成教学动画视频

---

## 本地部署方案

绘演万象支持在以下环境中进行本地部署：

- 教师个人电脑
- 实验室工作站
- 校内服务器
- 教学团队局域网环境
- 私有云或校内部署节点

### 本地部署优势

- 教学资料无需上传到第三方平台
- 内容生成过程可控，便于长期维护
- 生成结果本地保存，便于归档与复用
- 支持逐步建设课程专属知识体系
- 适合教学团队、实验室和学校级平台落地

---

## 环境要求

### 推荐操作系统
- Ubuntu 22.04 / 24.04
- Windows 10 / 11
- macOS

### 推荐 Python 版本
- Python 3.10
- Python 3.11

---

## Python 依赖

当前部署所需核心依赖如下：

```txt
fastapi
uvicorn
openai
pydantic
manim
sqlalchemy
python-jose
passlib[bcrypt]
python-dotenv
```

---

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/HuiYanWanXiang/HuiYanWanXiang.git
cd HuiYanWanXiang
```

### 2. 创建虚拟环境

#### Linux / macOS
```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### Windows
```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. 安装依赖

若已维护 `requirements.txt`：

```bash
pip install -U pip
pip install -r requirements.txt
```

若需要手动安装：

```bash
pip install fastapi uvicorn openai pydantic manim sqlalchemy python-jose passlib[bcrypt] python-dotenv
```

---

## 启动方式

### 方式一：直接运行入口文件

```bash
python main.py
```

### 方式二：使用 Uvicorn 启动

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## 启动后访问方式

- 本机访问：`http://127.0.0.1:8000/`
- 局域网访问：`http://<本机IP>:8000/`

若部署在实验室服务器或内网环境中，可由同一网络下其他设备通过局域网 IP 访问。

---

## 视频功能依赖（Manim）

若只使用 HTML 教学页生成功能，可先完成基础部署。  
若需要启用视频生成能力，则建议额外安装 Manim 相关系统依赖。

### Ubuntu 推荐安装

```bash
sudo apt update
sudo apt install -y ffmpeg libcairo2-dev pkg-config pango1.0-tools libpango1.0-dev
```

若需要渲染数学公式（如 `MathTex`），建议补充安装：

```bash
sudo apt install -y texlive texlive-latex-extra texlive-fonts-recommended
```

---

## 本地知识增强 / 本地知识库搭建方案

为了让生成结果更贴合课程内容、学校需求与教师风格，建议围绕课程资源逐步搭建本地知识目录。

### 1. 推荐新增本地知识目录

可在项目根目录下建立：

```text
knowledge_base/
├── physics/
├── math/
├── lesson_plans/
├── question_bank/
├── experiments/
└── school_courses/
```

### 2. 建议放入的资料类型

- 教材章节摘要
- 教师讲义
- 课程 PPT 文本整理
- 题库与习题解析
- 实验指导资料
- 课程标准
- 校本课程资源
- 科普内容素材

### 3. 推荐组织方式

按“学科 / 课程 / 专题 / 章节”分类管理，例如：

```text
knowledge_base/
├── physics/
│   ├── mechanics/
│   ├── oscillation/
│   └── electromagnetism/
├── math/
│   ├── calculus/
│   ├── linear_algebra/
│   └── differential_equations/
├── question_bank/
│   ├── high_school_physics/
│   └── college_math/
└── lesson_plans/
    ├── forced_oscillation/
    └── derivative_application/
```

### 4. 当前版本已实现的能力

当前版本已经支持：

- 本地系统提示词加载
- 领域知识增强模块加载
- 基于主题关键词触发知识增强

这意味着系统已经具备“**本地知识增强**”能力，可围绕具体课程持续沉淀与优化内容生成效果。

### 5. 当前版本的真实定位

当前版本更准确地说是：

> **基于本地 Prompt 与领域知识模块的知识增强系统**

后续可进一步扩展为：

- 本地文档解析
- 文本切分
- 向量索引
- 相似内容召回
- 检索增强生成（RAG）

### 6. 本地知识库的价值

本地知识沉淀可以帮助平台从“通用生成工具”升级为“课程专属生成平台”：

- 更贴合学校课程体系
- 更贴合教师教学语言
- 更贴合教材内容与题库风格
- 更适合长期教学资源建设
- 更利于形成学校 / 团队自己的数据资产

---

## 模型接入方式

当前版本支持接入兼容 OpenAI 协议的大模型服务。  
在实际使用时，可根据需要配置：

- API Key
- Base URL
- Model Name

这意味着系统既可连接公有云模型，也可连接校内私有模型服务或自建 OpenAI-compatible 网关。

---

## 推荐的产品化部署方向

在当前本地部署基础上，后续可继续扩展以下能力：

- 统一后端存放模型配置
- 前端不直接暴露 API Key
- 使用 `.env` 管理部署参数
- 接入数据库管理用户与任务记录
- 增加登录、鉴权、权限控制
- 增加本地知识库检索与管理后台
- 支持多课程、多学科资源管理

---

## 建议的环境变量配置（后续可扩展）

可新增 `.env.example`：

```env
APP_HOST=0.0.0.0
APP_PORT=8000

DEFAULT_BASE_URL=
DEFAULT_MODEL=
DEFAULT_API_KEY=

DATABASE_URL=sqlite:///./huiyan.db
JWT_SECRET_KEY=change_me

SAVE_DIR=saved_projects
KNOWLEDGE_BASE_DIR=knowledge_base
```

说明：  
当前版本主要通过请求参数传入模型配置；使用 `.env` 统一管理配置是后续更适合产品化部署的推荐方案。

---

## 接口说明

### 1. HTML 生成接口
- 路径：`POST /api/generate-html`
- 功能：根据用户输入的教学需求生成交互式 HTML 页面

### 2. 视频生成接口
- 路径：`POST /api/generate-video`
- 功能：生成 Manim 教学视频任务

### 3. 视频状态查询接口
- 路径：`GET /api/video-status/{job_id}`
- 功能：查询视频生成状态

### 4. 视频访问路径
- 路径：`GET /video/runs/<job_id>/.../*.mp4`
- 功能：访问渲染完成的视频文件

---

## 测试

```bash
python -m unittest tests/test_core.py
```

---

## 安全与稳定性说明

系统当前通过以下方式提升生成质量与稳定性：

- 使用系统提示词约束输出格式
- 对 HTML 内容进行基本清洗与补全
- 使用本地知识增强模块提高领域适配性
- 使用 Manim 渲染链路输出可复用教学视频
- 生成结果保存在本地目录，便于回溯与管理

---

## 产品化价值总结

绘演万象不仅是一个“大模型生成网页 / 视频”的工具，更是一个可本地落地、可长期沉淀、可逐步扩展为教学平台的内容生成系统。

其核心价值体现在：

- **可本地部署**：适合学校、实验室、教学团队私有化运行
- **可本地知识增强**：适合围绕课程和教材持续优化输出
- **可双模态输出**：同时满足交互式教学与视频讲解需求
- **可持续扩展**：具备向用户系统、知识库系统、校级平台演进的潜力

---

## 适用对象

- 学校与学院教学团队
- 实验教学中心
- 教育科技项目团队
- 科普内容制作团队
- 需要私有化部署的教学生成平台建设者

---

## License

本项目当前主要用于教学研究、课程建设、竞赛展示与技术验证。  
如需面向学校合作、实验室部署或进一步产品化落地，可在当前架构基础上继续扩展。