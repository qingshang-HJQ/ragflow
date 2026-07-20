"""文本切分：Document -> Chunk。

学习点：
- chunk_size 太大：检索不精准，浪费上下文
- chunk_size 太小：语义残缺
- overlap：减轻切在句子中间时的信息丢失
"""

from __future__ import annotations

from dataclasses import dataclass

from rag.loader import Document


@dataclass
class Chunk:
    id: str
    text: str
    source: str
    index: int


def split_documents(
    documents: list[Document],
    chunk_size: int,
    chunk_overlap: int,
) -> list[Chunk]:
    """按字符数（或 token 近似）切分文档。

    TODO:
    - 实现固定窗口切分 + overlap
    - 为每个 chunk 生成稳定 id（如 path + index）
    - 可选：尽量在换行 / 句号处断开
    """
    raise NotImplementedError("TODO: split_documents")
