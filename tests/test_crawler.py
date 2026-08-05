from pathlib import Path

from playwright.sync_api import (
    Error as PlaywrightError,
    TimeoutError as PlaywrightTimeoutError,
)

from src.config import Config
from src.crawler import open_page


class FakePage:
    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.goto_calls = []
        self.screenshot_calls = []

    def goto(self, url, *, wait_until, timeout):
        self.goto_calls.append(
            {
                "url": url,
                "wait_until": wait_until,
                "timeout": timeout,
            }
        )

        outcome = self.outcomes.pop(0)
        if isinstance(outcome, BaseException):
            raise outcome

        return outcome

    def screenshot(self, *, path, full_page):
        self.screenshot_calls.append(
            {
                "path": path,
                "full_page": full_page,
            }
        )


def test_open_page_success():
    page = FakePage([None])
    config = Config(timeout_ms=1234, retries=3)

    result = open_page(
        page,
        "https://example.com/page/1",
        config,
    )

    assert result is True
    assert len(page.goto_calls) == 1
    assert page.goto_calls[0]["timeout"] == 1234
    assert page.goto_calls[0]["wait_until"] == (
        "domcontentloaded"
    )
    assert page.screenshot_calls == []


def test_open_page_retries_then_succeeds(monkeypatch):
    page = FakePage(
        [
            PlaywrightTimeoutError("timeout"),
            PlaywrightError("temporary failure"),
            None,
        ]
    )
    config = Config(retries=3)
    delays = []
    retry_events = []

    monkeypatch.setattr(
        "src.crawler.time.sleep",
        delays.append,
    )

    result = open_page(
        page,
        "https://example.com/page/1",
        config,
        on_retry=lambda: retry_events.append(True),
    )

    assert result is True
    assert len(page.goto_calls) == 3
    assert delays == [1, 2]
    assert len(retry_events) == 2
    assert page.screenshot_calls == []


def test_open_page_final_failure_saves_screenshot(
    monkeypatch,
    tmp_path,
):
    page = FakePage(
        [
            PlaywrightTimeoutError("timeout 1"),
            PlaywrightTimeoutError("timeout 2"),
            PlaywrightError("final failure"),
        ]
    )
    screenshot_dir = tmp_path / "screenshots"
    config = Config(
        retries=3,
        screenshot_dir=screenshot_dir,
    )
    delays = []
    retry_events = []

    monkeypatch.setattr(
        "src.crawler.time.sleep",
        delays.append,
    )

    result = open_page(
        page,
        "https://example.com/page/1",
        config,
        on_retry=lambda: retry_events.append(True),
    )

    assert result is False
    assert len(page.goto_calls) == 3
    assert delays == [1, 2]
    assert len(retry_events) == 2
    assert len(page.screenshot_calls) == 1

    screenshot_call = page.screenshot_calls[0]
    screenshot_path = Path(screenshot_call["path"])

    assert screenshot_path.parent == screenshot_dir
    assert screenshot_path.suffix == ".png"
    assert screenshot_call["full_page"] is True

    # FakePage 只记录路径，不产生真实截图文件。
    assert screenshot_path.exists() is False
