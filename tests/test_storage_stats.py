import json

import pytest

import src.stats as stats_module
from src.models import Movie
from src.stats import CrawlStats
from src.storage import JsonlStorage


def test_jsonl_utf8_write_and_duplicate_block(
    tmp_path,
    raw_movie,
):
    output_path = tmp_path / "movies.jsonl"
    storage = JsonlStorage(output_path)
    movie = Movie.from_raw(raw_movie)

    assert storage.append(movie) is True
    assert storage.append(movie) is False
    assert storage.url_count == 1

    lines = output_path.read_text(
        encoding="utf-8"
    ).splitlines()

    assert len(lines) == 1
    assert "霸王别姬" in lines[0]
    assert json.loads(lines[0]) == movie.to_dict()


def test_storage_tolerates_damaged_existing_lines(tmp_path):
    output_path = tmp_path / "movies.jsonl"
    output_path.write_text(
        "\n".join(
            [
                '{"url": "https://example.com/1"}',
                "{damaged",
                '["not", "an", "object"]',
                '{"name": "missing url"}',
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    with pytest.warns(RuntimeWarning) as warnings:
        storage = JsonlStorage(output_path)

    assert len(warnings) == 3
    assert storage.url_count == 1
    assert storage.contains("https://example.com/1")


def test_crawl_stats_counts_and_elapsed(monkeypatch):
    stats = CrawlStats()
    stats._started_counter = 100.0

    monkeypatch.setattr(
        stats_module,
        "perf_counter",
        lambda: 102.5,
    )

    stats.page_completed += 1
    stats.url_discovered = 10
    stats.success += 7
    stats.failed += 1
    stats.skipped += 2
    stats.record_retry()
    stats.record_retry()
    stats.finish()

    result = stats.to_dict()

    assert result["page_completed"] == 1
    assert result["url_discovered"] == 10
    assert result["success"] == 7
    assert result["failed"] == 1
    assert result["skipped"] == 2
    assert result["retries"] == 2
    assert result["elapsed_seconds"] == 2.5
    assert isinstance(result["started_at"], str)
    