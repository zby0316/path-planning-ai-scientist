# 基础版 MVP 全流程搭建执行方案

---

## 一、基础版系统目标与范围

### 1.1 核心目标

构建一个**可运行的多智能体路径规划算法自适应选型 AI Scientist 系统**基础版，实现从"环境输入 → 复杂度分级 → 知识库检索 → 算法评分 → 最优输出"的完整决策流程。

**系统输出格式（三行核心结果）：**

```text
当前场景等级：高复杂度
选定最优算法名称：混合优化算法
简短选型依据：当前障碍物占比为62%，属于高复杂度场景；历史知识库显示混合优化算法在该类场景下成功率最高，虽然耗时较长，但当前算力允许，因此优先选择成功率更高的混合优化算法。
```

### 1.2 算法集合（严格限定）

```python
ALLOWED_ALGORITHMS = ["A*", "ACO", "PSO", "SA", "混合优化算法"]
```

### 1.3 环境复杂度三级划分

| 等级 | 障碍物占比 | A* 倾向 | 群智能倾向 |
|------|-----------|---------|------------|
| 低复杂度 | < 20% | 高（优先速度） | 需证明收益 |
| 中复杂度 | 20% ~ 50% | 中（看场景） | 平衡各项 |
| 高复杂度 | > 50% | 低（可能降权） | 优先成功率 |

### 1.4 7 步 MVP 路线图

```text
┌──────────────────────────────────────────────────────────────────┐
│  Step 1 → Step 2 → Step 3 → Step 4 → Step 5 → Step 6 → Step 7   │
│ 地图输入   知识库    评分选型   算法实现   实验对比   Qwen接入   GUI  │
│ 环境分级   建立      决策输出   地图生成   性能统计   解释生成   展示  │
└──────────────────────────────────────────────────────────────────┘
```

### 1.5 技术栈（基础版）

| 层面 | 技术选型 |
|------|----------|
| 语言 | Python 3.9+ |
| 智能体调度 | 纯 Python 类（自研轻量编排） |
| 数据库 | JSON 文件（知识库）/ SQLite（历史数据） |
| 大模型 | Qwen API（阿里云百炼平台） |
| 前端 | Streamlit |
| 可视化 | Matplotlib + Plotly |
| 算法 | NumPy + SciPy + NetworkX |

---

## 二、项目目录结构与文件清单

### 2.1 完整目录树

```text
ai_scientist_path_planning/
│
├── main.py                          # 主入口，串联全流程
├── config.py                        # 全局配置（路径、阈值、权重）
├── requirements.txt                 # Python 依赖清单
├── .env.example                     # 环境变量模板（Qwen API Key）
│
├── agents/                          # 多智能体模块
│   ├── __init__.py
│   ├── orchestrator_agent.py        # 总控调度智能体 ★
│   ├── data_agent.py                # 数据接收与校验智能体
│   ├── environment_agent.py         # 环境分析智能体
│   ├── knowledge_agent.py           # 知识库检索智能体
│   ├── rule_agent.py                # 规则约束智能体
│   ├── evaluation_agent.py          # 算法评估智能体
│   ├── decision_agent.py            # 决策生成智能体
│   ├── explanation_agent.py         # 解释生成智能体
│   ├── human_loop_agent.py          # 人在回路智能体
│   └── hypothesis_agent.py          # 科学假设生成智能体
│
├── algorithms/                      # 路径规划算法实现
│   ├── __init__.py
│   ├── astar.py                     # A* 算法
│   ├── aco.py                       # 蚁群算法
│   ├── pso.py                       # 粒子群算法
│   ├── sa.py                        # 模拟退火算法
│   └── hybrid.py                    # 混合优化算法（A* + 局部优化）
│
├── map/                             # 地图模块
│   ├── __init__.py
│   ├── map_generator.py             # 随机栅格地图生成器
│   └── connectivity_checker.py      # 连通性检查（BFS/DFS）
│
├── evaluation/                      # 评估模块
│   ├── __init__.py
│   ├── metrics.py                   # 指标计算（耗时/路径/成功率/稳定性）
│   ├── scoring.py                   # 加权评分函数
│   └── benchmark.py                 # 批量对比实验运行器
│
├── knowledge_base/                  # 知识库数据
│   ├── algorithm_profile.json       # 算法特性知识库
│   └── historical_results.json      # 历史性能数据（15条模拟数据）
│
├── llm/                             # 大模型接入
│   ├── __init__.py
│   ├── qwen_client.py               # Qwen API 客户端
│   └── prompt_templates.py          # Prompt 模板库
│
├── gui/                             # 可视化界面
│   ├── __init__.py
│   ├── streamlit_app.py             # Streamlit 主页面
│   └── visualization.py             # 图表绘制工具
│
├── data/                            # 运行时数据
│   ├── maps/                        # 生成的地图文件
│   ├── experiments/                 # 实验结果
│   └── logs/                        # 运行日志
│
├── reports/                         # 报告输出
│   └── generated_reports/           # 自动生成的报告
│
└── tests/                           # 单元测试
    ├── __init__.py
    ├── test_environment_agent.py
    ├── test_decision_agent.py
    ├── test_astar.py
    ├── test_map_generator.py
    ├── test_scoring.py
    └── test_integration.py          # 端到端集成测试
```

### 2.2 各文件职责速查表

| 文件路径 | 职责 |
|----------|------|
| `main.py` | 系统入口，串联完整决策流程，支持命令行与模块调用两种模式 |
| `config.py` | 集中管理所有可配置参数（权重、阈值、路径、API设置） |
| `agents/orchestrator_agent.py` | 总控调度，管理智能体执行顺序与数据传递 |
| `agents/data_agent.py` | 校验输入字段完整性与合法性 |
| `agents/environment_agent.py` | 按障碍物占比进行三级分级，计算综合复杂度指数 |
| `agents/knowledge_agent.py` | 读取 JSON 知识库，按场景等级筛选算法记录 |
| `agents/rule_agent.py` | 根据算力限制、连通性等规则对算法施加惩罚项 |
| `agents/evaluation_agent.py` | 归一化 + 加权评分，输出排序后的算法列表 |
| `agents/decision_agent.py` | 选择得分最高算法，输出标准化三行结果 |
| `agents/explanation_agent.py` | 调用 Qwen 生成可解释的选型依据文本 |
| `agents/human_loop_agent.py` | 检测分数接近等异常情况，触发人工校验提示 |
| `agents/hypothesis_agent.py` | 调用 Qwen 生成可验证科学假设与研究计划 |
| `algorithms/astar.py` | A* 搜索（曼哈顿距离启发函数，优先队列实现） |
| `algorithms/aco.py` | 蚁群算法（信息素矩阵、概率选择、挥发更新） |
| `algorithms/pso.py` | 粒子群算法（栅格编码、速度位置更新、惯性权重） |
| `algorithms/sa.py` | 模拟退火（指数降温、邻域搜索、Metropolis准则） |
| `algorithms/hybrid.py` | A* 生成初始路径 + 局部搜索优化 |
| `map/map_generator.py` | 按障碍物占比生成随机栅格地图 |
| `map/connectivity_checker.py` | BFS/DFS 检查起点终点连通性 |
| `evaluation/metrics.py` | 单次运行指标提取 |
| `evaluation/scoring.py` | 多指标归一化与加权综合评分 |
| `evaluation/benchmark.py` | 同一地图批量运行5种算法并对比 |
| `llm/qwen_client.py` | Qwen API 的封装调用（HTTP请求 + 重试 + 错误处理） |
| `llm/prompt_templates.py` | 集中管理所有 Prompt 模板字符串 |
| `gui/streamlit_app.py` | 浏览器交互界面 |
| `gui/visualization.py` | 地图渲染、对比图表、雷达图等 |
| `tests/*` | 各模块单元测试与端到端集成测试 |

---

## 三、阶段一：核心决策引擎（Step 1 ~ 3）

> **里程碑验证**：输入一组地图参数 → 系统输出三行决策结果，无需真实算法运行。

### Step 1 — 地图输入与环境分级

#### 1.1 创建项目骨架

按上述目录树创建所有空白文件夹和 `__init__.py` 文件。执行命令：

```bash
mkdir -p ai_scientist_path_planning/{agents,algorithms,map,evaluation,knowledge_base,llm,gui,data/{maps,experiments,logs},reports/generated_reports,tests}
```

#### 1.2 创建 `config.py`

