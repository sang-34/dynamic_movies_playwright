from dataclasses import dataclass, asdict, field
from collections.abc import Iterable, Mapping
from typing import Any


@dataclass(slots=True)
class Movie:
    url: str
    name: str
    cover: str
    drama: str
    categories: list[str] = field(default_factory=list)
    score: float = 0.0


    @classmethod
    def from_raw(cls, raw: Mapping[str, Any]) -> "Movie":
        url = cls._required_text(raw.get("url"), "url")
        name = cls._required_text(raw.get("name"), "name")
        cover = cls._required_text(raw.get("cover"), "cover")
        drama = cls._required_text(raw.get("drama"), "drama")
        categories = cls._normalize_categories(raw.get("categories"))
        score = cls._normalize_score(raw.get("score"))


        return cls(
            url=url, name=name, cover=cover, drama=drama,
            categories=categories, score=score
        )

    @staticmethod
    def _required_text(value: Any, field_name: str) -> str:
        if value is None:
            raise ValueError(f"{field_name} cannot be empty")

        cleaned = str(value).strip()
        if not cleaned:
            raise ValueError(f"{field_name} cannot be empty")

        return cleaned

    @staticmethod
    def _normalize_categories(value: Any) -> list[str]:
        if value is None:
            return []

        if isinstance(value, str):
            values: Iterable[Any] = [value]
        elif isinstance(value, Iterable):
            values = value
        else:
            values = [value]

        categories: list[str] = []

        for item in values:
            if item is None:
                continue

            cleaned = str(item).strip()
            if cleaned:
                categories.append(cleaned)

        return categories

    @staticmethod
    def _normalize_score(value:Any) -> float:
        if value is None:
            return 0.0

        if isinstance(value, str):
            value = value.strip()
            if not value:
                return 0.0

        try:
            score = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError("score must be a number") from exc

        if not 0.0 <= score <= 10.0:
            raise ValueError("score must be between 0 and 10")

        return score

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
