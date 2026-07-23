"""向量存储：Milvus 入库与相似度检索。

学习点：
- store 只负责「存向量 + 按相似度找邻居」，不算 embedding。
- 元数据（原文 text、来源 source）必须和向量一起存，否则检索后无法拼 Prompt。
- 换 embedding 模型导致维度变化时，需要删掉旧 collection 再建（不能混用）。
"""

from __future__ import annotations

from dataclasses import dataclass

from pymilvus import (
    Collection,
    CollectionSchema,
    DataType,
    FieldSchema,
    connections,
    utility,
)

from . import config
from .chunker import Chunk


@dataclass
class SearchHit:
    """检索命中：带回原文，供 Generator 使用。"""

    chunk: Chunk
    score: float


class VectorStore:
    """对接本机 / Ubuntu 上的 Milvus Standalone（默认无用户名密码）。"""

    def __init__(
        self,
        host: str | None = None,
        port: str | None = None,
        collection_name: str | None = None,
        metric_type: str | None = None,
    ) -> None:
        self.host = host or config.MILVUS_HOST
        self.port = str(port or config.MILVUS_PORT)
        self.collection_name = collection_name or config.MILVUS_COLLECTION
        self.metric_type = (metric_type or config.MILVUS_METRIC).upper()
        self._collection: Collection | None = None

        # 默认无账号密码；若你以后开了鉴权，可在此加 user/password
        connections.connect(
            alias="default",
            host=self.host,
            port=self.port,
        )

    def ensure_collection(self, dim: int) -> Collection:
        """若 collection 不存在则创建；维度必须与 embedding 模型一致。"""
        if utility.has_collection(self.collection_name):
            col = Collection(self.collection_name)
            # 简单校验：已有向量字段维度是否匹配
            for field in col.schema.fields:
                if field.name == "embedding":
                    existing_dim = field.params.get("dim")
                    if existing_dim is not None and int(existing_dim) != int(dim):
                        raise RuntimeError(
                            f"Milvus collection「{self.collection_name}」维度={existing_dim}，"
                            f"当前模型维度={dim}。请换 collection 名或删除旧库后重建。"
                        )
            col.load()
            self._collection = col
            return col

        # ---- Schema：主键 + 原文元数据 + 向量 ----
        # text 用 65535 上限；超长入库前会截断
        fields = [
            FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=64),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="source", dtype=DataType.VARCHAR, max_length=512),
            FieldSchema(name="chunk_index", dtype=DataType.INT64),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=dim),
        ]
        schema = CollectionSchema(fields, description="RAG_DEMO chunks")
        col = Collection(name=self.collection_name, schema=schema)

        # IVF_FLAT：DEMO 数据量小足够；nlist 可按数据量调
        col.create_index(
            field_name="embedding",
            index_params={
                "index_type": "IVF_FLAT",
                "metric_type": self.metric_type,
                "params": {"nlist": 128},
            },
        )
        col.load()
        self._collection = col
        return col

    def _col(self) -> Collection:
        if self._collection is None:
            raise RuntimeError("请先调用 ensure_collection(dim) 或 add(...)")
        return self._collection

    @staticmethod
    def _truncate_text(text: str, max_len: int = 60000) -> str:
        """Milvus VARCHAR 有上限；过长则截断并留标记。"""
        if len(text) <= max_len:
            return text
        return text[: max_len - 20] + "\n...[truncated]"

    def add(self, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        """写入 chunk 与对应向量；长度必须一致。"""
        if len(chunks) != len(vectors):
            raise ValueError(f"chunks={len(chunks)} 与 vectors={len(vectors)} 数量不一致")
        if not chunks:
            return

        dim = len(vectors[0])
        col = self.ensure_collection(dim)

        # pymilvus insert：按字段列式传入
        ids = [c.id for c in chunks]
        texts = [self._truncate_text(c.text) for c in chunks]
        sources = [c.source[:512] for c in chunks]
        indexes = [int(c.index) for c in chunks]

        col.insert([ids, texts, sources, indexes, vectors])
        col.flush()  # DEMO 立即可见；生产可按批量策略 flush

    def search(self, query_vector: list[float], top_k: int) -> list[SearchHit]:
        """返回相似度最高的 top_k 条（附带原文）。"""
        col = self._col()
        # nprobe：IVF 探测桶数，越大越准越慢
        results = col.search(
            data=[query_vector],
            anns_field="embedding",
            param={"metric_type": self.metric_type, "params": {"nprobe": 16}},
            limit=top_k,
            output_fields=["text", "source", "chunk_index"],
        )

        def _get(entity, key: str, default=""):
            # 兼容 pymilvus 不同小版本的 entity 访问方式
            if hasattr(entity, "get"):
                val = entity.get(key)
                if val is not None:
                    return val
            return getattr(entity, key, default)

        hits: list[SearchHit] = []
        for hit in results[0]:
            entity = hit.entity
            chunk = Chunk(
                id=str(hit.id),
                text=str(_get(entity, "text") or ""),
                source=str(_get(entity, "source") or ""),
                index=int(_get(entity, "chunk_index", 0) or 0),
            )
            # COSINE 时 distance 语义因版本略有差异；DEMO 直接展示即可
            hits.append(SearchHit(chunk=chunk, score=float(hit.distance)))
        return hits

    def drop(self) -> None:
        """删除整个 collection（换模型维度时用）。"""
        if utility.has_collection(self.collection_name):
            utility.drop_collection(self.collection_name)
            self._collection = None

    def count(self) -> int:
        """当前实体数量（便于 ingest 后验收）。"""
        if not utility.has_collection(self.collection_name):
            return 0
        col = Collection(self.collection_name)
        col.flush()
        return int(col.num_entities)

    # 兼容骨架里的 save/load：Milvus 数据在服务端，这里无需本地落盘
    def save(self) -> None:
        """Milvus 已在服务端持久化；保留空实现方便 pipeline 调用。"""
        return None

    def load(self) -> None:
        """确保 collection 已 load 到内存。"""
        if utility.has_collection(self.collection_name):
            col = Collection(self.collection_name)
            col.load()
            self._collection = col

