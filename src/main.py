from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser =p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://spa2.scrape.center/page/1")
    items = page.locator("#index .item")
    items.first.wait_for(state="visible")
    print(f"数据数量:{items.count()}")
    browser.close()
    # 数据数量:10