```python
# config.py — 全局配置文件

# ========== 路径 ==========
KNOWLEDGE_BASE_DIR = "knowledge_base"
ALGORITHM_PROFILE_PATH = f"{KNOWLEDGE_BASE_DIR}/algorithm_profile.json"
HISTORICAL_RESULTS_PATH = f"{KNOWLEDGE_BASE_DIR}/historical_results.json"
DATA_DIR = "data"
MAPS_DIR = f"{DATA_DIR}/maps"
EXPERIMENTS_DIR = f"{DATA_DIR}/experiments"
LOGS_DIR = f"{DATA_DIR}/logs"
REPORTS_DIR = "reports/generated_reports"

# ========== 环境分级阈值 ==========
OBSTACLE_LOW_THRESHOLD = 0.20
OBSTACLE_MEDIUM_THRESHOLD = 0.50

# ========== 算力限制等级 ==========
COMPUTE_LIMITS = ["low", "medium", "high"]

# ========== 允许的算法集合 ==========
ALLOWED_ALGORITHMS = ["A*", "ACO", "PSO", "SA", "混合优化算法"]

# ========== 评分权重 ==========
WEIGHTS = {
    "低复杂度": {"time": 0.45, "path_length": 0.30, "success_rate": 0.15, "stability": 0.10},
    "中复杂度": {"time": 0.25, "path_length": 0.30, "success_rate": 0.30, "stability": 0.15},
    "高复杂度": {"time": 0.15, "path_length": 0.20, "success_rate": 0.50, "stability": 0.15},
}

# 算力受限时权重修正
COMPUTE_LIMIT_WEIGHT_ADJUST = {"time": +0.20, "path_length": -0.10, "success_rate": -0.10}

# ========== 规则惩罚参数 ==========
PENALTY_HIGH_TIME_THRESHOLD = 1.5    # 算力受限时，耗时超过此值（秒）触发惩罚
PENALTY_HIGH_TIME_VALUE = 0.15
PENALTY_LOW_SUCCESS_RATE = 0.80      # 高复杂度下成功率低于此值触发惩罚
PENALTY_LOW_SUCCESS_VALUE = 0.20
PENALTY_OVERKILL_VALUE = 0.10        # 低复杂度下使用混合优化算法的惩罚
PENALTY_POOR_CONNECTIVITY_SUCCESS = 0.85
PENALTY_POOR_CONNECTIVITY_VALUE = 0.15

# 连通性差阈值
POOR_CONNECTIVITY_THRESHOLD = 0.4

# ========== 人在回路参数 ==========
SCORE_GAP_THRESHOLD = 0.05  # 前两名评分差距小于此值触发人工校验

# ========== Qwen API 配置 ==========
QWEN_API_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
QWEN_MODEL_NAME = "qwen-plus"
# API Key 从环境变量 QWEN_API_KEY 读取，不写在代码中

# ========== 地图默认参数 ==========
DEFAULT_MAP_WIDTH = 100
DEFAULT_MAP_HEIGHT = 100
DEFAULT_START_POINT = [0, 0]
DEFAULT_TARGET_POINT = [99, 99]
```

**创建操作清单：**

| 序号 | 操作 | 文件 |
|------|------|------|
| 1 | 创建项目根目录及所有子目录 | `/ai_scientist_path_planning/` |
| 2 | 创建各包的 `__init__.py` | `agents/`, `algorithms/`, `map/`, `evaluation/`, `llm/`, `gui/`, `tests/` |
| 3 | 创建配置文件 | `config.py` |
| 4 | 创建 `.env.example` | 填入 `QWEN_API_KEY=your_api_key_here` |

#### 1.3 创建 `agents/data_agent.py`

```python
# agents/data_agent.py — 数据接收与校验智能体

from config import COMPUTE_LIMITS


class DataReceiverAgent:
    """校验输入数据完整性与合法性"""

    REQUIRED_FIELDS = [
        "obstacle_ratio", "map_width", "map_height",
        "connectivity", "topology_randomness", "compute_limit"
    ]

    def validate(self, env: dict) -> dict:
        for field in self.REQUIRED_FIELDS:
            if field not in env:
                raise ValueError(f"缺少必要字段: {field}")

        if not (0 <= env["obstacle_ratio"] <= 1):
            raise ValueError("obstacle_ratio 必须在 0 到 1 之间")
        if not (0 <= env.get("connectivity", 0) <= 1):
            raise ValueError("connectivity 必须在 0 到 1 之间")
        if not (0 <= env.get("topology_randomness", 0) <= 1):
            raise ValueError("topology_randomness 必须在 0 到 1 之间")
        if env["compute_limit"] not in COMPUTE_LIMITS:
            raise ValueError(f"compute_limit 必须为 {COMPUTE_LIMITS}")
        if env["map_width"] <= 0 or env["map_height"] <= 0:
            raise ValueError("地图尺寸必须大于 0")

        return env
```

#### 1.4 创建 `agents/environment_agent.py`

```python
# agents/environment_agent.py — 环境复杂度分析智能体

from config import OBSTACLE_LOW_THRESHOLD, OBSTACLE_MEDIUM_THRESHOLD


class EnvironmentAgent:
    """将地图特征分为低/中/高三个复杂度等级"""

    def classify(self, env: dict) -> dict:
        obstacle_ratio = env["obstacle_ratio"]

        if obstacle_ratio < OBSTACLE_LOW_THRESHOLD:
            scene_level = "低复杂度"
        elif obstacle_ratio <= OBSTACLE_MEDIUM_THRESHOLD:
            scene_level = "中复杂度"
        else:
            scene_level = "高复杂度"

        complexity_index = (
            0.45 * obstacle_ratio +
            0.25 * (1 - env.get("connectivity", 0)) +
            0.20 * env.get("topology_randomness", 0) +
            0.10 * env.get("dynamic_change_rate", 0)
        )

        env["scene_level"] = scene_level
        env["complexity_index"] = round(complexity_index, 4)
        return env
```

---

### Step 2 — 建立算法知识库

#### 2.1 创建 `knowledge_base/algorithm_profile.json`

```json
{
  "A*": {
    "advantages": ["速度快", "确定性强", "低复杂度场景路径质量高"],
    "disadvantages": ["高障碍物环境下搜索空间膨胀", "动态环境下重规划开销较大"],
    "suitable_scene": ["低复杂度", "连通性好", "算力受限"],
    "unsuitable_scene": ["高障碍物密集区域", "动态障碍频繁环境"]
  },
  "ACO": {
    "advantages": ["全局搜索能力较强", "适合复杂路径搜索"],
    "disadvantages": ["收敛速度较慢", "参数敏感"],
    "suitable_scene": ["中复杂度", "高复杂度", "多路径候选"],
    "unsuitable_scene": ["对实时性要求极高的场景"]
  },
  "PSO": {
    "advantages": ["适合连续空间优化", "全局搜索能力较好"],
    "disadvantages": ["离散栅格地图中需要编码转换", "可能早熟收敛"],
    "suitable_scene": ["中复杂度", "连续空间路径优化"],
    "unsuitable_scene": ["严格实时性要求", "高离散度地图"]
  },
  "SA": {
    "advantages": ["可跳出局部最优", "实现简单"],
    "disadvantages": ["收敛速度和退火参数相关", "高复杂度下稳定性不足"],
    "suitable_scene": ["中复杂度", "局部路径优化"],
    "unsuitable_scene": ["高复杂度大规模地图", "严格时间约束"]
  },
  "混合优化算法": {
    "advantages": ["兼顾全局搜索和局部优化", "高复杂度场景成功率较高"],
    "disadvantages": ["计算成本较高", "系统复杂度较高"],
    "suitable_scene": ["高复杂度", "动态障碍", "随机拓扑强"],
    "unsuitable_scene": ["算力严重受限", "简单低障碍场景"]
  }
}
```

#### 2.2 创建 `knowledge_base/historical_results.json`

5 种算法 × 3 个复杂度等级 = 15 条模拟性能数据。

```json
[
  {
    "algorithm": "A*",
    "scene_level": "低复杂度",
    "avg_time": 0.12,
    "avg_path_length": 108.0,
    "success_rate": 0.98,
    "stability_score": 0.95
  },
  {
    "algorithm": "ACO",
    "scene_level": "低复杂度",
    "avg_time": 1.20,
    "avg_path_length": 112.0,
    "success_rate": 0.96,
    "stability_score": 0.90
  },
  {
    "algorithm": "PSO",
    "scene_level": "低复杂度",
    "avg_time": 1.10,
    "avg_path_length": 116.0,
    "success_rate": 0.92,
    "stability_score": 0.86
  },
  {
    "algorithm": "SA",
    "scene_level": "低复杂度",
    "avg_time": 0.90,
    "avg_path_length": 118.0,
    "success_rate": 0.90,
    "stability_score": 0.84
  },
  {
    "algorithm": "混合优化算法",
    "scene_level": "低复杂度",
    "avg_time": 1.80,
    "avg_path_length": 109.0,
    "success_rate": 0.97,
    "stability_score": 0.93
  },
  {
    "algorithm": "A*",
    "scene_level": "中复杂度",
    "avg_time": 0.75,
    "avg_path_length": 142.0,
    "success_rate": 0.82,
    "stability_score": 0.80
  },
  {
    "algorithm": "ACO",
    "scene_level": "中复杂度",
    "avg_time": 1.80,
    "avg_path_length": 130.0,
    "success_rate": 0.91,
    "stability_score": 0.87
  },
  {
    "algorithm": "PSO",
    "scene_level": "中复杂度",
    "avg_time": 1.50,
    "avg_path_length": 136.0,
    "success_rate": 0.87,
    "stability_score": 0.84
  },
  {
    "algorithm": "SA",
    "scene_level": "中复杂度",
    "avg_time": 1.20,
    "avg_path_length": 139.0,
    "success_rate": 0.84,
    "stability_score": 0.81
  },
  {
    "algorithm": "混合优化算法",
    "scene_level": "中复杂度",
    "avg_time": 2.20,
    "avg_path_length": 128.0,
    "success_rate": 0.93,
    "stability_score": 0.90
  },
  {
    "algorithm": "A*",
    "scene_level": "高复杂度",
    "avg_time": 2.40,
    "avg_path_length": 190.0,
    "success_rate": 0.55,
    "stability_score": 0.60
  },
  {
    "algorithm": "ACO",
    "scene_level": "高复杂度",
    "avg_time": 2.60,
    "avg_path_length": 158.0,
    "success_rate": 0.88,
    "stability_score": 0.86
  },
  {
    "algorithm": "PSO",
    "scene_level": "高复杂度",
    "avg_time": 2.20,
    "avg_path_length": 170.0,
    "success_rate": 0.78,
    "stability_score": 0.76
  },
  {
    "algorithm": "SA",
    "scene_level": "高复杂度",
    "avg_time": 1.90,
    "avg_path_length": 176.0,
    "success_rate": 0.72,
    "stability_score": 0.73
  },
  {
    "algorithm": "混合优化算法",
    "scene_level": "高复杂度",
    "avg_time": 3.00,
    "avg_path_length": 152.0,
    "success_rate": 0.94,
    "stability_score": 0.91
  }
]
```

