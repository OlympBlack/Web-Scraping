from playwright.sync_api import sync_playwright, TimeoutError

def scrape_quotes(topic: str):
    url = f"https://www.brainyquote.com/topics/{topic}-quotes"
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False, 
            slow_mo=50
        )

        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 800}
        )

        page = context.new_page()
        page.goto(url, timeout=60000)

        try:
            page.wait_for_selector("div.bqQt", timeout=20000)
        except TimeoutError:
            print("❌ Citations non chargées")
            browser.close()
            return results

        quote_blocks = page.query_selector_all("div.bqQt")

        print(f"✅ {len(quote_blocks)} blocs trouvés")

        for block in quote_blocks:
            quote_el = block.query_selector("a.title")
            author_el = block.query_selector("a.author")

            if not quote_el or not author_el:
                continue

            results.append({
                "text": quote_el.inner_text().strip(),
                "author": author_el.inner_text().strip(),
                "link": "https://www.brainyquote.com" + quote_el.get_attribute("href")
            })

        input("Appuie sur Entrée pour fermer le navigateur...")
        browser.close()

    return results
