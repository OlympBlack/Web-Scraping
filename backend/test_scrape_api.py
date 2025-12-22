import asyncio
import httpx
import json

async def test_scrape():
    async with httpx.AsyncClient(timeout=300.0) as client:
        print("Starting scrape request...")
        async with client.stream("GET", "http://127.0.0.1:8000/api/scrape?topic=nature") as response:
            async for line in response.aiter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        if "image_url" in data and "brainyquote" not in data.get("image_url", ""):
                             print(f"FOUND PROCESSED IMAGE: {data['image_url']}")
                        elif "total" in data:
                             print(f"Progress: {data.get('progress')}/{data.get('total')}")
                    except:
                        pass
        print("Scrape finished.")

if __name__ == "__main__":
    asyncio.run(test_scrape())