#### 2.3 创建 `agents/knowledge_agent.py`

```python
# agents/knowledge_agent.py — 知识库检索智能体

import json
from config import HISTORICAL_RESULTS_PATH, ALLOWED_ALGORITHMS


class KnowledgeRetrievalAgent:
    """从历史性能数据库中检索匹配场景等级的算法记录"""

    def __init__(self):
        with open(HISTORICAL_RESULTS_PATH, "r", encoding="utf-8") as f:
            self.performance_db = json.load(f)

    def retrieve(self, scene_level: str) -> list[dict]:
        return [
            record for record in self.performance_db
            if record["scene_level"] == scene_level
            and record["algorithm"] in ALLOWED_ALGORITHMS
        ]
```

**创建操作清单：**

| 序号 | 操作 | 文件 |
|------|------|------|
| 1 | 创建算法特性知识库 | `knowledge_base/algorithm_profile.json` |
| 2 | 创建15条历史模拟性能数据 | `knowledge_base/historical_results.json` |
| 3 | 创建知识库检索智能体 | `agents/knowledge_agent.py` |

---

### Step 3 — 算法评分与选型

#### 3.1 创建 `agents/rule_agent.py`

```python
# agents/rule_agent.py — 规则约束智能体

from config import (
    PENALTY_HIGH_TIME_THRESHOLD, PENALTY_HIGH_TIME_VALUE,
    PENALTY_LOW_SUCCESS_RATE, PENALTY_LOW_SUCCESS_VALUE,
    PENALTY_OVERKILL_VALUE, PENALTY_POOR_CONNECTIVITY_SUCCESS,
    PENALTY_POOR_CONNECTIVITY_VALUE, POOR_CONNECTIVITY_THRESHOLD,
)


class RuleConstraintAgent:
    """根据硬性规则对候选算法施加惩罚项"""

    def filter_and_penalize(self, env: dict, records: list[dict]) -> list[dict]:
        processed = []
        for record in records:
            penalty = 0.0
            algorithm = record["algorithm"]

            # 规则1：算力受限时惩罚高耗时算法
            if env["compute_limit"] == "low" and record["avg_time"] > PENALTY_HIGH_TIME_THRESHOLD:
                penalty += PENALTY_HIGH_TIME_VALUE

            # 规则2：高复杂度场景惩罚低成功率算法
            if env["scene_level"] == "高复杂度" and record["success_rate"] < PENALTY_LOW_SUCCESS_RATE:
                penalty += PENALTY_LOW_SUCCESS_VALUE

            # 规则3：低复杂度场景中使用过度复杂算法轻微惩罚
            if env["scene_level"] == "低复杂度" and algorithm == "混合优化算法":
                penalty += PENALTY_OVERKILL_VALUE

            # 规则4：连通性差时惩罚成功率较低算法
            if env.get("connectivity", 1.0) < POOR_CONNECTIVITY_THRESHOLD and \
               record["success_rate"] < PENALTY_POOR_CONNECTIVITY_SUCCESS:
                penalty += PENALTY_POOR_CONNECTIVITY_VALUE

            record = record.copy()
            record["penalty"] = penalty
            processed.append(record)

        return processed
```

#### 3.2 创建 `agents/evaluation_agent.py`

```python
# agents/evaluation_agent.py — 算法评估智能体

from config import WEIGHTS, COMPUTE_LIMIT_WEIGHT_ADJUST


class AlgorithmEvaluationAgent:
    """归一化 + 加权评分，输出排序后的算法列表"""

    def get_weights(self, env: dict) -> dict:
        weights = WEIGHTS[env["scene_level"]].copy()

        if env["compute_limit"] == "low":
            for key, adj in COMPUTE_LIMIT_WEIGHT_ADJUST.items():
                weights[key] = weights.get(key, 0) + adj

        return weights

    def _normalize_reverse(self, value: float, min_value: float, max_value: float) -> float:
        """逆向归一化：值越小得分越高（用于耗时、路径长度）"""
        if max_value == min_value:
            return 1.0
        return 1.0 - (value - min_value) / (max_value - min_value)

    def score(self, env: dict, records: list[dict]) -> list[dict]:
        weights = self.get_weights(env)

        times = [r["avg_time"] for r in records]
        lengths = [r["avg_path_length"] for r in records]
        min_time, max_time = min(times), max(times)
        min_length, max_length = min(lengths), max(lengths)

        scored = []
        for record in records:
            time_score = self._normalize_reverse(record["avg_time"], min_time, max_time)
            length_score = self._normalize_reverse(record["avg_path_length"], min_length, max_length)
            success_score = record["success_rate"]
            stability_score = record["stability_score"]

            final_score = (
                weights["time"] * time_score +
                weights["path_length"] * length_score +
                weights["success_rate"] * success_score +
                weights["stability"] * stability_score -
                record.get("penalty", 0)
            )

            record = record.copy()
            record["score"] = round(final_score, 4)
            record["detail"] = {
                "time_score": round(time_score, 4),
                "length_score": round(length_score, 4),
                "success_score": round(success_score, 4),
                "stability_score": round(stability_score, 4),
                "penalty": record.get("penalty", 0),
            }
            scored.append(record)

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored
```

#### 3.3 创建 `agents/decision_agent.py`

```python
# agents/decision_agent.py — 决策生成智能体

from config import ALLOWED_ALGORITHMS


class DecisionAgent:
    """选择得分最高的算法，生成标准化决策结果"""

    def select_best(self, env: dict, scored_records: list[dict]) -> dict:
        if not scored_records:
            raise ValueError("没有可用算法候选，请检查知识库数据")

        best = scored_records[0]

        if best["algorithm"] not in ALLOWED_ALGORITHMS:
            raise ValueError(f"非法算法 '{best['algorithm']}'，只允许从 {ALLOWED_ALGORITHMS} 中选择")

        return {
            "scene_level": env["scene_level"],
            "best_algorithm": best["algorithm"],
            "best_score": best["score"],
            "ranking": scored_records,
        }
```

#### 3.4 创建 `main.py` — 阶段一集成验证

```python
# main.py — Phase 1 验证：纯决策流程

from agents.data_agent import DataReceiverAgent
from agents.environment_agent import EnvironmentAgent
from agents.knowledge_agent import KnowledgeRetrievalAgent
from agents.rule_agent import RuleConstraintAgent
from agents.evaluation_agent import AlgorithmEvaluationAgent
from agents.decision_agent import DecisionAgent


class PathPlanningDecisionSystem:
    """路径规划算法自适应选型系统——核心决策引擎"""

    def __init__(self):
        self.data_agent = DataReceiverAgent()
        self.env_agent = EnvironmentAgent()
        self.knowledge_agent = KnowledgeRetrievalAgent()
        self.rule_agent = RuleConstraintAgent()
        self.eval_agent = AlgorithmEvaluationAgent()
        self.decision_agent = DecisionAgent()

    def decide(self, env_input: dict) -> dict:
        """执行完整决策流程，返回决策结果"""
        env = self.data_agent.validate(env_input)
        env = self.env_agent.classify(env)
        records = self.knowledge_agent.retrieve(env["scene_level"])
        records = self.rule_agent.filter_and_penalize(env, records)
        scored = self.eval_agent.score(env, records)
        decision = self.decision_agent.select_best(env, scored)
        return decision


def main():
    """Phase 1 验证：使用三组测试数据验证决策输出"""
    test_cases = [
        {
            "name": "低复杂度场景",
            "input": {
                "obstacle_ratio": 0.10,
                "map_width": 100, "map_height": 100,
                "connectivity": 0.90,
                "topology_randomness": 0.20,
                "compute_limit": "high",
            },
        },
        {
            "name": "中复杂度场景",
            "input": {
                "obstacle_ratio": 0.35,
                "map_width": 100, "map_height": 100,
                "connectivity": 0.68,
                "topology_randomness": 0.55,
                "compute_limit": "medium",
            },
        },
        {
            "name": "高复杂度场景（算力充足）",
            "input": {
                "obstacle_ratio": 0.62,
                "map_width": 100, "map_height": 100,
                "connectivity": 0.36,
                "topology_randomness": 0.72,
                "compute_limit": "high",
            },
        },
    ]

    system = PathPlanningDecisionSystem()

    for case in test_cases:
        decision = system.decide(case["input"])
        ranking = decision["ranking"]

        print(f"\n{'='*60}")
        print(f"  {case['name']}")
        print(f"{'='*60}")
        print(f"当前场景等级：{decision['scene_level']}")
        print(f"选定最优算法名称：{decision['best_algorithm']}")
        print(f"综合得分：{decision['best_score']}")
        print(f"\n排名详情：")
        for i, r in enumerate(ranking, 1):
            bar = "█" * int(r["score"] * 20)
            print(f"  {i}. {r['algorithm']:<6}  得分={r['score']:.4f}  {bar}")
            d = r["detail"]
            print(f"     耗时={d['time_score']:.3f}  路径={d['length_score']:.3f}  "
                  f"成功率={d['success_score']:.3f}  稳定性={d['stability_score']:.3f}  "
                  f"惩罚={d['penalty']:.3f}")


if __name__ == "__main__":
    main()
```

**集成验证命令：**

```bash
cd ai_scientist_path_planning
python main.py
```

