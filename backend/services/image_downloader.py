import httpx
import logging

logger = logging.getLogger(__name__)

async def download_image(url: str) -> tuple[bytes, str] | None:
    """
    Downloads an image from a URL.
    Returns (content, content_type) or None if failed.
    """
    if not url:
        return None
        
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)
            if response.status_code == 200:
                content_type = response.headers.get("content-type", "application/octet-stream")
                return response.content, content_type
            else:
                logger.warning(f"Failed to download image {url}: status {response.status_code}")
                return None
    except Exception as e:
        logger.error(f"Error downloading image {url}: {e}")
        return None
