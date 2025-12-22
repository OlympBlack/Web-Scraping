import json
import logging
import sys
import asyncio
from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from scraper.brainyquote_scraper import scrape_brainyquote_generator
from services.supabase_client import save_quote, upload_image
from services.image_downloader import download_image
import uuid

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
                # Save to Supabase if it's a quote item (has text and author)
                if "text" in data and "author" in data:
                    # Enrich with topic
                    data["topic"] = topic
                    
                    # Handle Image Logic
                    original_image_url = data.get("image_url")
                    if original_image_url:
                        try:
                            logger.info(f"Downloading image from {original_image_url}...")
                            download_result = await download_image(original_image_url)
                            
                            if download_result:
                                image_content, mime_type = download_result
                                # Create a unique filename
                                suffix = "jpg"
                                if "png" in mime_type:
                                    suffix = "png"
                                elif "webp" in mime_type:
                                    suffix = "webp"
                                    
                                filename = f"{topic}/{uuid.uuid4()}.{suffix}"
                                logger.info(f"Uploading image to {filename} (Type: {mime_type})...")
                                public_url = upload_image(image_content, filename, content_type=mime_type)
                                
                                if public_url:
                                    logger.info(f"Image uploaded successfully: {public_url}")
                                    data["image_url"] = public_url
                                else:
                                    logger.warning("Failed to upload image, keeping original URL (or None)")
                            else:
                                logger.warning("Failed to download image content")
                        except Exception as img_err:
                            logger.error(f"Error processing image: {img_err}")

                    save_quote(data)
                
                # Using Server-Sent Events (SSE) or just Newline Delimited JSON (NDJSON)
                # NDJSON is easier to parse manually on client in a simple loop
                yield json.dumps(data) + "\n"
        except Exception as e:
            logger.error(f"Stream error: {e}")
            yield json.dumps({"error": f"Stream interrupted: {str(e)}"}) + "\n"

    return StreamingResponse(event_generator(), media_type="application/x-ndjson")