**预期输出：**
- 低复杂度场景 → A* 得分最高
- 中复杂度场景 → ACO 或混合优化算法得分较高
- 高复杂度场景 → 混合优化算法得分最高，A* 可能因低成功率被惩罚

---

## 四、阶段二：路径规划算法实现（Step 4 ~ 5）

> **里程碑验证**：生成随机地图 → 分别运行5种算法 → 输出对比表与推荐算法。

### Step 4 — 实现五种路径规划算法

#### 4.1 创建 `map/map_generator.py`

```python
# map/map_generator.py — 随机栅格地图生成器

import numpy as np


class MapGenerator:
    """生成指定尺寸和障碍物占比的二维栅格地图

    0 = 可通行, 1 = 障碍物
    """

    def __init__(self, seed: int = None):
        self.rng = np.random.RandomState(seed)

    def generate(
        self,
        width: int,
        height: int,
        obstacle_ratio: float,
        start: tuple = None,
        target: tuple = None,
    ) -> np.ndarray:
        grid = np.zeros((height, width), dtype=np.int8)

        total_cells = width * height
        obstacle_count = int(total_cells * obstacle_ratio)

        all_indices = list(range(total_cells))

        # 保留起点和终点为空
        reserved = set()
        if start:
            reserved.add(start[1] * width + start[0])
        if target:
            reserved.add(target[1] * width + target[0])

        available = [i for i in all_indices if i not in reserved]
        chosen = self.rng.choice(available, size=min(obstacle_count, len(available)), replace=False)

        for idx in chosen:
            row, col = divmod(idx, width)
            grid[row, col] = 1

        return grid
```

#### 4.2 创建 `map/connectivity_checker.py`

```python
# map/connectivity_checker.py — 连通性检查

from collections import deque
import numpy as np


class ConnectivityChecker:
    """使用 BFS 检查起点到终点的连通性"""

    def is_reachable(
        self,
        grid: np.ndarray,
        start: tuple,
        target: tuple,
    ) -> bool:
        h, w = grid.shape
        visited = np.zeros_like(grid, dtype=bool)
        queue = deque([start])
        visited[start[1], start[0]] = True

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        while queue:
            x, y = queue.popleft()
            if (x, y) == target:
                return True

            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h:
                    if not visited[ny, nx] and grid[ny, nx] == 0:
                        visited[ny, nx] = True
                        queue.append((nx, ny))

        return False
```

#### 4.3 创建 `algorithms/astar.py`

```python
# algorithms/astar.py — A* 算法

import heapq
import numpy as np


class AStar:
    """A* 路径搜索（曼哈顿距离启发函数）"""

    def search(self, grid: np.ndarray, start: tuple, target: tuple) -> dict:
        h, w = grid.shape
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}
        nodes_expanded = 0

        while open_set:
            _, current = heapq.heappop(open_set)
            nodes_expanded += 1

            if current == target:
                path = self._reconstruct_path(came_from, current)
                return {
                    "success": True,
                    "path": path,
                    "path_length": len(path),
                    "nodes_expanded": nodes_expanded,
                }

            for dx, dy in directions:
                nx, ny = current[0] + dx, current[1] + dy
                if 0 <= nx < w and 0 <= ny < h and grid[ny, nx] == 0:
                    tentative_g = g_score[current] + 1
                    neighbor = (nx, ny)
                    if tentative_g < g_score.get(neighbor, float("inf")):
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g
                        f_score = tentative_g + heuristic(neighbor, target)
                        heapq.heappush(open_set, (f_score, neighbor))

        return {"success": False, "path": [], "path_length": 0, "nodes_expanded": nodes_expanded}

    def _reconstruct_path(self, came_from: dict, current: tuple) -> list:
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path
```

#### 4.4 创建 `algorithms/aco.py`（蚁群算法）

```python
# algorithms/aco.py — 蚁群算法

import numpy as np


class AntColony:
    """基础蚁群算法路径搜索"""

    def __init__(self):
        self.n_ants = 50
        self.n_iterations = 100
        self.evaporation_rate = 0.1
        self.alpha = 1.0    # 信息素重要程度
        self.beta = 2.0     # 启发式重要程度
        self.q0 = 0.9       # 伪随机比例

    def search(self, grid: np.ndarray, start: tuple, target: tuple) -> dict:
        h, w = grid.shape
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        pheromone = np.ones((h, w)) * 0.1
        best_path = []
        best_length = float("inf")

        for iteration in range(self.n_iterations):
            all_paths = []
            for _ in range(self.n_ants):
                path = self._construct_path(grid, start, target, pheromone, directions)
                if path:
                    all_paths.append(path)
                    if len(path) < best_length:
                        best_length = len(path)
                        best_path = path

            # 信息素挥发
            pheromone *= (1 - self.evaporation_rate)
            # 信息素沉积
            for path in all_paths:
                deposit = 1.0 / len(path)
                for x, y in path:
                    pheromone[y, x] += deposit

        success = len(best_path) > 0
        return {
            "success": success,
            "path": best_path,
            "path_length": len(best_path),
        }

    def _construct_path(self, grid, start, target, pheromone, directions):
        h, w = grid.shape
        current = start
        path = [current]
        visited = set([current])
        steps = 0
        max_steps = w * h * 2

        while current != target and steps < max_steps:
            steps += 1
            x, y = current
            candidates = []
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and grid[ny, nx] == 0 and (nx, ny) not in visited:
                    heuristic = 1.0 / (abs(nx - target[0]) + abs(ny - target[1]) + 1)
                    prob = (pheromone[ny, nx] ** self.alpha) * (heuristic ** self.beta)
                    candidates.append(((nx, ny), prob))

            if not candidates:
                break

            total = sum(p for _, p in candidates)
            probs = [p / total for _, p in candidates]
            chosen_idx = np.random.choice(len(candidates), p=probs)
            current = candidates[chosen_idx][0]
            path.append(current)
            visited.add(current)

        return path if current == target else []
```

#### 4.5 创建 `algorithms/pso.py`（粒子群算法）

```python
# algorithms/pso.py — 粒子群算法

import numpy as np
from collections import deque


class ParticleSwarm:
    """基础粒子群路径搜索"""

    def __init__(self, n_particles: int = 30, n_iterations: int = 200):
        self.n_particles = n_particles
        self.n_iterations = n_iterations
        self.w = 0.5        # 惯性权重
        self.c1 = 1.5       # 个体学习因子
        self.c2 = 1.5       # 群体学习因子

    def search(self, grid: np.ndarray, start: tuple, target: tuple) -> dict:
        h, w = grid.shape
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        def random_path():
            """生成随机可行路径"""
            path = [start]
            visited = set([start])
            current = start
            for _ in range(w * h):
                if current == target:
                    break
                neighbors = []
                x, y = current
                for dx, dy in directions:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and grid[ny, nx] == 0:
                        dist = abs(nx - target[0]) + abs(ny - target[1])
                        neighbors.append(((nx, ny), dist))
                if not neighbors:
                    break
                neighbors.sort(key=lambda v: v[1] + (0 if (v[0] not in visited) else 1000))
                best_neighbor = neighbors[0][0]
                visited.add(best_neighbor)
                path.append(best_neighbor)
                current = best_neighbor
            return path

        particles = [random_path() for _ in range(self.n_particles)]
        p_best = [p for p in particles]
        g_best = min(particles, key=lambda p: self._fitness(p, target))

        for _ in range(self.n_iterations):
            for i in range(self.n_particles):
                new_path = self._update_path(
                    particles[i], p_best[i], g_best, grid, start, target, directions
                )
                if self._fitness(new_path, target) < self._fitness(particles[i], target):
                    particles[i] = new_path
                if self._fitness(new_path, target) < self._fitness(p_best[i], target):
                    p_best[i] = new_path
                if self._fitness(new_path, target) < self._fitness(g_best, target):
                    g_best = new_path

        success = g_best[-1] == target if g_best else False
        return {
            "success": success,
            "path": g_best,
            "path_length": len(g_best),
        }

    def _fitness(self, path: list, target: tuple) -> float:
        if not path:
            return float("inf")
        dist = abs(path[-1][0] - target[0]) + abs(path[-1][1] - target[1])
        return len(path) + dist * 10

    def _update_path(self, path, p_best, g_best, grid, start, target, directions):
        """交叉变异更新路径"""
        h, w = grid.shape
        r = np.random.random()
        if r < self.w:    # 保持原路径
            return self._mutate(path, grid, directions)
        elif r < self.w + self.c1 / (self.c1 + self.c2 + self.w):
            return self._crossover(path, p_best, grid, start)
        else:
            return self._crossover(path, g_best, grid, start)

    def _crossover(self, path_a, path_b, grid, start):
        if len(path_b) < 2:
            return path_a
        idx = np.random.randint(0, min(len(path_a), len(path_b)))
        new_path = path_a[:idx] + path_b[idx:]
        if new_path[0] != start:
            new_path.insert(0, start)
        return new_path

    def _mutate(self, path, grid, directions):
        if len(path) < 3:
            return path
        idx = np.random.randint(1, len(path) - 1)
        x, y = path[idx]
        h, w = grid.shape
        candidates = []
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and grid[ny, nx] == 0:
                candidates.append((nx, ny))
        if candidates:
            new_node = candidates[np.random.randint(len(candidates))]
            new_path = path[:idx] + [new_node] + path[idx + 1:]
            return new_path
        return path
```

#### 4.6 创建 `algorithms/sa.py`（模拟退火）

