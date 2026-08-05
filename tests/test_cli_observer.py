from pathlib import Path
from types import SimpleNamespace

import pytest

from src.main import parse_config
from src.observer import register_api_observer


class FakeEventPage:
    def __init__(self):
        self.callbacks = {}

    def on(self, event, callback):
        self.callbacks[event] = callback


class BrokenResponse:
    @property
    def url(self):
        raise RuntimeError("broken response")


def test_cli_pages_default_modes():
    config = parse_config(["--pages", "3"])

    assert config.pages == 3
    assert config.headless is True
    assert config.observe_api is False
    assert config.output_path == Path("outputs/movies.jsonl")


def test_cli_custom_output_path():
    config = parse_config(
        ["--output", "outputs/test.jsonl"]
    )

    assert config.output_path == Path(
        "outputs/test.jsonl"
    )


def test_cli_headed_and_observe_api():
    config = parse_config(
        ["--pages", "2", "--headed", "--observe-api"]
    )

    assert config.pages == 2
    assert config.headless is False
    assert config.observe_api is True


@pytest.mark.parametrize("value", ["0", "-1", "invalid"])
def test_cli_rejects_invalid_pages(value):
    with pytest.raises(SystemExit):
        parse_config(["--pages", value])


def test_api_observer_filters_other_responses(capsys):
    page = FakeEventPage()
    register_api_observer(page)

    callback = page.callbacks["response"]
    callback(
        SimpleNamespace(
            url="https://example.com/api/person",
            status=200,
            request=SimpleNamespace(
                method="GET",
                resource_type="xhr",
            ),
        )
    )

    assert capsys.readouterr().out == ""


def test_api_observer_output_format(capsys):
    page = FakeEventPage()
    register_api_observer(page)

    callback = page.callbacks["response"]
    callback(
        SimpleNamespace(
            url="https://example.com/api/movie/1",
            status=200,
            request=SimpleNamespace(
                method="GET",
                resource_type="xhr",
            ),
        )
    )

    output = capsys.readouterr().out

    assert "[API]" in output
    assert "status=200" in output
    assert "method=GET" in output
    assert "resource_type=xhr" in output
    assert "url=https://example.com/api/movie/1" in output


def test_api_observer_exception_is_isolated(capsys):
    page = FakeEventPage()
    register_api_observer(page)

    callback = page.callbacks["response"]

    # 回调异常必须被内部捕获，不能传播到测试调用方。
    callback(BrokenResponse())

    output = capsys.readouterr().out
    assert "[API observer error]" in output
    assert "broken response" in output
