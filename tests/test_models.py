import pytest

from src.models import Movie


def test_movie_cleaning_and_serialization(raw_movie):
    movie = Movie.from_raw(raw_movie)

    assert movie.to_dict() == {
        "url": "https://example.com/detail/1",
        "name": "霸王别姬",
        "cover": "https://example.com/cover.jpg",
        "drama": "一段电影简介。",
        "categories": ["剧情", "爱情"],
        "score": 9.5,
    }


@pytest.mark.parametrize(
    "field",
    ["url", "name", "cover", "drama"],
)
def test_required_text_is_rejected(field, raw_movie):
    raw_movie[field] = "   "

    with pytest.raises(ValueError, match=field):
        Movie.from_raw(raw_movie)


@pytest.mark.parametrize(
    ("raw_score", "expected"),
    [
        ("8.5", 8.5),
        (7, 7.0),
        (None, 0.0),
        (" ", 0.0),
    ],
)
def test_score_conversion(raw_score, expected, raw_movie):
    raw_movie["score"] = raw_score

    assert Movie.from_raw(raw_movie).score == expected


@pytest.mark.parametrize("raw_score", ["invalid", object()])
def test_invalid_score_is_rejected(raw_score, raw_movie):
    raw_movie["score"] = raw_score

    with pytest.raises(ValueError, match="score must be a number"):
        Movie.from_raw(raw_movie)


@pytest.mark.parametrize(
    "raw_score",
    [-0.1, 10.1, float("nan"), float("inf")],
)
def test_out_of_range_score_is_rejected(raw_score, raw_movie):
    raw_movie["score"] = raw_score

    with pytest.raises(
        ValueError,
        match="score must be between 0 and 10",
    ):
        Movie.from_raw(raw_movie)


def test_category_empty_values_are_removed(raw_movie):
    raw_movie["categories"] = [
        None,
        "",
        "   ",
        " 剧情 ",
        123,
    ]

    movie = Movie.from_raw(raw_movie)

    assert movie.categories == ["剧情", "123"]
    assert all(isinstance(item, str) for item in movie.categories)