```python
# algorithms/sa.py — 模拟退火算法

import numpy as np
import random
import math


class SimulatedAnnealing:
    """模拟退火路径搜索"""

    def __init__(self):
        self.initial_temp = 1000.0
        self.cooling_rate = 0.995
        self.min_temp = 0.01
        self.max_iter_per_temp = 50

    def search(self, grid: np.ndarray, start: tuple, target: tuple) -> dict:
        h, w = grid.shape
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        def random_path():
            current = start
            path = [current]
            visited = set([current])
            for _ in range(w * h):
                if current == target:
                    break
                x, y = current
                neighbors = []
                for dx, dy in directions:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and grid[ny, nx] == 0:
                        neighbors.append((nx, ny))
                if not neighbors:
                    break
                neighbors.sort(key=lambda n: (n in visited, abs(n[0] - target[0]) + abs(n[1] - target[1])))
                current = neighbors[0]
                visited.add(current)
                path.append(current)
            return path

        def energy(p):
            if not p or p[-1] != target:
                return float("inf")
            return len(p)

        def neighbor(p):
            if len(p) < 3:
                return p
            idx = random.randint(1, len(p) - 2)
            x, y = p[idx]
            candidates = []
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and grid[ny, nx] == 0:
                    candidates.append((nx, ny))
            if candidates:
                new_node = random.choice(candidates)
                return p[:idx] + [new_node] + p[idx + 1:]
            return p

        current_path = random_path()
        current_energy = energy(current_path)
        best_path = current_path
        best_energy = current_energy

        temp = self.initial_temp
        while temp > self.min_temp:
            for _ in range(self.max_iter_per_temp):
                new_path = neighbor(current_path)
                new_energy = energy(new_path)
                delta = new_energy - current_energy

                if delta < 0 or random.random() < math.exp(-delta / temp):
                    current_path = new_path
                    current_energy = new_energy

                    if current_energy < best_energy:
                        best_path = current_path
                        best_energy = current_energy

            temp *= self.cooling_rate

        success = best_path[-1] == target if best_path else False
        return {
            "success": success,
            "path": best_path,
            "path_length": len(best_path),
        }
```

#### 4.7 创建 `algorithms/hybrid.py`（混合优化算法）

```python
# algorithms/hybrid.py — 混合优化算法（A* + 局部搜索优化）

import numpy as np
from algorithms.astar import AStar


class HybridAlgorithm:
    """A* 生成初始路径 + 局部路径平滑优化"""

    def __init__(self):
        self.astar = AStar()
        self.smooth_iterations = 50

    def search(self, grid: np.ndarray, start: tuple, target: tuple) -> dict:
        # Phase 1: A* 快速生成初始路径
        result = self.astar.search(grid, start, target)
        if not result["success"]:
            return result

        # Phase 2: 局部平滑优化
        path = result["path"]
        for _ in range(self.smooth_iterations):
            path = self._smooth(path, grid)

        return {
            "success": True,
            "path": path,
            "path_length": len(path),
            "nodes_expanded": result["nodes_expanded"],
        }

    def _smooth(self, path: list, grid: np.ndarray) -> list:
        """尝试移除路径中的冗余点（捷径优化）"""
        if len(path) <= 2:
            return path

        h, w = grid.shape
        i = 0
        new_path = [path[0]]

        while i < len(path) - 1:
            # 从后往前找可直达的最远点
            for j in range(len(path) - 1, i, -1):
                if self._line_of_sight(path[i], path[j], grid):
                    new_path.append(path[j])
                    i = j
                    break
            else:
                i += 1
                if i < len(path):
                    new_path.append(path[i])

        return new_path

    def _line_of_sight(self, a: tuple, b: tuple, grid: np.ndarray) -> bool:
        """检查两点之间是否有视线（无障碍物）"""
        x0, y0 = a
        x1, y1 = b
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        h, w = grid.shape
        while (x0, y0) != (x1, y1):
            if not (0 <= x0 < w and 0 <= y0 < h):
                return False
            if grid[y0, x0] == 1:
                return False
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

        return True
```

---

### Step 5 — 实验对比与性能统计

#### 5.1 创建 `evaluation/metrics.py`

```python
# evaluation/metrics.py — 性能指标计算

import time
import numpy as np


def evaluate_algorithm(
    algorithm_func,
    grid: np.ndarray,
    start: tuple,
    target: tuple,
    n_runs: int = 5,
) -> dict:
    """对单种算法运行多次，统计平均值"""
    times = []
    lengths = []
    successes = 0

    for _ in range(n_runs):
        t_start = time.perf_counter()
        result = algorithm_func(grid, start, target)
        elapsed = time.perf_counter() - t_start

        times.append(elapsed)
        if result.get("success", False):
            successes += 1
            lengths.append(result.get("path_length", 0))

    return {
        "avg_time": round(np.mean(times), 4),
        "avg_path_length": round(np.mean(lengths), 1) if lengths else 0,
        "success_rate": round(successes / n_runs, 2),
        "stability_score": round(1.0 - np.std(times) / (np.mean(times) + 1e-6), 4),
    }
```

#### 5.2 创建 `evaluation/benchmark.py`

```python
# evaluation/benchmark.py — 批量实验对比运行器

import json
from algorithms.astar import AStar
from algorithms.aco import AntColony
from algorithms.pso import ParticleSwarm
from algorithms.sa import SimulatedAnnealing
from algorithms.hybrid import HybridAlgorithm
from evaluation.metrics import evaluate_algorithm


class BenchmarkRunner:
    """在同一地图上批量运行5种算法并对比"""

    ALGORITHMS = {
        "A*": AStar().search,
        "ACO": AntColony().search,
        "PSO": ParticleSwarm().search,
        "SA": SimulatedAnnealing().search,
        "混合优化算法": HybridAlgorithm().search,
    }

    def run(
        self,
        grid,
        start: tuple,
        target: tuple,
        n_runs: int = 5,
    ) -> list[dict]:
        results = []
        for name, algo_func in self.ALGORITHMS.items():
            metrics = evaluate_algorithm(algo_func, grid, start, target, n_runs)
            metrics["algorithm"] = name
            results.append(metrics)

        results.sort(key=lambda r: r["success_rate"], reverse=True)
        return results

    def save(self, results: list[dict], filepath: str):
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

    def print_table(self, results: list[dict]):
        print(f"\n{'算法':<10} {'平均耗时(s)':<12} {'路径长度':<10} {'成功率':<8} {'稳定性':<8}")
        print("-" * 55)
        for r in results:
            print(f"{r['algorithm']:<10} {r['avg_time']:<12.4f} {r['avg_path_length']:<10} "
                  f"{r['success_rate']:<8.2f} {r['stability_score']:<8.4f}")
```

**创建操作清单：**

| 序号 | 操作 | 文件 |
|------|------|------|
| 1 | 创建地图生成器 | `map/map_generator.py` |
| 2 | 创建连通性检查器 | `map/connectivity_checker.py` |
| 3 | 创建 A* 算法 | `algorithms/astar.py` |
| 4 | 创建蚁群算法 | `algorithms/aco.py` |
| 5 | 创建粒子群算法 | `algorithms/pso.py` |
| 6 | 创建模拟退火算法 | `algorithms/sa.py` |
| 7 | 创建混合优化算法 | `algorithms/hybrid.py` |
| 8 | 创建性能指标模块 | `evaluation/metrics.py` |
| 9 | 创建批量对比运行器 | `evaluation/benchmark.py` |

---

## 五、阶段三：Qwen 接入与解释生成（Step 6）

> **里程碑验证**：系统决策后，通过 Qwen API 自动生成可解释的选型依据文本与科学假设。

### Step 6 — 接入 Qwen 生成解释与科学假设

#### 6.1 创建 `llm/qwen_client.py`

```python
# llm/qwen_client.py — Qwen API 客户端

import os
import requests
from config import QWEN_API_BASE_URL, QWEN_MODEL_NAME


class QwenClient:
    """阿里云百炼平台 Qwen API 调用封装"""

    def __init__(self):
        self.api_key = os.getenv("QWEN_API_KEY")
        if not self.api_key:
            raise RuntimeError("环境变量 QWEN_API_KEY 未设置")
        self.base_url = QWEN_API_BASE_URL
        self.model = QWEN_MODEL_NAME

    def chat(self, system_prompt: str, user_prompt: str, temperature: float = 0.3) -> str:
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
        }

        response = requests.post(url, json=payload, headers=headers, timeout=60)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
```

#### 6.2 创建 `llm/prompt_templates.py`

```python
# llm/prompt_templates.py — Prompt 模板库

EXPLANATION_SYSTEM_PROMPT = """你是一个路径规划算法选型系统的解释器。
你的任务是根据系统给出的决策数据，生成简洁、可读的选型依据说明。
只输出中文文本，不输出JSON或任何其他格式。
严格以三行格式输出：
第一行：当前场景等级：[等级]
第二行：选定最优算法名称：[算法名]
第三行：简短选型依据：[依据]"""

EXPLANATION_USER_TEMPLATE = """请基于以下决策数据生成选型依据：

当前场景等级：{scene_level}
选定最优算法：{best_algorithm}
综合得分：{best_score}

算法排名（分数从高到低）：
{ranking_detail}

环境参数：
- 障碍物占比：{obstacle_ratio}
- 地图尺寸：{map_width}×{map_height}
- 通道连通性：{connectivity}
- 拓扑随机性：{topology_randomness}
- 算力限制：{compute_limit}"""

HYPOTHESIS_SYSTEM_PROMPT = """你是一个路径规划领域的 AI Scientist。
根据系统的算法选型结果，自动生成一份可验证的科学假设与研究计划。
输出中文，结构化呈现。"""

HYPOTHESIS_USER_TEMPLATE = """基于以下信息生成科学假设与研究计划：

场景等级：{scene_level}
推荐算法：{best_algorithm}
选型依据：{explanation}
算法排名：{ranking_detail}
环境参数：{env_detail}

请输出：
1. 可验证科学假设
2. 解决思路
3. 必要技术手段
4. 实验设计（含数据集、评估指标、预期结果）"""
```

