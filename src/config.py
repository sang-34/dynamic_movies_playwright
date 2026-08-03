from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Config:
    base_url: str = "https://spa2.scrape.center/page/{page}"
    pages: int = 10
    headless: bool = True
    timeout_ms: int = 10_000
    retries: int = 3
    output_path: Path = Path("outputs/movies.jsonl")
    screenshot_dir: Path = Path("screenshots")
    observe_api: bool = False






