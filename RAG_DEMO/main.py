"""CLI 入口。

在 PyCharm 中请用：
  from RAG_DEMO.demo_rag...   （工程根 = ragflow 时 IDE 可解析）

运行时仍推荐：
  cd RAG_DEMO && python main.py ...
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent          # .../RAG_DEMO
_REPO = _ROOT.parent                             # .../ragflow
# 仓库根：解析 RAG_DEMO.demo_rag；DEMO 根：兼容 import demo_rag
for _p in (_REPO, _ROOT):
    s = str(_p)
    if s not in sys.path:
        sys.path.insert(0, s)


def cmd_ping() -> None:
    from pymilvus import connections, utility

    from RAG_DEMO.demo_rag import config
    from RAG_DEMO.demo_rag.embedder import Embedder

    print(f"Milvus → {config.MILVUS_HOST}:{config.MILVUS_PORT}")
    connections.connect(alias="default", host=config.MILVUS_HOST, port=config.MILVUS_PORT)
    print(f"  OK  version={utility.get_server_version()}")

    print(f"Embedding → {config.OPENAI_BASE_URL}  model={config.EMBEDDING_MODEL}")
    emb = Embedder()
    vec = emb.embed_query("连通性测试")
    print(f"  OK  dim={len(vec)}")


def cmd_ingest(drop: bool = False) -> None:
    from RAG_DEMO.demo_rag.pipeline import ingest

    ingest(drop_existing=drop)


def cmd_ask(question: str) -> None:
    from RAG_DEMO.demo_rag.pipeline import ask

    ans = ask(question)
    print("\n===== 答案 =====")
    print(ans.text)
    print("\n===== 引用片段 =====")
    for i, h in enumerate(ans.sources):
        preview = h.chunk.text.replace("\n", " ")[:120]
        print(f"[{i}] {h.chunk.source}#{h.chunk.index}  score={h.score:.4f}")
        print(f"    {preview}")


def cmd_eval() -> None:
    from eval.runner import run_eval

    run_eval()


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print(__doc__)
        return 1

    cmd = argv[0]
    if cmd == "ping":
        cmd_ping()
        return 0
    if cmd == "ingest":
        cmd_ingest(drop="--drop" in argv[1:])
        return 0
    if cmd == "ask":
        if len(argv) < 2:
            print('用法: python main.py ask "你的问题"')
            return 1
        cmd_ask(" ".join(argv[1:]))
        return 0
    if cmd == "eval":
        cmd_eval()
        return 0

    print(f"未知命令: {cmd}")
    print(__doc__)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