#### 6.3 创建 `agents/explanation_agent.py`

```python
# agents/explanation_agent.py — 解释生成智能体

from llm.qwen_client import QwenClient
from llm.prompt_templates import (
    EXPLANATION_SYSTEM_PROMPT,
    EXPLANATION_USER_TEMPLATE,
)


class ExplanationAgent:
    """调用 Qwen 生成可解释的选型依据"""

    def __init__(self, use_qwen: bool = True):
        self.use_qwen = use_qwen
        if use_qwen:
            self.client = QwenClient()

    def explain(self, env: dict, decision: dict) -> dict:
        if self.use_qwen:
            return self._qwen_explain(env, decision)
        else:
            return self._rule_explain(env, decision)

    def _qwen_explain(self, env: dict, decision: dict) -> dict:
        ranking_detail = self._format_ranking(decision["ranking"])
        user_prompt = EXPLANATION_USER_TEMPLATE.format(
            scene_level=decision["scene_level"],
            best_algorithm=decision["best_algorithm"],
            best_score=decision["best_score"],
            ranking_detail=ranking_detail,
            obstacle_ratio=env.get("obstacle_ratio", "N/A"),
            map_width=env.get("map_width", "N/A"),
            map_height=env.get("map_height", "N/A"),
            connectivity=env.get("connectivity", "N/A"),
            topology_randomness=env.get("topology_randomness", "N/A"),
            compute_limit=env.get("compute_limit", "N/A"),
        )
        text = self.client.chat(EXPLANATION_SYSTEM_PROMPT, user_prompt)
        return {"explanation_text": text}

    def _rule_explain(self, env: dict, decision: dict) -> dict:
        """无 Qwen 时的规则化解释"""
        reason = (
            f"当前障碍物占比为 {env.get('obstacle_ratio', 0):.2f}，"
            f"按照规则判定为{decision['scene_level']}；"
            f"通道连通性为 {env.get('connectivity', 0):.2f}，"
            f"算力限制为 {env.get('compute_limit', 'N/A')}。"
            f"综合五种算法评分，{decision['best_algorithm']} 得分最高"
            f"（{decision['best_score']}），因此被选为最优算法。"
        )
        text = (
            f"当前场景等级：{decision['scene_level']}\n"
            f"选定最优算法名称：{decision['best_algorithm']}\n"
            f"简短选型依据：{reason}"
        )
        return {"explanation_text": text}

    def _format_ranking(self, ranking: list) -> str:
        lines = []
        for i, r in enumerate(ranking, 1):
            lines.append(
                f"{i}. {r['algorithm']}: 得分={r['score']:.4f}, "
                f"耗时={r['avg_time']}s, 成功率={r['success_rate']}, "
                f"惩罚={r.get('penalty', 0)}"
            )
        return "\n".join(lines)
```

#### 6.4 创建 `agents/hypothesis_agent.py`

```python
# agents/hypothesis_agent.py — 科学假设生成智能体

from llm.qwen_client import QwenClient
from llm.prompt_templates import (
    HYPOTHESIS_SYSTEM_PROMPT,
    HYPOTHESIS_USER_TEMPLATE,
)


class HypothesisAgent:
    """调用 Qwen 生成可验证科学假设"""

    def __init__(self, use_qwen: bool = True):
        self.use_qwen = use_qwen
        if use_qwen:
            self.client = QwenClient()

    def generate(self, env: dict, decision: dict, explanation: str) -> str:
        if not self.use_qwen:
            return self._default_hypothesis(env, decision)

        ranking_detail = "\n".join(
            f"{r['algorithm']}: 得分={r['score']:.4f}, 成功率={r['success_rate']}"
            for r in decision["ranking"][:3]
        )
        env_detail = (
            f"障碍物占比={env.get('obstacle_ratio')}, "
            f"连通性={env.get('connectivity')}, "
            f"拓扑随机性={env.get('topology_randomness')}, "
            f"算力限制={env.get('compute_limit')}"
        )
        user_prompt = HYPOTHESIS_USER_TEMPLATE.format(
            scene_level=decision["scene_level"],
            best_algorithm=decision["best_algorithm"],
            explanation=explanation,
            ranking_detail=ranking_detail,
            env_detail=env_detail,
        )
        return self.client.chat(HYPOTHESIS_SYSTEM_PROMPT, user_prompt)

    def _default_hypothesis(self, env: dict, decision: dict) -> str:
        return (
            f"待研究问题：在{decision['scene_level']}动态随机地图中，"
            f"哪种路径规划算法在成功率和耗时方面综合表现最优？\n\n"
            f"科学假设：当前地图障碍物占比为{env.get('obstacle_ratio', 0):.0%}，"
            f"属于{decision['scene_level']}，"
            f"{decision['best_algorithm']}在历史同类场景中综合得分最高，"
            f"预期其在此类环境下具有最优的路径规划表现。\n\n"
            f"验证方案：在相同复杂度等级的随机地图上"
            f"对比5种算法的成功率、平均耗时和路径长度。"
        )
```

**创建操作清单：**

| 序号 | 操作 | 文件 |
|------|------|------|
| 1 | 创建 Qwen API 客户端 | `llm/qwen_client.py` |
| 2 | 创建 Prompt 模板库 | `llm/prompt_templates.py` |
| 3 | 创建解释生成智能体 | `agents/explanation_agent.py` |
| 4 | 创建科学假设生成智能体 | `agents/hypothesis_agent.py` |
| 5 | 创建 `.env.example` | 环境变量模板 |
| 6 | 更新 `main.py` | 集成解释与假设生成 |

---

## 六、阶段四：GUI 展示与报告（Step 7）

> **里程碑验证**：通过浏览器访问 Streamlit 界面，可交互输入参数并查看决策结果。

### Step 7 — GUI 演示界面

#### 6.1 创建 `gui/visualization.py`

```python
# gui/visualization.py — 图表绘制工具

import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")
import numpy as np


def draw_grid(grid: np.ndarray, path: list = None, start: tuple = None, target: tuple = None, title: str = "地图可视化"):
    """绘制栅格地图与路径"""
    fig, ax = plt.subplots(figsize=(6, 6))
    h, w = grid.shape

    # 绘制网格
    colors = np.zeros((h, w))
    colors[grid == 1] = 2   # 障碍物
    ax.imshow(colors, cmap="gray_r", origin="upper", vmin=0, vmax=2)

    if start:
        ax.plot(start[0], start[1], "go", markersize=8, label="起点")
    if target:
        ax.plot(target[0], target[1], "ro", markersize=8, label="终点")
    if path:
        xs = [p[0] for p in path]
        ys = [p[1] for p in path]
        ax.plot(xs, ys, "b-", linewidth=2, label="路径")

    ax.set_title(title)
    ax.legend(loc="upper right")
    ax.set_xlim(-0.5, w - 0.5)
    ax.set_ylim(h - 0.5, -0.5)
    return fig


def draw_ranking_bar(ranking: list[dict]):
    """绘制算法排名柱状图"""
    fig, ax = plt.subplots(figsize=(8, 4))
    names = [r["algorithm"] for r in ranking]
    scores = [r["score"] for r in ranking]
    colors = ["#2ecc71" if i == 0 else "#3498db" for i in range(len(names))]

    bars = ax.bar(names, scores, color=colors)
    ax.set_ylabel("综合得分")
    ax.set_title("算法综合评分排名")
    ax.set_ylim(0, 1)

    for bar, score in zip(bars, scores):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                f"{score:.3f}", ha="center", va="bottom", fontsize=10)

    return fig


def draw_radar(ranking: list[dict]):
    """绘制多指标雷达图"""
    categories = ["耗时", "路径长度", "成功率", "稳定性"]
    N = len(categories)
    angles = [n / N * 2 * np.pi for n in range(N)]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    for r in ranking[:5]:
        detail = r.get("detail", {})
        values = [
            detail.get("time_score", 0),
            detail.get("length_score", 0),
            detail.get("success_score", 0),
            detail.get("stability_score", 0),
        ]
        values += values[:1]
        ax.plot(angles, values, "o-", linewidth=2, label=r["algorithm"])
        ax.fill(angles, values, alpha=0.1)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories)
    ax.set_title("多指标雷达对比")
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))
    return fig
```

#### 6.2 创建 `gui/streamlit_app.py`

