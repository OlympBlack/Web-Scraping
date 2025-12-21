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
            
            # Navigate to the first page
            try:
                await page.goto(url, timeout=60000, wait_until="domcontentloaded")
            except Exception as e:
                logger.error(f"Failed to load page: {e}")
                yield {"error": f"Failed to load page: {str(e)}"}
                return

            page_number = 1
            max_pages = 20 # Safety limit

            while page_number <= max_pages:
                logger.info(f"Scraping page {page_number} for topic '{topic}'")

                # Check for "Page Not Found" (invalid topic) on first page mainly
                if page_number == 1:
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
                    logger.warning(f"No quotes found on page {page_number} (selector timed out): {e}")
                    if page_number == 1:
                        # Only critical if it's the first page
                        # Debug: log content length and take screenshot
                        content = await page.content()
                        logger.info(f"Page content length: {len(content)}")
                        
                        screenshot_path = f"debug_screenshot_{topic}_p{page_number}.png"
                        await page.screenshot(path=screenshot_path)
                        logger.info(f"Saved debug screenshot to {screenshot_path}")
                        
                        yield {"error": "No quotes found. The site might be blocking the scraper."}
                        return
                    else:
                        logger.info("No more quotes found on this page, stopping.")
                        break

                # Select only actual quote items (exclude ads which are just .grid-item)
                quote_elements = await page.query_selector_all(".grid-item.bqQt")
                total_on_page = len(quote_elements)
                logger.info(f"Found {total_on_page} quotes on page {page_number}.")
                
                # Send information about this page to initialize/reset progress bar for this page
                yield {"total": total_on_page, "page": page_number}

                for idx, el in enumerate(quote_elements, start=1):
                    try:
                        text_el = await el.query_selector("a.b-qt")
                        author_el = await el.query_selector("a.bq-aut")
                        
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
                            yield {"progress": idx, "total": total_on_page}
                            continue

                        text = (await text_el.inner_text()).strip()
                        author = (await author_el.inner_text()).strip()
                        link = "https://www.brainyquote.com" + (await text_el.get_attribute("href") or "")

                        yield {
                            "text": text,
                            "author": author,
                            "link": link,
                            "image_url": img_src,
                            "page": page_number,
                            "progress": idx,
                            "total": total_on_page
                        }
                        
                        # Small delay
                        await asyncio.sleep(0.05)
                        
                    except Exception as item_error:
                        logger.error(f"Error scraping item {idx} on page {page_number}: {item_error}")
                        yield {"progress": idx, "total": total_on_page}
                        continue
                
                # Pagination Logic
                try:
                    # Look for "Next" button/link. BrainyQuote usually has a "Next" text or an icon.
                    # We try to find a link that contains "Next" or has a class indicative of next page.
                    # Usually: <ul class="pagination"> ... <li><a href="...">Next</a></li>
                    
                    next_button = await page.query_selector("ul.pagination li.page-item:last-child a")
                    # Or try text match if class structure changed
                    if not next_button:
                        next_button = await page.get_by_text("Next", exact=True).element_handle()
                    
                    if next_button:
                        # Check if it's disabled (sometimes 'disabled' class on li)
                        parent_li = await next_button.evaluate_handle("el => el.parentElement")
                        class_name = await parent_li.get_attribute("class")
                        if class_name and "disabled" in class_name:
                            logger.info("Next button is disabled. End of pagination.")
                            break
                        
                        logger.info("Next button found, navigating to next page...")
                        await next_button.click()
                        await page.wait_for_load_state("domcontentloaded")
                        page_number += 1
                        await asyncio.sleep(1) # Be polite
                    else:
                        logger.info("No Next button found. End of pagination.")
                        break
                        
                except Exception as pag_error:
                    logger.warning(f"Error during pagination check: {pag_error}")
                    break

            yield {"done": True, "total_pages": page_number}

        except Exception as e:
            logger.error(f"Global error in scraper: {e}")
            yield {"error": str(e)}
        finally:
            await browser.close()
