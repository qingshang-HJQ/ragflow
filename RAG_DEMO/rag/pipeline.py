"""Pipeline：串联 ingest 与 ask。

学习点：
- 端到端链路清晰后，再去对照 RAGFlow 源码会快很多
"""

from __future__ import annotations

from rag.generator import Answer


def ingest() -> None:
    """load -> chunk -> embed -> store.save

    TODO: 按 config 读取目录与参数，完成建库。
    """
    raise NotImplementedError("TODO: ingest")


def ask(question: str) -> Answer:
    """load store -> retrieve -> generate

    TODO: 返回 Answer，供 main / eval 使用。
    """
    raise NotImplementedError("TODO: ask")
