"""文档加载：从 data/sample 读取 .md / .txt。

学习点：
- Document 是原始材料；后续所有步骤都依赖这里读到的干净文本。
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class Document:
    path: str
    text: str


def load_documents(data_dir: Path) -> list[Document]:
    """扫描目录，返回 Document 列表。

    TODO:
    - 递归或非递归读取 .md / .txt
    - 跳过空文件
    - 用 utf-8 读取，处理好编码错误
    """
    raise NotImplementedError("TODO: load_documents")
