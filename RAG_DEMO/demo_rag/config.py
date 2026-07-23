"""全局配置：从 .env 读取外网 Embedding / Chat，以及本机（Ubuntu）Milvus。

注意：包名是 demo_rag，避免和仓库根目录的正式 rag/ 包冲突（否则 IDE 引用会红）。
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# demo_rag/config.py → 上一级才是 RAG_DEMO 根目录
_DEMO_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_DEMO_ROOT / ".env")

PROJECT_ROOT = _DEMO_ROOT
DATA_DIR = Path(os.getenv("DATA_DIR", str(PROJECT_ROOT / "data" / "sample")))
INDEX_DIR = PROJECT_ROOT / ".index"

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "512"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))
TOP_K = int(os.getenv("TOP_K", "4"))

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
CHAT_MODEL = os.getenv("CHAT_MODEL", "gpt-4o-mini")
EMBEDDING_BATCH_SIZE = int(os.getenv("EMBEDDING_BATCH_SIZE", "32"))

MILVUS_HOST = os.getenv("MILVUS_HOST", "127.0.0.1")
MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")
MILVUS_COLLECTION = os.getenv("MILVUS_COLLECTION", "rag_demo_chunks")
MILVUS_METRIC = os.getenv("MILVUS_METRIC", "COSINE")


def require_openai_key() -> None:
    if not OPENAI_API_KEY or OPENAI_API_KEY.startswith("sk-xxx"):
        raise RuntimeError(
            "请先在 RAG_DEMO/.env 填写有效的 OPENAI_API_KEY（可复制 .env.example）。"
        )
