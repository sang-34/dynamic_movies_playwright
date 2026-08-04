import argparse
from collections.abc import Sequence
from typing import Optional

from playwright.sync_api import sync_playwright

from .config import Config
from .crawler import crawl_index, crawl_detail
from .models import Movie


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
    return parser


def parse_config(argv: Optional[Sequence[str]] = None) -> Config:
    args = build_parser().parse_args(argv)

    return Config(pages=args.pages, headless=not args.headed)


def main(argv: Optional[Sequence[str]] = None) -> None:
    config = parse_config(argv)
    movies: list[Movie] = []

    with sync_playwright() as playwright:
        browser = None

        try:
            browser = playwright.chromium.launch(headless=config.headless)
            context = browser.new_context()
            context.set_default_timeout(timeout=config.timeout_ms)
            page = context.new_page()

            detail_urls = crawl_index(page, 1, config)
            print(f"发现 {len(detail_urls)} 个唯一详情 URL")

            for url in detail_urls:
                try:
                    movie = crawl_detail(page, url, config)
                    if movie is None:
                        continue

                    movies.append(movie)
                    print(movie.to_dict())
                except Exception as exc:
                    print(f"跳过详情页: {url}, 错误: {exc}")
        finally:
            if browser is not None:
                browser.close()

    print(f"合法 Movie 对象数量：{len(movies)}")

if __name__ == "__main__":
    main()