```python
# gui/streamlit_app.py — Streamlit 主页面

import streamlit as st
import numpy as np
from main import PathPlanningDecisionSystem
from agents.explanation_agent import ExplanationAgent
from agents.hypothesis_agent import HypothesisAgent
from map.map_generator import MapGenerator
from map.connectivity_checker import ConnectivityChecker
from evaluation.benchmark import BenchmarkRunner
from gui.visualization import draw_grid, draw_ranking_bar, draw_radar
from config import DEFAULT_MAP_WIDTH, DEFAULT_MAP_HEIGHT


def main():
    st.set_page_config(page_title="AI Scientist 路径规划算法选型系统", layout="wide")
    st.title("基于 Qwen 的多智能体路径规划算法自适应选型 AI Scientist 系统")

    # ── 左侧：参数输入区 ──
    with st.sidebar:
        st.header("地图参数设置")
        map_width = st.number_input("地图宽度", 10, 500, DEFAULT_MAP_WIDTH, step=10)
        map_height = st.number_input("地图高度", 10, 500, DEFAULT_MAP_HEIGHT, step=10)
        obstacle_ratio = st.slider("障碍物占比", 0.0, 1.0, 0.35, 0.01)
        connectivity = st.slider("通道连通性", 0.0, 1.0, 0.68, 0.01)
        topology_randomness = st.slider("拓扑随机性", 0.0, 1.0, 0.55, 0.01)
        compute_limit = st.selectbox("算力限制", ["low", "medium", "high"], index=1)
        random_seed = st.number_input("随机种子", 0, 10000, 42)
        st.divider()
        run_decision = st.button("运行算法选型", type="primary", use_container_width=True)

    # ── 中间：地图与算法运行结果 ──
    col_center, col_right = st.columns([3, 2])

    with col_center:
        if run_decision:
            with st.spinner("正在生成地图并运行算法实验..."):
                # 生成地图
                generator = MapGenerator(seed=random_seed)
                start = (0, 0)
                target = (map_width - 1, map_height - 1)
                grid = generator.generate(map_width, map_height, obstacle_ratio, start, target)

                # 连通性检查
                checker = ConnectivityChecker()
                reachable = checker.is_reachable(grid, start, target)
                if not reachable:
                    for _ in range(5):
                        grid = generator.generate(map_width, map_height, obstacle_ratio, start, target)
                        if checker.is_reachable(grid, start, target):
                            reachable = True
                            break
                    if not reachable:
                        st.warning("警告：起点和终点不连通！请调整参数后重试。")

                # 运行算法对比实验
                benchmark = BenchmarkRunner()
                benchmark_results = benchmark.run(grid, start, target, n_runs=3)

                # 运行决策系统
                env_input = {
                    "obstacle_ratio": obstacle_ratio,
                    "map_width": map_width, "map_height": map_height,
                    "connectivity": connectivity,
                    "topology_randomness": topology_randomness,
                    "compute_limit": compute_limit,
                }
                system = PathPlanningDecisionSystem()
                decision = system.decide(env_input)
                st.session_state["decision"] = decision
                st.session_state["benchmark_results"] = benchmark_results
                st.session_state["grid"] = grid
                st.session_state["start"] = start
                st.session_state["target"] = target
                st.session_state["env_input"] = env_input

        if "grid" in st.session_state:
            st.subheader("地图可视化")
            fig_grid = draw_grid(
                st.session_state["grid"],
                start=st.session_state["start"],
                target=st.session_state["target"],
                title=f"随机栅格地图 (障碍物占比={obstacle_ratio:.0%})"
            )
            st.pyplot(fig_grid)

            st.subheader("算法性能对比表")
            benchmark.print_table(st.session_state["benchmark_results"])

            st.subheader("算法综合评分排名")
            fig_bar = draw_ranking_bar(st.session_state["decision"]["ranking"])
            st.pyplot(fig_bar)

            st.subheader("多指标雷达图")
            fig_radar = draw_radar(st.session_state["decision"]["ranking"])
            st.pyplot(fig_radar)

    # ── 右侧：决策结果与解释 ──
    with col_right:
        if "decision" in st.session_state:
            decision = st.session_state["decision"]
            env_input = st.session_state["env_input"]

            st.header("决策结果")
            st.success(f"**场景等级：{decision['scene_level']}**")
            st.info(f"**推荐算法：{decision['best_algorithm']}**")
            st.metric("综合得分", f"{decision['best_score']:.4f}")

            st.divider()
            st.subheader("选型依据")
            explanation_agent = ExplanationAgent(use_qwen=False)
            explanation = explanation_agent.explain(env_input, decision)
            st.text(explanation["explanation_text"])

            st.divider()
            st.subheader("人在回路微调")
            user_priority = st.radio(
                "优化优先级",
                ["系统推荐", "优先最短耗时", "优先最短路径", "优先最高成功率", "平衡模式"],
                index=0,
                key="human_loop",
            )
            if user_priority != "系统推荐":
                st.warning("检测到人工微调请求，将在下一轮决策中调整权重。")

            st.divider()
            st.subheader("科学假设")
            if st.button("生成科学假设"):
                with st.spinner("Qwen 正在生成..."):
                    hypo_agent = HypothesisAgent(use_qwen=False)
                    hypo = hypo_agent.generate(
                        env_input, decision,
                        explanation["explanation_text"]
                    )
                    st.text_area("科学假设与研究计划", hypo, height=300)


if __name__ == "__main__":
    main()
```

---

## 七、阶段五：测试与验证

### 7.1 创建 `tests/test_environment_agent.py`

```python
# tests/test_environment_agent.py

import pytest
from agents.environment_agent import EnvironmentAgent


class TestEnvironmentAgent:
    def setup_method(self):
        self.agent = EnvironmentAgent()

    def test_low_complexity(self):
        env = {"obstacle_ratio": 0.10}
        result = self.agent.classify(env)
        assert result["scene_level"] == "低复杂度"

    def test_medium_complexity(self):
        env = {"obstacle_ratio": 0.35}
        result = self.agent.classify(env)
        assert result["scene_level"] == "中复杂度"

    def test_high_complexity(self):
        env = {"obstacle_ratio": 0.62}
        result = self.agent.classify(env)
        assert result["scene_level"] == "高复杂度"

    def test_boundary_low(self):
        env = {"obstacle_ratio": 0.199}
        result = self.agent.classify(env)
        assert result["scene_level"] == "低复杂度"

    def test_boundary_medium(self):
        env = {"obstacle_ratio": 0.20}
        result = self.agent.classify(env)
        assert result["scene_level"] == "中复杂度"

    def test_boundary_high(self):
        env = {"obstacle_ratio": 0.501}
        result = self.agent.classify(env)
        assert result["scene_level"] == "高复杂度"
```

### 7.2 创建 `tests/test_decision_agent.py`

```python
# tests/test_decision_agent.py

import pytest
from agents.decision_agent import DecisionAgent
from config import ALLOWED_ALGORITHMS


class TestDecisionAgent:
    def setup_method(self):
        self.agent = DecisionAgent()

    def test_select_best_normal(self):
        scored = [
            {"algorithm": "A*", "score": 0.95},
            {"algorithm": "ACO", "score": 0.80},
            {"algorithm": "PSO", "score": 0.75},
        ]
        env = {"scene_level": "低复杂度"}
        result = self.agent.select_best(env, scored)
        assert result["best_algorithm"] == "A*"
        assert result["scene_level"] == "低复杂度"

    def test_illegal_algorithm(self):
        scored = [{"algorithm": "Dijkstra", "score": 0.99}]
        env = {"scene_level": "低复杂度"}
        with pytest.raises(ValueError):
            self.agent.select_best(env, scored)

    def test_empty_records(self):
        with pytest.raises(ValueError):
            self.agent.select_best({"scene_level": "高复杂度"}, [])
```

### 7.3 创建 `tests/test_map_generator.py`

```python
# tests/test_map_generator.py

import numpy as np
from map.map_generator import MapGenerator


class TestMapGenerator:
    def test_generate_basic(self):
        gen = MapGenerator(seed=42)
        grid = gen.generate(50, 50, 0.3)
        assert grid.shape == (50, 50)
        assert np.all((grid == 0) | (grid == 1))

    def test_generate_obstacle_ratio(self):
        gen = MapGenerator(seed=42)
        grid = gen.generate(100, 100, 0.4)
        actual_ratio = grid.sum() / grid.size
        assert abs(actual_ratio - 0.4) < 0.05
```

### 7.4 创建 `tests/test_astar.py`

```python
# tests/test_astar.py

import numpy as np
from algorithms.astar import AStar


class TestAStar:
    def test_direct_path(self):
        grid = np.zeros((10, 10), dtype=np.int8)
        astar = AStar()
        result = astar.search(grid, (0, 0), (9, 9))
        assert result["success"] is True
        assert result["path_length"] > 0
        assert result["path"][0] == (0, 0)
        assert result["path"][-1] == (9, 9)

    def test_no_path(self):
        grid = np.ones((10, 10), dtype=np.int8)
        grid[0, 0] = 0
        grid[9, 9] = 0
        astar = AStar()
        result = astar.search(grid, (0, 0), (9, 9))
        assert result["success"] is False
```

### 7.5 创建 `tests/test_integration.py`

```python
# tests/test_integration.py

from main import PathPlanningDecisionSystem
from agents.explanation_agent import ExplanationAgent


class TestIntegration:
    """端到端集成测试"""

    def test_full_decision_flow_low(self):
        system = PathPlanningDecisionSystem()
        env = {
            "obstacle_ratio": 0.10,
            "map_width": 100, "map_height": 100,
            "connectivity": 0.90, "topology_randomness": 0.20,
            "compute_limit": "high",
        }
        decision = system.decide(env)
        assert decision["scene_level"] == "低复杂度"
        assert decision["best_algorithm"] in ["A*", "ACO", "PSO", "SA", "混合优化算法"]
        assert len(decision["ranking"]) == 5
        assert decision["ranking"][0]["score"] >= decision["ranking"][-1]["score"]

    def test_full_decision_flow_high(self):
        system = PathPlanningDecisionSystem()
        env = {
            "obstacle_ratio": 0.62,
            "map_width": 100, "map_height": 100,
            "connectivity": 0.36, "topology_randomness": 0.72,
            "compute_limit": "high",
        }
        decision = system.decide(env)
        assert decision["scene_level"] == "高复杂度"

    def test_explanation_without_qwen(self):
        system = PathPlanningDecisionSystem()
        env = {
            "obstacle_ratio": 0.35,
            "map_width": 100, "map_height": 100,
            "connectivity": 0.68, "topology_randomness": 0.55,
            "compute_limit": "medium",
        }
        decision = system.decide(env)
        agent = ExplanationAgent(use_qwen=False)
        result = agent.explain(env, decision)
        assert "explanation_text" in result
        assert "当前场景等级" in result["explanation_text"]
        assert "选定最优算法名称" in result["explanation_text"]


def run_tests():
    """手动运行集成测试（不依赖 pytest）"""
    test = TestIntegration()
    test.test_full_decision_flow_low()
    test.test_full_decision_flow_high()
    test.test_explanation_without_qwen()
    print("所有集成测试通过！")


if __name__ == "__main__":
    run_tests()
```

