"""全局配置：路径、切分参数、检索参数、模型名。

学习点：
- 把可变参数集中在一处，方便做 A/B 实验（只改一个变量）。
"""

from pathlib import Path

# TODO: 从环境变量 / .env 加载 API_KEY、BASE_URL、模型名
# TODO: 定义 PROJECT_ROOT、DATA_DIR、INDEX_DIR
# TODO: 定义 CHUNK_SIZE、CHUNK_OVERLAP、TOP_K

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data" / "sample"
INDEX_DIR = PROJECT_ROOT / ".index"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
TOP_K = 4

EMBEDDING_MODEL = ""
CHAT_MODEL = ""
