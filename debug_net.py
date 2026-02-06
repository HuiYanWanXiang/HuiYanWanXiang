import asyncio
from openai import AsyncOpenAI

# ==========================================
# ⚠️ 请务必在这里填入您的真实 Key
# ==========================================
API_KEY = "sk-b1bf4e421bde436bab19ea49407cbd05" 
BASE_URL = "https://api.deepseek.com"

async def test_connection():
    print(f"1. 正在尝试连接: {BASE_URL}")
    client = AsyncOpenAI(api_key=API_KEY, base_url=BASE_URL, timeout=10)
    
    try:
        response = await client.chat.completions.create(
            model="deepseek-coder",
            messages=[{"role": "user", "content": "你好"}],
        )
        print("✅ 连接成功！DeepSeek 回复：")
        print(response.choices[0].message.content)
    except Exception as e:
        print("\n❌ 连接失败！原因如下：")
        print(e)
        print("\n建议：")
        print("1. 检查 API_KEY 是否填写正确。")
        print("2. 关闭电脑上的 VPN/代理软件。")
        print("3. 检查是否连接了互联网。")

if __name__ == "__main__":
    asyncio.run(test_connection())