"""简易评测：跑 questions.json，人工/半自动判分。

学习点：
- 不要只靠感觉调参；每次只改一个变量再跑一遍
- 先看检索命中，再看答案关键词，最后看是否胡编
"""

from __future__ import annotations

from pathlib import Path


QUESTIONS_PATH = Path(__file__).resolve().parent / "questions.json"


def load_questions(path: Path = QUESTIONS_PATH) -> list[dict]:
    """读取评测题。"""
    # TODO: json.load，过滤 question 为空的条目
    raise NotImplementedError("TODO: load_questions")


def judge_one(item: dict, answer_text: str, source_paths: list[str]) -> dict:
    """对单题做极简判分。

    TODO 建议字段：
    - retrieval_hit: expected_source_hint 是否出现在 source_paths
    - keyword_hit: expected_answer_keywords 是否大部分出现在 answer_text
    - abstain_ok: 无答案题是否回答了“不知道”
    """
    raise NotImplementedError("TODO: judge_one")


def run_eval() -> None:
    """对每题调用 pipeline.ask，打印表格或逐题结果。

    TODO:
    - 遍历 questions
    - ask -> judge_one
    - 汇总 retrieval_hit / keyword_hit 比例
    """
    raise NotImplementedError("TODO: run_eval")
