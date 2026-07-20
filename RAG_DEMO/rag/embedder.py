"""Embedding：文本 -> 向量。

学习点：
- embedding 把“语义相近”变成向量空间里的距离相近
- query 与 chunk 必须用同一套 embedding 模型
"""

from __future__ import annotations


class Embedder:
    """封装 embedding API 或本地模型。"""

    def __init__(self, model: str) -> None:
        # TODO: 初始化客户端（OpenAI 兼容 API 或本地模型）
        self.model = model
        raise NotImplementedError("TODO: Embedder.__init__")

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """批量文本转向量。

        TODO:
        - 调用 embedding 接口
        - 处理空列表与批量上限
        """
        raise NotImplementedError("TODO: embed_texts")

    def embed_query(self, query: str) -> list[float]:
        """单条 query 转向量。"""
        # TODO: 复用 embed_texts
        raise NotImplementedError("TODO: embed_query")
