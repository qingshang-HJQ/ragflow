"""检索：问题 -> top-k Chunk。

学习点：
- 答错时先看这里返回的片段，再决定改切分还是改生成。
- top_k 过小漏召回；过大引入噪声。
"""

from __future__ import annotations

from .embedder import Embedder
from .store import SearchHit, VectorStore


class Retriever:
    def __init__(self, store: VectorStore, embedder: Embedder, top_k: int) -> None:
        self.store = store
        self.embedder = embedder
        self.top_k = top_k

    def retrieve(self, query: str, *, debug: bool = True) -> list[SearchHit]:
        """query embedding（外网）-> Milvus search（内网）。"""
        qvec = self.embedder.embed_query(query)
        hits = self.store.search(qvec, self.top_k)

        if debug:
            print(f"\n[retrieve] query={query!r}  top_k={self.top_k}  hits={len(hits)}")
            for i, h in enumerate(hits):
                preview = h.chunk.text.replace("\n", " ")[:80]
                print(
                    f"  [{i}] score={h.score:.4f}  source={h.chunk.source}#{h.chunk.index}  {preview}"
                )
        return hits

