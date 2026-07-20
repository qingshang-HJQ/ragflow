"""向量存储：入库与相似度检索。

学习点：
- store 只负责“存向量 + 按相似度找邻居”
- 元数据（原文、来源）要和向量一起存，否则检索后无法拼上下文
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from rag.chunker import Chunk


@dataclass
class SearchHit:
    chunk: Chunk
    score: float


class VectorStore:
    """可用 FAISS / Chroma / 纯 NumPy 余弦相似度实现其一。"""

    def __init__(self, index_dir: Path) -> None:
        self.index_dir = index_dir
        # TODO: 初始化内存索引或从磁盘加载
        raise NotImplementedError("TODO: VectorStore.__init__")

    def add(self, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        """写入 chunk 与对应向量。"""
        # TODO: 校验长度一致；写入索引与元数据
        raise NotImplementedError("TODO: add")

    def search(self, query_vector: list[float], top_k: int) -> list[SearchHit]:
        """返回相似度最高的 top_k 条。"""
        # TODO: 相似度计算 + 排序 + 带回 Chunk
        raise NotImplementedError("TODO: search")

    def save(self) -> None:
        """持久化到 index_dir，便于下次 ask 不必重建。"""
        raise NotImplementedError("TODO: save")

    def load(self) -> None:
        """从 index_dir 加载。"""
        raise NotImplementedError("TODO: load")
