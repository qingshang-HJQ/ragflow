"""生成：上下文 + 问题 -> 答案（外网 Chat API）。

学习点：
- Prompt 约束模型「只根据资料回答；没有就说不知道」。
- 引用不能消灭幻觉，但能帮你验证答案是否有据。
"""

from __future__ import annotations

from dataclasses import dataclass

from openai import OpenAI

from . import config
from .store import SearchHit


@dataclass
class Answer:
    text: str
    sources: list[SearchHit]


class Generator:
    def __init__(
        self,
        model: str | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
    ) -> None:
        config.require_openai_key()
        self.model = model or config.CHAT_MODEL
        self._client = OpenAI(
            api_key=api_key or config.OPENAI_API_KEY,
            base_url=base_url or config.OPENAI_BASE_URL,
        )

    def build_prompt(self, question: str, hits: list[SearchHit]) -> str:
        """把检索片段组装成 user 侧资料块。"""
        if not hits:
            docs = "（无检索结果）"
        else:
            parts = []
            for i, h in enumerate(hits):
                parts.append(
                    f"[{i}] 来源: {h.chunk.source}#chunk{h.chunk.index}\n{h.chunk.text}"
                )
            docs = "\n\n".join(parts)

        return (
            "请严格根据下列资料回答用户问题。\n"
            "规则：\n"
            "1. 只能使用资料中的信息；资料不足时明确回答「不知道」。\n"
            "2. 不要编造法律条文、数字或原文没有的内容。\n"
            "3. 回答末尾用「引用:」列出用到的来源编号，如 [0],[2]。\n\n"
            f"资料：\n{docs}\n\n"
            f"问题：{question}\n"
        )

    def generate(self, question: str, hits: list[SearchHit]) -> Answer:
        """调用 Chat Completions，返回 Answer。"""
        user_content = self.build_prompt(question, hits)
        resp = self._client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "你是严谨的企业知识库助手，只依据给定资料作答。",
                },
                {"role": "user", "content": user_content},
            ],
            temperature=0.2,
        )
        text = (resp.choices[0].message.content or "").strip()
        return Answer(text=text, sources=hits)

