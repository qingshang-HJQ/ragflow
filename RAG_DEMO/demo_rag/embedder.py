"""Embedding：文本 -> 向量（调用外网 OpenAI 兼容 API）。

学习点：
- embedding 把「语义相近」变成向量空间里的距离相近。
- query 与 chunk 必须用同一套 embedding 模型（含 base_url / model 名）。
- 本 DEMO 不算本地模型；向量计算在云端，结果拿回来再写入 Milvus。
"""

from __future__ import annotations

from openai import OpenAI

from . import config


class Embedder:
    """封装外网 embedding API。"""

    def __init__(
        self,
        model: str | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
        batch_size: int | None = None,
    ) -> None:
        config.require_openai_key()
        self.model = model or config.EMBEDDING_MODEL
        self.batch_size = batch_size or config.EMBEDDING_BATCH_SIZE
        # OpenAI 官方 SDK 也兼容多数「OpenAI 格式」网关
        self._client = OpenAI(
            api_key=api_key or config.OPENAI_API_KEY,
            base_url=base_url or config.OPENAI_BASE_URL,
        )
        self._dim: int | None = None  # 首次 encode 后缓存维度，建 Milvus 表要用

    @property
    def dim(self) -> int | None:
        """向量维度；尚未编码过时为 None。"""
        return self._dim

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """批量文本转向量，返回与 texts 等长的二维列表。"""
        if not texts:
            return []

        # API 通常拒绝纯空白：统一成占位符，避免整批失败（对齐 RAGFlow 思路）
        safe = [("None" if not (t or "").strip() else t.strip()) for t in texts]

        all_vectors: list[list[float]] = []
        for i in range(0, len(safe), self.batch_size):
            batch = safe[i : i + self.batch_size]
            resp = self._client.embeddings.create(model=self.model, input=batch)
            # 按 index 排序，保证与输入顺序一致
            sorted_data = sorted(resp.data, key=lambda d: d.index)
            all_vectors.extend([list(d.embedding) for d in sorted_data])

        if len(all_vectors) != len(texts):
            raise RuntimeError(
                f"embedding 条数不一致: input={len(texts)} output={len(all_vectors)}"
            )

        self._dim = len(all_vectors[0])
        return all_vectors

    def embed_query(self, query: str) -> list[float]:
        """单条问题转向量；检索时必须走这里（与入库同一模型）。"""
        return self.embed_texts([query])[0]

