import logging
import asyncio
from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)

async def scrape_brainyquote_generator(topic: str):
    """
    Scrapes BrainyQuote for a given topic, yielding results asynchronously.
    """
    topic = topic.strip().lower().replace(" ", "-")
    url = f"https://www.brainyquote.com/topics/{topic}-quotes"
    
    logger.info(f"Starting scrape for topic: {topic} at {url}")

    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=True)
        # Use a real user agent to avoid basic bot detection
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        try:
            page = await context.new_page()
            
            # Removed aggressive resource blocking to ensure grid renders correctly
            
            try:
                await page.goto(url, timeout=60000, wait_until="domcontentloaded")
            except Exception as e:
                logger.error(f"Failed to load page: {e}")
                yield {"error": f"Failed to load page: {str(e)}"}
                return

            # Check for "Page Not Found" (invalid topic)
            try:
                title = await page.title()
                h1_text = await page.evaluate("() => document.querySelector('h1') ? document.querySelector('h1').innerText : ''")
                
                if "Page Not Found" in title or "Page Not Found" in h1_text:
                    logger.warning(f"Topic '{topic}' not found.")
                    yield {"error": f"Le sujet '{topic}' n'a pas été trouvé. Essayez un autre terme."}
                    return
            except Exception as e:
                logger.warning(f"Error checking 404 state: {e}")

            # Wait for grid items to appear
            try:
                # Wait for the container first
                await page.wait_for_selector("#quotesList", timeout=15000)
                # Then wait for items
                await page.wait_for_selector(".grid-item.bqQt", timeout=15000)
            except Exception as e:
                logger.warning(f"No quotes found (selector timed out): {e}")
                # Debug: log content length and take screenshot
                content = await page.content()
                logger.info(f"Page content length: {len(content)}")
                
                # Save screenshot to debug visually
                screenshot_path = f"debug_screenshot_{topic}.png"
                await page.screenshot(path=screenshot_path)
                logger.info(f"Saved debug screenshot to {screenshot_path}")
                
                yield {"error": "No quotes found. The site might be blocking the scraper. Check backend logs for screenshot."}
                return

            # Select only actual quote items (exclude ads which are just .grid-item)
            quote_elements = await page.query_selector_all(".grid-item.bqQt")
            total = len(quote_elements)
            logger.info(f"Found {total} potential quote elements.")
            
            # Send initial "start" event
            yield {"total": total} 

            for idx, el in enumerate(quote_elements, start=1):
                try:
                    text_el = await el.query_selector("a.b-qt")
                    author_el = await el.query_selector("a.bq-aut")
                     # ... (image processing matches existing code) ...
                    
                    # Try finding image
                    img_el = await el.query_selector("img.bqphtgrid")
                    img_src = None
                    if img_el:
                        img_src = await img_el.get_attribute("src")
                        if not img_src or "base64" in img_src:
                            data_src = await img_el.get_attribute("data-src")
                            if data_src:
                                img_src = data_src
                        
                        if img_src and img_src.startswith("/"):
                            img_src = "https://www.brainyquote.com" + img_src

                    if not text_el or not author_el:
                        # Even if we skip, we should update progress so frontend doesn't hang
                        yield {"progress": idx, "total": total}
                        continue

                    text = (await text_el.inner_text()).strip()
                    author = (await author_el.inner_text()).strip()
                    link = "https://www.brainyquote.com" + (await text_el.get_attribute("href") or "")

                    yield {
                        "text": text,
                        "author": author,
                        "link": link,
                        "image_url": img_src,
                        "progress": idx,
                        "total": total
                    }
                    
                    # Small delay
                    await asyncio.sleep(0.1)
                    
                except Exception as item_error:
                    logger.error(f"Error scraping item {idx}: {item_error}")
                    # Yield progress even on error
                    yield {"progress": idx, "total": total}
                    continue
            
            # Ensure we send a distinct "done" event or just the final progress
            yield {"done": True, "total": total}

        except Exception as e:
            logger.error(f"Global error in scraper: {e}")
            yield {"error": str(e)}
        finally:
            await browser.close()
