# 基于 Qwen 多智能体系统的动态随机地图路径规划算法适配边界发现与科学假设生成系统
# config.py — 全局配置文件

import json as _json
import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PROJECT_ROOT.parent
load_dotenv(PROJECT_ROOT / ".env")


def _configured_path(name: str, default: Path, base: Path = PROJECT_ROOT) -> str:
    """Resolve configurable paths independently of the process working directory."""
    raw = os.getenv(name)
    path = Path(raw).expanduser() if raw else default
    if not path.is_absolute():
        path = base / path
    return str(path.resolve())

# ========== 路径 ==========
ASSETS_DIR = _configured_path("ASSETS_DIR", REPO_ROOT / "assets", REPO_ROOT)
KNOWLEDGE_BASE_DIR = _configured_path("KB_DIR", PROJECT_ROOT / "knowledge_base")
ALGORITHM_PROFILE_PATH = _configured_path(
    "ALGORITHM_PROFILE_PATH", Path(KNOWLEDGE_BASE_DIR) / "algorithm_profile.json"
)
HISTORICAL_RESULTS_PATH = _configured_path(
    "HISTORICAL_RESULTS_PATH", Path(KNOWLEDGE_BASE_DIR) / "historical_results.json"
)
LITERATURE_KB_PATH = _configured_path(
    "LITERATURE_KB_PATH", PROJECT_ROOT / "literature" / "literature_kb.json"
)
DATA_DIR = _configured_path("DATA_DIR", PROJECT_ROOT / "data")
MAPS_DIR = _configured_path("MAPS_DIR", Path(ASSETS_DIR) / "maps", REPO_ROOT)
EXPERIMENTS_DIR = _configured_path("EXPERIMENTS_DIR", Path(DATA_DIR) / "experiments")
LOGS_DIR = _configured_path("LOGS_DIR", Path(DATA_DIR) / "logs")
REPORTS_DIR = _configured_path("REPORTS_DIR", PROJECT_ROOT / "reports" / "generated_reports")

# ========== 环境分级阈值 ==========
OBSTACLE_LOW_THRESHOLD = float(os.getenv("OBSTACLE_LOW_THRESHOLD", "0.20"))
OBSTACLE_MEDIUM_THRESHOLD = float(os.getenv("OBSTACLE_MEDIUM_THRESHOLD", "0.50"))

# ========== 算力限制等级 ==========
COMPUTE_LIMITS = ["low", "medium", "high"]  # 算力等级枚举（取值范围：low/medium/high）

# ========== 允许的算法集合 ==========
ALLOWED_ALGORITHMS = ["A*", "ACO", "PSO", "SA", "混合优化算法"]  # 系统白名单算法集合

# ========== 评分权重 ==========
_weights_env = os.getenv("WEIGHTS_JSON", "")
if _weights_env:
    try:
        WEIGHTS = _json.loads(_weights_env)
        for level in ["低复杂度", "中复杂度", "高复杂度"]:
            WEIGHTS.setdefault(level, {})
    except _json.JSONDecodeError:
        WEIGHTS = {
            "低复杂度": {"time": 0.25, "path_length": 0.20, "success_rate": 0.15, "stability": 0.08, "smoothness": 0.08, "safety_score": 0.08, "expanded_nodes": 0.05, "compute_cost": 0.05, "robustness": 0.06},
            "中复杂度": {"time": 0.18, "path_length": 0.20, "success_rate": 0.20, "stability": 0.08, "smoothness": 0.06, "safety_score": 0.08, "expanded_nodes": 0.05, "compute_cost": 0.05, "robustness": 0.10},
            "高复杂度": {"time": 0.10, "path_length": 0.12, "success_rate": 0.30, "stability": 0.10, "smoothness": 0.05, "safety_score": 0.08, "expanded_nodes": 0.05, "compute_cost": 0.05, "robustness": 0.15},
        }
