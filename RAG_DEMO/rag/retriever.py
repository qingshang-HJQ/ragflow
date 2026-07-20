"""检索：问题 -> top-k Chunk。

学习点：
- 答错时先看这里返回的片段，再决定改切分还是改生成
- top_k 过小漏召回；过大引入噪声
"""

from __future__ import annotations

from rag.embedder import Embedder
from rag.store import SearchHit, VectorStore


class Retriever:
    def __init__(self, store: VectorStore, embedder: Embedder, top_k: int) -> None:
        self.store = store
        self.embedder = embedder
        self.top_k = top_k

    def retrieve(self, query: str) -> list[SearchHit]:
        """query embedding -> store.search。

        TODO:
        - embed query
        - search top_k
        - 打印调试信息（可选）：每条 hit 的 source / score / 前 80 字
        """
        raise NotImplementedError("TODO: retrieve")
