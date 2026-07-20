"""生成：上下文 + 问题 -> 答案。

学习点：
- Prompt 约束模型“只根据资料回答；没有就说不知道”
- 引用不能消灭幻觉，但能帮你验证答案是否有据
"""

from __future__ import annotations

from dataclasses import dataclass

from rag.store import SearchHit


@dataclass
class Answer:
    text: str
    sources: list[SearchHit]


class Generator:
    def __init__(self, model: str) -> None:
        self.model = model
        # TODO: 初始化 chat 客户端
        raise NotImplementedError("TODO: Generator.__init__")

    def build_prompt(self, question: str, hits: list[SearchHit]) -> str:
        """把检索片段组装成 prompt。

        TODO 提示词至少包含：
        - 角色：只基于给定资料回答
        - 资料不足时回答“不知道”
        - 要求列出使用的来源（source + chunk index）
        """
        raise NotImplementedError("TODO: build_prompt")

    def generate(self, question: str, hits: list[SearchHit]) -> Answer:
        """调用 LLM 并包装为 Answer。"""
        # TODO: build_prompt -> chat completion -> Answer
        raise NotImplementedError("TODO: generate")
