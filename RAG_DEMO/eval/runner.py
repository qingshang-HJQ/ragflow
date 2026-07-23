"""简易评测：跑 questions.json。

先看 retrieval_hit（来源是否对），再看 keyword_hit（答案关键词）。
"""

from __future__ import annotations

import json
from pathlib import Path

QUESTIONS_PATH = Path(__file__).resolve().parent / "questions.json"


def load_questions(path: Path = QUESTIONS_PATH) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("questions", [])
    return [q for q in data if (q.get("question") or "").strip()]


def judge_one(item: dict, answer_text: str, source_paths: list[str]) -> dict:
    sources_joined = " ".join(source_paths)
    hint = (item.get("expected_source_hint") or "").strip()
    retrieval_hit = (not hint) or (hint in sources_joined)

    keywords = item.get("expected_answer_keywords") or []
    if keywords:
        hit_n = sum(1 for k in keywords if k and k in answer_text)
        keyword_hit = hit_n >= max(1, (len(keywords) + 1) // 2)
    else:
        keyword_hit = True

    expect_abstain = bool(item.get("expect_abstain"))
    abstain_ok = (not expect_abstain) or ("不知道" in answer_text)

    return {
        "retrieval_hit": retrieval_hit,
        "keyword_hit": keyword_hit,
        "abstain_ok": abstain_ok,
    }


def run_eval() -> None:
    from RAG_DEMO.demo_rag.pipeline import ask

    questions = load_questions()
    if not questions:
        print(f"无题目: {QUESTIONS_PATH}")
        return

    stats = {"retrieval_hit": 0, "keyword_hit": 0, "abstain_ok": 0, "n": 0}
    for item in questions:
        q = item["question"]
        print("\n" + "=" * 60)
        print(f"Q: {q}")
        ans = ask(q, debug_retrieve=True)
        sources = [h.chunk.source for h in ans.sources]
        judged = judge_one(item, ans.text, sources)
        print(f"A: {ans.text[:300]}")
        print(f"judge: {judged}")
        stats["n"] += 1
        for k in ("retrieval_hit", "keyword_hit", "abstain_ok"):
            stats[k] += int(judged[k])

    n = max(stats["n"], 1)
    print("\n===== 汇总 =====")
    print(f"n={stats['n']}")
    print(f"retrieval_hit={stats['retrieval_hit']}/{stats['n']} ({stats['retrieval_hit']/n:.0%})")
    print(f"keyword_hit={stats['keyword_hit']}/{stats['n']} ({stats['keyword_hit']/n:.0%})")
    print(f"abstain_ok={stats['abstain_ok']}/{stats['n']} ({stats['abstain_ok']/n:.0%})")

