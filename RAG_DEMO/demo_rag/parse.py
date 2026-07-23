"""文档解析（TXT）：bytes/路径 → 文本 → 按分隔符与 token 预算切段。

学习点（对齐 RAGFlow deepdoc/parser/txt_parser.py）：
- 加载阶段只给 name + blob；这里才变成可读文本并粗切。
- __call__ 负责 I/O；parser_txt 是纯逻辑，便于单测和复用。
- 返回 [[text, meta], ...]，meta 留空是为了和其他解析器（PDF 等）形状一致。
"""

from __future__ import annotations

import re

# DEMO 简化：若本地没有 common.token_utils，可用 len(t)//2 近似 token 数
try:
    from common.token_utils import num_tokens_from_string
except ImportError:

    def num_tokens_from_string(text: str) -> int:
        return max(len(text) // 2, 1)


class TxtParser:
    """纯文本解析器：解码 + 按分隔符/token 合并成 chunk。"""

    def __call__(self, fnm, binary=None, chunk_token_num=128, delimiter="\n!?;。；！？"):
        """实例可当函数调用，与 RAGFlow 其他 Parser 用法一致。

        Args:
            fnm: 文件名或本地路径；有 binary 时主要用于标识。
            binary: 优先使用的文件字节（对应 loader 产出的 blob）。
            chunk_token_num: 单块大致 token 上限，超了就新开一块。
            delimiter: 切分边界字符；可用 `多字符` 包住整段当作一个分隔符。
        """
        # 1) 先统一成 str（路径读盘 / bytes 解码）
        txt = get_text(fnm, binary)
        # 2) 再切段；I/O 与切分逻辑分开
        return self.parser_txt(txt, chunk_token_num, delimiter)

    def parser_txt(self, txt, chunk_token_num=128, delimiter="\n!?;。；！？"):
        """纯文本切分：已有 str 时可直接调用，不必再读文件。"""
        if not isinstance(txt, str):
            raise TypeError("txt type should be str!")

        # cks: 已生成的文本块；tk_nums: 对应块的累计 token 数
        cks = [""]
        tk_nums = [0]

        # 让配置里的 "\n" 等转义真正变成换行符（与 RAGFlow 一致）
        delimiter = delimiter.encode("utf-8").decode("unicode_escape").encode("latin1").decode("utf-8")

        def add_chunk(t):
            """把一段正文并入当前块；当前块已超预算则新开一块。"""
            nonlocal cks, tk_nums
            tnum = num_tokens_from_string(t)
            if tk_nums[-1] > chunk_token_num:
                cks.append(t)
                tk_nums.append(tnum)
            else:
                # 同一块内用换行拼接，避免两段粘成一句
                if cks[-1]:
                    cks[-1] += "\n" + t
                else:
                    cks[-1] += t
                tk_nums[-1] += tnum

        # --- 解析 delimiter ---
        # 反引号包裹的整段（如 `@@@`）视为「一个」分隔符；其余字符逐个作为分隔符
        dels = []
        s = 0
        for m in re.finditer(r"`([^`]+)`", delimiter, re.I):
            f, t = m.span()
            dels.append(m.group(1))
            dels.extend(list(delimiter[s:f]))
            s = t
        if s < len(delimiter):
            dels.extend(list(delimiter[s:]))

        # 转义后拼成正则「或」；split 时保留分隔符，方便下面过滤掉
        dels = [re.escape(d) for d in dels if d]
        dels = [d for d in dels if d]
        dels = "|".join(dels)
        secs = re.split(r"(%s)" % dels, txt)
        for sec in secs:
            if re.match(f"^{dels}$", sec):
                continue  # 跳过分隔符本身
            add_chunk(sec)

        # 第二项 meta 为空：TXT 无页码/bbox；接口形状与 PDF 等解析器对齐
        return [[c, ""] for c in cks]


def get_text(fnm: str, binary=None) -> str:
    """bytes 或本地路径 → str。

    有 binary 时走解码（对接 loader 的 blob）；否则按路径读文件。
    DEMO 固定 utf-8；RAGFlow 会用 find_codec 探测 GBK 等编码。
    """
    if binary is not None:
        txt = binary.decode("utf-8", errors="ignore")
    else:
        with open(fnm, "r", encoding="utf-8", errors="ignore") as f:
            txt = f.read()

    # 统一换行，避免 Windows \r\n 在预览/切分里显得很乱
    txt = txt.replace("\r\n", "\n").replace("\r", "\n")
    # 压缩过多空行，方便观察切块边界（真正生产可按需保留）
    txt = re.sub(r"\n{3,}", "\n\n", txt)
    return txt


def preview_chunks(chunks, *, limit: int | None = None, max_chars: int = 200) -> None:
    """把切块结果打成可读报告（不要用 !r，否则换行会变成 \\n 看不清）。"""
    total = len(chunks)
    show = chunks if limit is None else chunks[:limit]
    print(f"共 {total} 块" + (f"（只展示前 {len(show)} 块）" if limit else ""))
    print("=" * 60)

    for i, (text, _meta) in enumerate(show):
        body = text.strip()
        first_line = body.split("\n", 1)[0] if body else "(空块)"
        tokens = num_tokens_from_string(text)
        print(f"── chunk[{i}]  chars={len(text)}  ~tokens={tokens}")
        print(f"首行: {first_line[:80]}")
        print("内容预览:")
        preview = body.replace("\n", "\n  ")
        if len(preview) > max_chars:
            preview = preview[:max_chars] + "\n  ...[截断]"
        print(f"  {preview}")
        print("-" * 60)


if __name__ == "__main__":
    import os

    # 有 sample 目录就读真实文件；否则用内联字符串测 parser_txt
    demo_path = os.path.join(os.path.dirname(__file__), "..", "data", "sample")
    if os.path.isdir(demo_path):
        for name in sorted(os.listdir(demo_path)):
            if not name.endswith((".txt", ".md")):
                continue
            path = os.path.join(demo_path, name)
            blob = open(path, "rb").read()
            # token 预算小一点，方便观察「何时新开一块」
            chunks = TxtParser()(name, binary=blob, chunk_token_num=256)
            print(f"\n文件: {name}")
            # limit=None 打印全部；想少看就改成 limit=5
            preview_chunks(chunks, limit=None, max_chars=240)
            break
    else:
        chunks = TxtParser().parser_txt("第一句。第二句！第三句？", chunk_token_num=8)
        preview_chunks(chunks)

