import asyncio
import os
import httpx
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

API_KEY = os.getenv("VIDEO_API_KEY", "").strip()
BASE_URL = "https://api.apishop.qzz.io/v1"
MODEL = "gpt-5.4"


def mask_api_key(api_key: str) -> str:
    api_key = (api_key or "").strip()
    if not api_key:
        return "<empty>"
    if len(api_key) <= 12:
        return api_key[:4] + "***"
    return f"{api_key[:8]}...{api_key[-4:]}"


async def raw_httpx_check() -> None:
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.post(
            f"{BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": MODEL,
                "messages": [{"role": "user", "content": "你好"}],
            },
        )
        print("raw status:", resp.status_code)
        print("raw headers:", dict(resp.headers))
        print("raw body:", resp.text[:3000])


async def sdk_check() -> None:
    client = AsyncOpenAI(api_key=API_KEY, base_url=BASE_URL, timeout=20, max_retries=0)
    try:
        resp = await client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": "你好"}],
        )
        print("sdk success:", resp.choices[0].message.content)
    finally:
        await client.close()


async def main() -> None:
    print("base_url:", BASE_URL)
    print("model:", MODEL)
    print("api_key:", mask_api_key(API_KEY))

    print("\n=== raw httpx ===")
    try:
        await raw_httpx_check()
    except Exception as e:
        print("raw failed:", repr(e))

    print("\n=== openai sdk ===")
    try:
        await sdk_check()
    except Exception as e:
        print("sdk failed:", repr(e))


if __name__ == "__main__":
    asyncio.run(main())
