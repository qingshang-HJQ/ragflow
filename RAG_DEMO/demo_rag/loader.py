"""文档加载：本地文件 → (name, blob)。"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

SUPPORTED = {".md", ".txt", ".markdown"}


@dataclass
class LoadedFile:
    name: str
    blob: bytes
    path: str = ""


def load_documents(data_dir: Path) -> list[LoadedFile]:
    data_dir = Path(data_dir)
    if not data_dir.is_dir():
        raise NotADirectoryError(f"不是目录: {data_dir}")

    results: list[LoadedFile] = []
    for path in sorted(data_dir.iterdir()):
        if not path.is_file():
            continue
        if path.suffix.lower() not in SUPPORTED:
            continue
        blob = path.read_bytes()
        if not blob:
            continue
        results.append(LoadedFile(name=path.name, blob=blob, path=str(path)))
    return results
