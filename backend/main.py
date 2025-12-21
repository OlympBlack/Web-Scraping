import json
import logging
import sys
import asyncio
from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from scraper.brainyquote_scraper import scrape_brainyquote_generator

# Fix for Playwright on Windows
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Autoriser le frontend Nuxt à accéder à l'API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/api/scrape")
async def api_scrape(topic: str = Query(..., description="Sujet à scraper")):
    async def event_generator():
        try:
            async for data in scrape_brainyquote_generator(topic):
                # Using Server-Sent Events (SSE) or just Newline Delimited JSON (NDJSON)
                # NDJSON is easier to parse manually on client in a simple loop
                yield json.dumps(data) + "\n"
        except Exception as e:
            logger.error(f"Stream error: {e}")
            yield json.dumps({"error": f"Stream interrupted: {str(e)}"}) + "\n"

    return StreamingResponse(event_generator(), media_type="application/x-ndjson")

