from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from openai import AsyncOpenAI  # 注意：这里我们只导入类，不再实例化全局变量
import uvicorn
import os
import datetime
import re

from prompts.loader import load_system_prompt
from utils.logger import setup_logger

logger = setup_logger()
app = FastAPI()

# 挂载静态资源
app.mount("/static", StaticFiles(directory="static"), name="static")

# 确保存档目录存在
SAVE_DIR = "saved_projects"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

# =========================================================
# 📦 更新请求模型
# 现在前端发来的不仅仅是 prompt，还有配置信息
# =========================================================
class GenRequest(BaseModel):
    prompt: str
    api_key: str      # 必填
    base_url: str     # 必填
    model: str        # 必填

@app.get("/")
async def read_index():
    return FileResponse('web_interface/index.html')

@app.post("/api/generate-html")
async def generate_html(request: GenRequest):
    user_prompt = request.prompt
    
    # 日志里不要打印 key，只打印前几位，为了安全
    masked_key = request.api_key[:8] + "***"
    logger.info(f"收到指令: {user_prompt} | Provider: {request.base_url} | Key: {masked_key}")
    
    try:
        # =================================================
        # 🔑 动态实例化客户端 (Dynamic Client)
        # =================================================
        # 这里使用用户传来的 api_key 和 base_url
        temp_client = AsyncOpenAI(
            api_key=request.api_key, 
            base_url=request.base_url,
            timeout=None # 依然保持无超时限制
        )
        
        # 加载提示词
        system_prompt = load_system_prompt()
        
        # 调用 LLM
        response = await temp_client.chat.completions.create(
            model=request.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"教学主题：{user_prompt}。请生成中文网页。"}
            ],
            temperature=0.7, 
            max_tokens=8192, 
            stream=False
        )

        raw_content = response.choices[0].message.content
        clean_html = raw_content.replace("```html", "").replace("```", "").strip()
        
        if not clean_html.endswith("</html>"):
            clean_html += "\n</body></html>"

        # 存档逻辑
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_prompt = re.sub(r'[\\/*?:"<>|]', "", user_prompt)[:10]
        filename = f"{timestamp}_{safe_prompt}.html"
        file_path = os.path.join(SAVE_DIR, filename)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(clean_html)
            
        logger.info(f"生成成功: {file_path}")
        
        # 关闭临时连接 (虽然 Python 会自动回收，但显式关闭是个好习惯)
        await temp_client.close()
        
        return JSONResponse(content={"html": clean_html, "saved_path": filename})

    except Exception as e:
        logger.error(f"生成失败: {str(e)}")
        # 将错误信息返回给前端，比如 "Authentication Fails"
        return JSONResponse(content={"error": str(e)})

if __name__ == "__main__":
    logger.info("绘演万象 Pro 版启动...")
    uvicorn.run(app, host="0.0.0.0", port=8000)