import argparse
from collections.abc import Sequence
from typing import Optional

from .config import Config


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
    print(config)


if __name__ == "__main__":
    main()
