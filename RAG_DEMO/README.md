# RAG_DEMO：4 小时最小 RAG 学习骨架

本目录只提供**文件结构与学习目标**，不含实现代码。你按下面顺序把每个文件填满，即可跑通一个简易 RAG。

## 学习目标（完成后应能回答）

1. 文档如何变成可检索的 chunk？
2. 用户问题如何匹配到相关片段？
3. 答案错误时，如何区分是切分 / 检索 / 生成问题？
4. `chunk_size`、`top_k`、prompt 分别影响什么？
5. 如何用 10 道题判断系统有没有变好？

## 目录结构

```text
RAG_DEMO/
├── README.md                 # 本说明
├── requirements.txt          # 依赖清单（自行安装）
├── .env.example              # API Key / 模型配置示例
├── config.py                 # 全局配置（路径、chunk、top_k）
├── main.py                   # CLI 入口：ingest / ask / eval
├── data/
│   └── sample/               # 放入你自己的 .md / .txt 文档
├── eval/
│   ├── questions.json        # 10 道测试题模板
│   └── runner.py             # 跑评测、打印命中与幻觉观察
└── rag/
    ├── loader.py             # 读取 data/ 下文档
    ├── chunker.py            # 文本切分
    ├── embedder.py           # 文本 -> 向量
    ├── store.py              # 向量入库 / 相似度检索
    ├── retriever.py          # 按 query 取 top-k chunk
    ├── generator.py          # 拼 prompt，调用 LLM
    └── pipeline.py           # 串联 ingest 与 ask 全链路
```

## 建议填写顺序（约 4 小时）

| 顺序 | 文件 | 时间 | 验收标准 |
|------|------|------|----------|
| 1 | `config.py` + `.env` | 15 min | 能读到模型与路径配置 |
| 2 | `rag/loader.py` | 20 min | 能打印文档路径与字数 |
| 3 | `rag/chunker.py` | 30 min | 同一文档可输出不同 chunk_size 的片段列表 |
| 4 | `rag/embedder.py` + `store.py` | 40 min | 能对 chunk 建索引并按向量相似度搜 |
| 5 | `rag/retriever.py` | 20 min | 给定问题能打印 top-k 原文 |
| 6 | `rag/generator.py` | 30 min | 能基于上下文生成带“引用/不知道”约束的答案 |
| 7 | `rag/pipeline.py` + `main.py` | 30 min | `ingest` 与 `ask` 可端到端跑通 |
| 8 | `eval/questions.json` + `runner.py` | 35 min | 10 题手工判分，记录检索是否命中 |

## 最小命令形态（实现后）

```bash
cd RAG_DEMO
pip install -r requirements.txt
cp .env.example .env   # 填入你的 API Key

python main.py ingest
python main.py ask "这段文档主要讲什么？"
python main.py eval
```

## 调试习惯（比写代码更重要）

每次答错，按这个顺序查：

```text
1. 检索到的 top-k 原文里有没有正确答案？
2. 没有 → 查切分 / embedding / top_k
3. 有 → 查 prompt / 上下文组装 / 模型生成
```

## 刻意不做的事

- 不引入 LangChain / LlamaIndex 全栈框架（先手写链路）
- 不对接 RAGFlow 服务（学完再对照源码）
- 不追求 PDF 复杂解析（先用 `.md` / `.txt`）