else:
    WEIGHTS = {
        "低复杂度": {"time": 0.25, "path_length": 0.20, "success_rate": 0.15, "stability": 0.08, "smoothness": 0.08, "safety_score": 0.08, "expanded_nodes": 0.05, "compute_cost": 0.05, "robustness": 0.06},
        "中复杂度": {"time": 0.18, "path_length": 0.20, "success_rate": 0.20, "stability": 0.08, "smoothness": 0.06, "safety_score": 0.08, "expanded_nodes": 0.05, "compute_cost": 0.05, "robustness": 0.10},
        "高复杂度": {"time": 0.10, "path_length": 0.12, "success_rate": 0.30, "stability": 0.10, "smoothness": 0.05, "safety_score": 0.08, "expanded_nodes": 0.05, "compute_cost": 0.05, "robustness": 0.15},
    }

# 算力受限时权重修正（取值范围 ±1.0）
COMPUTE_LIMIT_WEIGHT_ADJUST = {
    "time": +0.15,
    "path_length": -0.05,
    "success_rate": -0.05,
    "expanded_nodes": -0.03,
    "compute_cost": -0.05,
    "smoothness": -0.02,
}

# 评分指标归一化方向配置（取值 'reverse' / 'forward'）
NORMALIZATION_DIRECTION = {
    "time": "reverse",            # 越小越好
    "path_length": "reverse",     # 越小越好
    "success_rate": "forward",    # 越大越好
    "stability": "forward",       # 越大越好
    "smoothness": "reverse",      # 越小越好
    "safety_score": "forward",    # 越大越好
    "expanded_nodes": "reverse",  # 越小越好
    "compute_cost": "reverse",    # 越小越好
    "robustness": "forward",      # 越大越好
}

# 参与评分的指标字段
SCORING_METRIC_KEYS = list(NORMALIZATION_DIRECTION.keys())

# ========== 规则惩罚参数 ==========
PENALTY_HIGH_TIME_THRESHOLD = float(os.getenv("PENALTY_HIGH_TIME_THRESHOLD", "1.5"))
PENALTY_HIGH_TIME_VALUE = float(os.getenv("PENALTY_HIGH_TIME_VALUE", "0.15"))
PENALTY_LOW_SUCCESS_RATE = float(os.getenv("PENALTY_LOW_SUCCESS_RATE", "0.80"))
PENALTY_LOW_SUCCESS_VALUE = float(os.getenv("PENALTY_LOW_SUCCESS_VALUE", "0.20"))
PENALTY_OVERKILL_VALUE = float(os.getenv("PENALTY_OVERKILL_VALUE", "0.10"))
PENALTY_POOR_CONNECTIVITY_SUCCESS = float(os.getenv("PENALTY_POOR_CONNECTIVITY_SUCCESS", "0.85"))
PENALTY_POOR_CONNECTIVITY_VALUE = float(os.getenv("PENALTY_POOR_CONNECTIVITY_VALUE", "0.15"))

POOR_CONNECTIVITY_THRESHOLD = float(os.getenv("POOR_CONNECTIVITY_THRESHOLD", "0.4"))

# ========== 人在回路参数 ==========
SCORE_GAP_THRESHOLD = float(os.getenv("SCORE_GAP_THRESHOLD", "0.05"))

# ========== LLM 配置 ==========
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "qwen")

DEEPSEEK_API_BASE_URL = os.getenv("DEEPSEEK_API_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL_NAME = os.getenv("DEEPSEEK_MODEL_NAME", "deepseek-chat")

QWEN_API_BASE_URL = os.getenv("QWEN_API_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
QWEN_MODEL_NAME = os.getenv("QWEN_MODEL_NAME", "qwen-plus")

OPENAI_API_BASE_URL = os.getenv("OPENAI_API_BASE_URL", "https://api.openai.com/v1")
OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "gpt-4o")

# ========== 地图默认参数 ==========
DEFAULT_MAP_WIDTH = 100   # 默认地图宽度（单位：网格格数）
DEFAULT_MAP_HEIGHT = 100  # 默认地图高度（单位：网格格数）
DEFAULT_START_POINT = [0, 0]    # 默认起点坐标（取值范围 0-地图尺寸）
DEFAULT_TARGET_POINT = [99, 99]  # 默认终点坐标（取值范围 0-地图尺寸）

# ========== 日志配置 ==========
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = _configured_path("LOG_FILE", Path(LOGS_DIR) / "system.log")
