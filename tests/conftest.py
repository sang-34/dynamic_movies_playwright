import pytest


@pytest.fixture
def raw_movie() -> dict[str, object]:
    return {
        "url": "  https://example.com/detail/1  ",
        "name": " 霸王别姬 ",
        "cover": " https://example.com/cover.jpg ",
        "drama": " 一段电影简介。 ",
        "categories": [" 剧情 ", " 爱情 "],
        "score": " 9.5 ",
    }
