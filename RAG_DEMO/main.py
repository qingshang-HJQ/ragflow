"""CLI 入口：ingest / ask / eval。

用法（实现后）：
  python main.py ingest
  python main.py ask "你的问题"
  python main.py eval
"""

from __future__ import annotations

import sys


def cmd_ingest() -> None:
    """把 data/sample 文档切分、向量化并写入索引。"""
    # TODO: 调用 rag.pipeline.ingest()
    raise NotImplementedError("TODO: ingest")


def cmd_ask(question: str) -> None:
    """对单个问题检索 + 生成，并打印引用片段。"""
    # TODO: 调用 rag.pipeline.ask(question)，打印 answer 与 sources
    raise NotImplementedError("TODO: ask")


def cmd_eval() -> None:
    """跑 eval/questions.json，打印简易评测结果。"""
    # TODO: 调用 eval.runner.run_eval()
    raise NotImplementedError("TODO: eval")


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print("Usage: python main.py [ingest|ask <q>|eval]")
        return 1

    # TODO: 解析子命令并分发到 cmd_*
    raise NotImplementedError("TODO: wire CLI")


if __name__ == "__main__":
    raise SystemExit(main())
