import re
import time
from datetime import datetime
from urllib.parse import urlsplit, urljoin

from playwright.sync_api import (
    Error as PlaywrightError,
    Page,
    TimeoutError as PlaywrightTimeoutError,
)

from .config import Config
from .models import Movie

_RETRY_DELAYS = (1, 2)


def _save_failure_screenshot(page: Page, url: str, config: Config) -> None:
    try:
        config.screenshot_dir.mkdir(parents=True, exist_ok=True)

        path_part = urlsplit(url).path.strip("/") or "page"
        safe_name = re.sub(r"[^a-zA-Z0-9_.-]", "_", path_part)[:80]
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S_%f")
        screenshot_path = config.screenshot_dir / f"{safe_name}_{timestamp}.png"

        page.screenshot(path=str(screenshot_path), full_page=True)
        print(f"失败截图已保存: {screenshot_path}")

    except (OSError, PlaywrightError) as exc:
        print(f"保存失败截图时出错: {exc}")


def open_page(page: Page, url: str, config: Config)  -> bool:
    attempts = max(config.retries, 1)

    for attempt in range(1, attempts + 1):
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=config.timeout_ms)
            return True
        except (PlaywrightTimeoutError, PlaywrightError) as exc:
            print(f"打开页面失败: {url}, 第 {attempt}/{attempts} 次尝试, 错误: {exc}")

        if attempt == attempts:
            _save_failure_screenshot(page, url, config)
            return False

        delay = _RETRY_DELAYS[min(attempt - 1, len(_RETRY_DELAYS) - 1)]
        print(f"{delay} 秒后重试")
        time.sleep(delay)

    return False


def crawl_index(page: Page, page_number: int, config: Config) -> list[str]:
    index_url = config.base_url.format(page=page_number)

    if not open_page(page, index_url, config):
        return []

    try:
        page.locator("#index .item").first.wait_for(
            state="visible", timeout=config.timeout_ms
        )

        hrefs = page.locator("#index .item a[href*='/detail/']").evaluate_all(
            "(links) => links.map(link => link.getAttribute('href'))"
        )

        absolute_urls = [urljoin(index_url, href) for href in hrefs if href]

        return list(dict.fromkeys(absolute_urls))
    except (PlaywrightTimeoutError, PlaywrightError) as exc:
        print(f"提取列表页失败: {index_url}, 错误: {exc}")
        _save_failure_screenshot(page, index_url, config)
        return []


def crawl_detail(page: Page, url: str, config: Config) -> Movie | None:
    if not open_page(page, url, config):
        return None

    try:
        page.locator("a.name h2").wait_for(state="visible", timeout=config.timeout_ms)

        cover_src = page.locator("img.cover").first.get_attribute(
            "src", timeout=config.timeout_ms
        )

        raw = {
            "url": url,
            "name": page.locator("h2").first.inner_text(timeout=config.timeout_ms),
            "cover": urljoin(url, cover_src) if cover_src else "",
            "categories": page.locator(".categories span").all_inner_texts(),
            "score": page.locator(".score").first.inner_text(timeout=config.timeout_ms),
            "drama": page.locator(".drama p").first.inner_text(timeout=config.timeout_ms),
        }

        return Movie.from_raw(raw)
    except (PlaywrightTimeoutError, PlaywrightError, ValueError) as exc:
        print(f"采集详情页面失败: {url}, 错误: {exc}")
        _save_failure_screenshot(page, url, config)
        return None
