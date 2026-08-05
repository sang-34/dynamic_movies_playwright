from dataclasses import dataclass, field
from datetime import datetime, timezone
from time import perf_counter
from typing import Any


@dataclass(slots=True)
class CrawlStats:
    page_completed: int = 0
    url_discovered: int = 0
    success: int = 0
    failed: int = 0
    skipped: int = 0
    retries: int = 0
    started_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    elapsed_seconds: float = 0.0

    _started_counter: float = field(
        default_factory=perf_counter,
        init=False, repr=False,
    )

    def record_retry(self) -> None:
        self.retries += 1

    def finish(self) -> None:
        self.elapsed_seconds = perf_counter() - self._started_counter

    def to_dict(self) -> dict[str, Any]:
        return {
            "page_completed": self.page_completed,
            "url_discovered": self.url_discovered,
            "success": self.success,
            "failed": self.failed,
            "skipped": self.skipped,
            "retries": self.retries,
            "started_at": self.started_at.isoformat(),
            "elapsed_seconds": self.elapsed_seconds,
        }
