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

版权所有 (C) 2026 大连理工大学. 保留所有权利.

模块功能描述:
1. 系统入口：初始化 FastAPI 应用服务实例。
2. 路由分发：处理静态资源请求与 API 数据接口。
3. 智能核心：封装与 DeepSeek/OpenAI 兼容的大模型通信逻辑。
4. 数据持久化：实现生成内容的自动命名、归档与本地存储。
5. 异常监控：全局捕获运行时错误并反馈至前端。
================================================================================
"""

import os
import datetime
import re
import logging
from typing import Optional

# 第三方依赖库导入
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from openai import AsyncOpenAI

# 引入项目内部模块
from prompts.loader import load_system_prompt
from prompts.physics_knowledge import get_physics_prompt # 引入刚才写的知识库
from utils.logger import setup_logger
from utils.exceptions import LLMConnectionError

# ==============================================================================
# 1. 系统初始化与配置 (Initialization & Configuration)
# ==============================================================================

# 配置日志记录器
logger = setup_logger()

# 实例化 FastAPI 应用
app = FastAPI(
    title="绘演万象后端引擎",
    description="基于 LLM 的物理仿真网页生成服务",
    version="1.0.0"
)

# 挂载静态资源目录 (CSS, JS, Images)
app.mount("/static", StaticFiles(directory="static"), name="static")

# 定义数据存档目录
SAVE_DIR = "saved_projects"

# 启动时检查目录完整性
if not os.path.exists(SAVE_DIR):
    try:
        os.makedirs(SAVE_DIR)
        logger.info(f"系统初始化: 已创建存档目录 [{SAVE_DIR}]")
    except OSError as e:
        logger.error(f"系统初始化失败: 无法创建目录 {e}")

# ==============================================================================
# 2. 数据模型定义 (Data Models)
# ==============================================================================

class GenRequest(BaseModel):
    """
    生成请求的数据验证模型
    """
    prompt: str          # 用户输入的自然语言指令
    api_key: str         # LLM 服务商提供的 API Key
    base_url: str        # LLM 服务的接口地址
    model: str           # 指定调用的模型名称 (e.g., deepseek-coder)

# ==============================================================================
# 3. 路由处理逻辑 (Route Handlers)
# ==============================================================================

@app.get("/")
async def read_index():
    """
    首页路由
    返回 Web 控制台的主 HTML 文件
    """
    index_path = 'web_interface/index.html'
    if not os.path.exists(index_path):
        return "System Error: index.html not found."
    return FileResponse(index_path)

@app.post("/api/generate-html")
async def generate_html(request: GenRequest):
    """
    核心接口：处理生成请求
    流程：
    1. 接收前端参数 (Prompt, Key, Config)
    2. 加载系统提示词与物理知识库
    3. 构建 LLM 请求上下文
    4. 调用 DeepSeek API 获取代码
    5. 清洗与补全代码
    6. 本地存档
    7. 返回结果
    """
    user_prompt = request.prompt
    
    # 隐私安全处理：日志中隐藏 Key
    masked_key = request.api_key[:6] + "******" if len(request.api_key) > 6 else "***"
    logger.info(f"收到生成指令: '{user_prompt}' | Model: {request.model} | Key: {masked_key}")
    
    # 实例化临时的 OpenAI 客户端
    # 注意：timeout=None 表示不设置超时，允许模型进行长时间思考
    client = AsyncOpenAI(
        api_key=request.api_key, 
        base_url=request.base_url,
        timeout=None 
    )
    
    try:
        # 步骤 1: 加载基础系统提示词
        base_system_prompt = load_system_prompt()
        
        # 步骤 2: 尝试匹配物理知识库 (增强 Prompt)
        # 简单的关键词匹配逻辑，实际可做更复杂的语义分析
        knowledge_augmentation = ""
        if "振动" in user_prompt or "oscillation" in user_prompt.lower():
             knowledge_augmentation = get_physics_prompt("mechanics_damped_oscillation")
        elif "波" in user_prompt or "wave" in user_prompt.lower():
             knowledge_augmentation = get_physics_prompt("wave_double_slit_interference")
        
        # 组合最终的 System Prompt
        final_system_prompt = base_system_prompt
        if knowledge_augmentation:
            final_system_prompt += "\n\n【补充物理领域知识】\n" + knowledge_augmentation
            logger.info("已触发物理知识库增强模式")

        # 步骤 3: 调用 LLM
        logger.info("正在连接 LLM 服务端...")
        response = await client.chat.completions.create(
            model=request.model,
            messages=[
                {"role": "system", "content": final_system_prompt},
                {"role": "user", "content": f"教学主题：{user_prompt}。请生成中文网页。"}
            ],
            temperature=0.7, 
            max_tokens=8192, 
            stream=False
        )

        # 步骤 4: 提取与清洗代码
        raw_content = response.choices[0].message.content
        clean_html = raw_content.replace("```html", "").replace("```", "").strip()
        
        # 简单的代码完整性检查与补全
        if not clean_html.endswith("</html>"):
            logger.warning("检测到代码截断，执行自动补全")
            clean_html += "\n\n</body></html>"

        # 步骤 5: 核心资产归档 (Data Persistence)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        # 清洗文件名中的非法字符
        safe_prompt = re.sub(r'[\\/*?:"<>|]', "", user_prompt)[:15]
        filename = f"{timestamp}_{safe_prompt}.html"
        file_path = os.path.join(SAVE_DIR, filename)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(clean_html)
            
        logger.info(f"生成成功，已归档至: {file_path}")
        
        # 显式关闭连接
        await client.close()
        
        # 返回成功响应
        return JSONResponse(content={
            "status": "success",
            "html": clean_html,
            "saved_path": filename,
            "timestamp": timestamp
        })

    except Exception as e:
        logger.error(f"生成过程中发生严重错误: {str(e)}")
        # 发生错误时，也要确保客户端关闭
        await client.close()
        return JSONResponse(content={"error": str(e), "status": "failed"})

# ==============================================================================
# 4. 程序入口 (Main Entry)
# ==============================================================================

if __name__ == "__main__":
    logger.info("========================================")
    logger.info("   绘演万象 (Huiyan) 引擎正在启动...   ")
    logger.info("   Port: 8000 | Env: Production         ")
    logger.info("========================================")
    
    # 启动 Uvicorn 服务器
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000, 
        log_level="info"
    )