### 7.6 创建 `requirements.txt`

```text
numpy>=1.24.0
scipy>=1.10.0
networkx>=3.0
matplotlib>=3.7.0
plotly>=5.14.0
streamlit>=1.28.0
pytest>=7.4.0
requests>=2.31.0
python-dotenv>=1.0.0
```

### 7.7 创建 `agents/orchestrator_agent.py`

```python
# agents/orchestrator_agent.py — 总控调度智能体

from agents.data_agent import DataReceiverAgent
from agents.environment_agent import EnvironmentAgent
from agents.knowledge_agent import KnowledgeRetrievalAgent
from agents.rule_agent import RuleConstraintAgent
from agents.evaluation_agent import AlgorithmEvaluationAgent
from agents.decision_agent import DecisionAgent
from agents.explanation_agent import ExplanationAgent
from agents.human_loop_agent import HumanLoopAgent
from agents.hypothesis_agent import HypothesisAgent


class OrchestratorAgent:
    """中央调度器，管理智能体执行顺序与数据传递"""

    def __init__(self, use_qwen: bool = False):
        self.data_agent = DataReceiverAgent()
        self.env_agent = EnvironmentAgent()
        self.knowledge_agent = KnowledgeRetrievalAgent()
        self.rule_agent = RuleConstraintAgent()
        self.eval_agent = AlgorithmEvaluationAgent()
        self.decision_agent = DecisionAgent()
        self.explanation_agent = ExplanationAgent(use_qwen=use_qwen)
        self.human_agent = HumanLoopAgent()
        self.hypothesis_agent = HypothesisAgent(use_qwen=use_qwen)

    def run(self, env_input: dict) -> dict:
        env = self.data_agent.validate(env_input)
        env = self.env_agent.classify(env)
        records = self.knowledge_agent.retrieve(env["scene_level"])
        records = self.rule_agent.filter_and_penalize(env, records)
        scored = self.eval_agent.score(env, records)
        decision = self.decision_agent.select_best(env, scored)
        decision = self.human_agent.check(decision)
        explanation = self.explanation_agent.explain(env, decision)

        result = {
            "env": env,
            "decision": decision,
            "explanation": explanation,
        }

        if decision.get("need_human_check"):
            result["hypothesis"] = self.hypothesis_agent.generate(
                env, decision, explanation.get("explanation_text", "")
            )

        return result
```

### 7.8 创建 `agents/human_loop_agent.py`

```python
# agents/human_loop_agent.py — 人在回路智能体

from config import SCORE_GAP_THRESHOLD


class HumanLoopAgent:
    """检测异常情况，触发人工校验提示"""

    def check(self, decision: dict) -> dict:
        ranking = decision["ranking"]

        if len(ranking) >= 2:
            gap = ranking[0]["score"] - ranking[1]["score"]
            if gap < SCORE_GAP_THRESHOLD:
                decision["need_human_check"] = True
                decision["human_check_reason"] = (
                    f"前两名算法（{ranking[0]['algorithm']} 与 {ranking[1]['algorithm']}）"
                    f"评分差距仅 {gap:.4f}，小于阈值 {SCORE_GAP_THRESHOLD}，建议人工确认优化优先级。"
                )
            else:
                decision["need_human_check"] = False

        return decision
```

---

## 八、完整代码结构框架（最终态）

### 8.1 目录树

```text
ai_scientist_path_planning/
│
├── main.py                          ★ 主入口（命令行模式：pure decision flow）
├── config.py                        ★ 全局配置
├── requirements.txt                   依赖清单
├── .env.example                       环境变量模板
│
├── agents/                          ★ 多智能体模块（10个智能体）
│   ├── __init__.py
│   ├── orchestrator_agent.py        总控调度（含 Qwen 集成入口）
│   ├── data_agent.py                数据校验
│   ├── environment_agent.py         环境分级
│   ├── knowledge_agent.py           知识库检索
│   ├── rule_agent.py                规则惩罚
│   ├── evaluation_agent.py          加权评分
│   ├── decision_agent.py            最优选择
│   ├── explanation_agent.py         解释生成（含 Qwen/规则双模式）
│   ├── human_loop_agent.py          人在回路
│   └── hypothesis_agent.py          科学假设生成
│
├── algorithms/                      ★ 5种路径规划算法
│   ├── __init__.py
│   ├── astar.py                     A*（150行）
│   ├── aco.py                       蚁群算法（80行）
│   ├── pso.py                       粒子群算法（100行）
│   ├── sa.py                        模拟退火（80行）
│   └── hybrid.py                    混合优化（60行）
│
├── map/                             ★ 地图模块
│   ├── __init__.py
│   ├── map_generator.py             随机栅格地图生成
│   └── connectivity_checker.py      BFS连通性检查
│
├── evaluation/                      ★ 评估模块
│   ├── __init__.py
│   ├── metrics.py                   指标计算（含稳定性评分）
│   ├── scoring.py                   评分函数（独立使用）
│   └── benchmark.py                 批量对比运行器
│
├── knowledge_base/                  ★ 数据
│   ├── algorithm_profile.json       算法特性
│   └── historical_results.json      15条模拟性能数据
│
├── llm/                             ★ 大模型
│   ├── __init__.py
│   ├── qwen_client.py               Qwen API 客户端
│   └── prompt_templates.py          Prompt 模板
│
├── gui/                             ★ 界面
│   ├── __init__.py
│   ├── streamlit_app.py             Streamlit 主页（三栏布局）
│   └── visualization.py             地图/柱状图/雷达图
│
├── data/                            ★ 运行时目录
│   ├── maps/
│   ├── experiments/
│   └── logs/
│
├── reports/                         ★ 报告
│   └── generated_reports/
│
└── tests/                           ★ 测试
    ├── __init__.py
    ├── test_environment_agent.py    环境分级测试（6个用例）
    ├── test_decision_agent.py       决策测试（3个用例）
    ├── test_astar.py                A* 测试（2个用例）
    ├── test_map_generator.py        地图生成测试（2个用例）
    ├── test_scoring.py              评分测试
    └── test_integration.py          端到端测试（3个用例）
```

### 8.2 文件统计

| 类别 | 文件数 | 预计代码行数 |
|------|--------|-------------|
| 核心入口与配置 | 3 | ~200 |
| 多智能体模块 | 10 | ~400 |
| 路径规划算法 | 5 | ~480 |
| 地图模块 | 2 | ~80 |
| 评估模块 | 3 | ~120 |
| 知识库数据 | 2 | ~150 |
| LLM 接入 | 2 | ~100 |
| GUI 界面 | 2 | ~200 |
| 单元测试 | 6 | ~200 |
| **合计** | **35** | **~1930** |

---

## 九、依赖清单与环境配置

### 9.1 Python 版本要求

- Python 3.9 或更高版本
- 推荐使用虚拟环境：`python -m venv venv`

### 9.2 安装步骤

```bash
# 1. 创建虚拟环境
python -m venv venv

# 2. 激活虚拟环境（Windows）
venv\Scripts\activate

# 3. 激活虚拟环境（macOS/Linux）
source venv/bin/activate

# 4. 安装依赖
pip install -r requirements.txt

# 5. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入真实的 QWEN_API_KEY
```

### 9.3 运行命令

```bash
# 命令行模式（纯决策流程，无需 GUI）
python main.py

# Streamlit GUI 模式
streamlit run gui/streamlit_app.py

# 运行测试
pytest tests/ -v

# 运行集成测试
python tests/test_integration.py
```

### 9.4 阿里云百炼平台接入指引

1. 注册阿里云百炼平台账号
2. 开通模型服务，获取 API Key
3. 将 API Key 写入 `.env` 文件中的 `QWEN_API_KEY` 字段
4. 基础版使用 `qwen-plus` 模型（性价比高）

---

## 十、验收清单

| 验收项 | 验证方式 | 通过标准 |
|--------|----------|----------|
| 环境分级正确性 | `pytest tests/test_environment_agent.py` | 6 个测试用例全部通过 |
| 决策流程完整性 | `python main.py` | 三组场景输出预期算法排名 |
| 知识库可读性 | 直接查看文件 | `historical_results.json` 含15条记录 |
| A* 算法正确性 | `pytest tests/test_astar.py` | 可行路径可达、障碍隔离返回失败 |
| 算法对比表输出 | BenchmarkRunner.print_table() | 5 行 × 5 列表格 |
| Qwen API 调用 | 设置 `QWEN_API_KEY` 后运行 | 返回中文解释文本 |
| Streamlit 可启动 | `streamlit run gui/streamlit_app.py` | 浏览器显示三栏布局 |
| 三行输出格式 | 查看终端/GUI 输出 | `当前场景等级：xxx\n选定最优算法名称：xxx\n简短选型依据：xxx` |
| 算法不得超出限定集合 | DecisionAgent 检查 | 5 种以内，非法算法抛 ValueError |
| 动态地图重启重计算 | 改变参数重新运行 | 输出结果与上次不同 |