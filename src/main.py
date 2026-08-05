import argparse
import json
from collections.abc import Sequence
from typing import Optional

from playwright.sync_api import sync_playwright

from .config import Config
from .crawler import crawl_index, crawl_detail
from .stats import CrawlStats
from .storage import JsonlStorage
from .observer import register_api_observer


def positive_int(value: str) -> int:
    try:
        number = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("page must be an integer") from exc

    if number <= 0:
        raise argparse.ArgumentTypeError("page must be greater than 0")

    return number


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Dynamic movies crawler")
    parser.add_argument(
        "--pages", type=positive_int, default=1,
        help="number of pages to crawler"
    )
    parser.add_argument(
        "--headed", action="store_true",
        help="run the browser in headed mode"
    )
    parser.add_argument(
        "--observe-api", action="store_true",
        help="print movie API response metadata"
    )
    return parser


def parse_config(argv: Optional[Sequence[str]] = None) -> Config:
    args = build_parser().parse_args(argv)

    return Config(
        pages=args.pages, headless=not args.headed, observe_api=args.observe_api
    )


def main(argv: Optional[Sequence[str]] = None) -> None:
    config = parse_config(argv)
    storage = JsonlStorage(config.output_path)
    stats = CrawlStats()
    discovered_urls: set[str] = set()

    try:
        with sync_playwright() as playwright:
            browser = None

            try:
                browser = playwright.chromium.launch(headless=config.headless)
                context = browser.new_context()
                context.set_default_timeout(timeout=config.timeout_ms)
                page = context.new_page()

                if config.observe_api:
                    register_api_observer(page)

                for page_number in range(1, config.pages + 1):
                    detail_urls = crawl_index(
                        page, page_number, config, on_retry=stats.record_retry
                    )

                    if detail_urls is None:
                        print(f"第 {page_number} 页处理失败")
                        continue

                    stats.page_completed += 1
                    discovered_urls.update(detail_urls)
                    stats.url_discovered = len(discovered_urls)

                    print(f"第 {page_number} 页发现 {len(discovered_urls)} 个唯一详情 URL")

                    for url in detail_urls:
                        if storage.contains(url):
                            stats.skipped += 1
                            continue

                        try:
                            movie = crawl_detail(
                                page, url, config, on_retry=stats.record_retry
                            )

                            if movie is None:
                                stats.failed += 1
                                continue

                            if storage.append(movie):
                                stats.success += 1
                                print(movie.to_dict())
                            else:
                                stats.skipped += 1
                        except Exception as exc:
                            stats.failed += 1
                            print(f"采集详情异常: {url}, 错误: {exc}")
            finally:
                if browser is not None:
                    browser.close()
    finally:
        stats.finish()

        print("\n采集汇总")
        print(json.dumps(stats.to_dict(), ensure_ascii=False, indent=4))
        print(f"输出文件唯一 URL 总数: {storage.url_count}")


if __name__ == "__main__":
    main()
