# RAG_DEMO：外网 Embedding + Ubuntu Milvus 最小 RAG

## IDE「未解析的引用」怎么消除

工程根是整个 **ragflow** 时，顶级包名应是 `RAG_DEMO.demo_rag`，不是单独的 `demo_rag`。

### 推荐写法（PyCharm / Cursor 都能解析）

在 `pipeline.py` 等包内文件用**相对导入**（已改好）：

```python
from . import config
from .loader import load_documents
```

在 `main.py` / 仓库其它位置：

```python
from RAG_DEMO.demo_rag import config
from RAG_DEMO.demo_rag.pipeline import ingest, ask
```

改完后若仍红：点击文件外任意处，或 **File → Synchronize / Invalidate Caches**。

### 仍不行时（二选一）

1. 右键 `RAG_DEMO` → Mark Directory as → **Sources Root**，然后可用 `from demo_rag import ...`
2. 或：`cd RAG_DEMO && pip install -e .`（见下方 pyproject）

## 架构

```text
本地文件 → loader/parse/chunker → 外网 Embedding → Ubuntu Milvus
提问 → 同一 Embedding → Milvus top-k → 外网 Chat → 答案
```

## 运行

```bash
cd RAG_DEMO
pip install -r requirements.txt
cp .env.example .env   # 填 API Key 与 MILVUS_HOST
python main.py ping
python main.py ingest
python main.py ask "你的问题"
```
