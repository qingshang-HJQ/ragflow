"""Pipeline：串联 ingest 与 ask。

架构：
  本地文件 → loader → parse/chunker → 外网 Embedding → Ubuntu Milvus
  用户问题 → 外网 Embedding → Milvus top-k → 外网 Chat → 答案+引用
"""

from __future__ import annotations

from . import config
from .chunker import split_loaded_files
from .embedder import Embedder
from .generator import Answer, Generator
from .loader import load_documents
from .retriever import Retriever
from .store import VectorStore


def ingest(*, drop_existing: bool = False) -> None:
    """load → chunk → embed → Milvus.insert。

    Args:
        drop_existing: True 时先删旧 collection（换模型/维度时用）。
    """
    print(f"[ingest] data_dir={config.DATA_DIR}")
    print(f"[ingest] milvus={config.MILVUS_HOST}:{config.MILVUS_PORT}  collection={config.MILVUS_COLLECTION}")

    files = load_documents(config.DATA_DIR)
    if not files:
        raise FileNotFoundError(f"未找到 .md/.txt：{config.DATA_DIR}")

    chunks = split_loaded_files(files, chunk_token_num=config.CHUNK_SIZE)
    print(f"[ingest] files={len(files)}  chunks={len(chunks)}")
    if not chunks:
        raise RuntimeError("切块结果为空，请检查样例文档与 CHUNK_SIZE")

    embedder = Embedder()
    store = VectorStore()
    if drop_existing:
        print("[ingest] drop existing collection ...")
        store.drop()

    texts = [c.text for c in chunks]
    print(f"[ingest] embedding via {config.EMBEDDING_MODEL} ...")
    vectors = embedder.embed_texts(texts)
    print(f"[ingest] vector dim={embedder.dim}  count={len(vectors)}")

    store.add(chunks, vectors)
    store.save()
    n = store.count()
    print(f"[ingest] done. milvus entities≈{n}")
    if n < len(chunks):
        print("[ingest] 提示: 实体数小于本次 chunks，可能是重复主键被拒绝；可用 ingest --drop 全量重建。")
    elif n > len(chunks):
        print("[ingest] 提示: 库中已有历史数据（未 --drop）。检索仍可用；要干净重建请加 --drop。")


def ask(question: str, *, debug_retrieve: bool = True) -> Answer:
    """load Milvus → retrieve → generate。"""
    embedder = Embedder()
    store = VectorStore()
    store.load()

    # 若库是空的，search 会失败或无结果；提示先 ingest
    if store.count() == 0:
        raise RuntimeError("Milvus collection 为空或不存在，请先执行: python main.py ingest")

    # ensure_collection 需要 dim；用一次 query embed 拿到维度并 load
    _ = embedder.embed_query(question)
    assert embedder.dim is not None
    store.ensure_collection(embedder.dim)

    retriever = Retriever(store, embedder, config.TOP_K)
    hits = retriever.retrieve(question, debug=debug_retrieve)

    generator = Generator()
    answer = generator.generate(question, hits)
    return answer

