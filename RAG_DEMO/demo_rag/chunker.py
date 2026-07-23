"""文本切分：LoadedFile -> Chunk。

本 DEMO 优先走 parse.TxtParser（按分隔符 + token 预算），
与「解析后再切块」的学习路径一致；也保留简单字符窗口作为备用。
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

from .loader import LoadedFile
from .parse import TxtParser


@dataclass
class Chunk:
    id: str
    text: str
    source: str
    index: int


def _stable_id(source: str, index: int, text: str) -> str:
    """稳定 id：同源同序同内容则不变，便于重复 ingest 时对照。"""
    raw = f"{source}::{index}::{text[:64]}"
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]


def split_loaded_files(
    files: list[LoadedFile],
    chunk_token_num: int = 512,
    delimiter: str = "\n!?;。；！？",
) -> list[Chunk]:
    """加载结果 → TxtParser 切段 → Chunk 列表。"""
    parser = TxtParser()
    chunks: list[Chunk] = []
    for f in files:
        # TxtParser 返回 [[text, meta], ...]
        sections = parser(f.name, binary=f.blob, chunk_token_num=chunk_token_num, delimiter=delimiter)
        for i, pair in enumerate(sections):
            text = (pair[0] if pair else "") or ""
            text = text.strip()
            if not text:
                continue
            chunks.append(
                Chunk(
                    id=_stable_id(f.name, i, text),
                    text=text,
                    source=f.name,
                    index=i,
                )
            )
    return chunks


# 兼容旧骨架函数名：内部转调 split_loaded_files
def split_documents(
    documents: list[LoadedFile],
    chunk_size: int,
    chunk_overlap: int,  # noqa: ARG001 — TxtParser 路径暂不用 overlap
) -> list[Chunk]:
    """骨架兼容入口：chunk_size 当作近似 token 预算。"""
    return split_loaded_files(documents, chunk_token_num=chunk_size)

