import json
import warnings
from pathlib import Path

from .models import Movie


class JsonlStorage:
    def __init__(self, path: Path) -> None:
        self.path = path
        self._urls: set[str] = set()
        self._load_existing()

    def _load_existing(self) -> None:
        if not self.path.exists():
            return

        with self.path.open("r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                line = line.strip()
                if not line:
                    continue

                try:
                    data = json.loads(line)
                except json.JSONDecodeError as exc:
                    warnings.warn(
                        f"{self.path}:{line_number} JSON 损坏, 已跳过: {exc}",
                        RuntimeWarning,
                        stacklevel=2,
                    )
                    continue

                if not isinstance(data, dict):
                    warnings.warn(
                        f"{self.path}:{line_number} 不是 JSON 对象, 已跳过",
                        RuntimeWarning,
                        stacklevel=2,
                    )
                    continue

                url = data.get("url")
                if not isinstance(url, str) or not url.strip():
                    warnings.warn(
                        f"{self.path}:{line_number} 缺少有效 URL, 已跳过",
                        RuntimeWarning,
                        stacklevel=2,
                    )
                    continue

                self._urls.add(url.strip())

    def contains(self, url: str) -> bool:
        return url in self._urls

    @property
    def url_count(self) -> int:
        return len(self._urls)

    def append(self, movie: Movie) -> bool:
        if movie.url in self._urls:
            return False

        line = json.dumps(movie.to_dict(), ensure_ascii=False)

        self.path.parent.mkdir(parents=True, exist_ok=True)

        with self.path.open("a", encoding="utf-8") as file:
            file.write(line)
            file.write("\n")
            file.flush()

        self._urls.add(movie.url)
        return True
