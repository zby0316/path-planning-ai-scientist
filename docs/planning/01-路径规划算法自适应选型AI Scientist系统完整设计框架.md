---
model: GPT 5.5
date: 2026-06-04T13:41:19.014Z
---


> **思考过程**
> 
> 

```json
{
  "toolName": "todoWrite",
  "state": "output-available",
  "input": {
    "todos": [
      {
        "status": "in_progress",
        "content": "提炼赛题要求与用户研究方向",
        "activeForm": "正在提炼赛题要求与用户研究方向"
      },
      {
        "status": "pending",
        "content": "设计多智能体系统架构与数据闭环",
        "activeForm": "正在设计多智能体系统架构与数据闭环"
      },
      {
        "status": "pending",
        "content": "给出评分函数、运行流程、代码骨架与交付物框架",
        "activeForm": "正在给出评分函数、运行流程、代码骨架与交付物框架"
      }
    ]
  },
  "output": {
    "count": 3,
    "todos": [
      {
        "status": "in_progress",
        "content": "提炼赛题要求与用户研究方向",
        "activeForm": "正在提炼赛题要求与用户研究方向"
      },
      {
        "status": "pending",
        "content": "设计多智能体系统架构与数据闭环",
        "activeForm": "正在设计多智能体系统架构与数据闭环"
      },
      {
        "status": "pending",
        "content": "给出评分函数、运行流程、代码骨架与交付物框架",
        "activeForm": "正在给出评分函数、运行流程、代码骨架与交付物框架"
      }
    ],
    "success": true
  }
}
```

> **思考过程**
> 
> 

```json
{
  "toolName": "todoWrite",
  "state": "output-available",
  "input": {
    "todos": [
      {
        "status": "completed",
        "content": "提炼赛题要求与用户研究方向",
        "activeForm": "正在提炼赛题要求与用户研究方向"
      },
      {
        "status": "in_progress",
        "content": "设计多智能体系统架构与数据闭环",
        "activeForm": "正在设计多智能体系统架构与数据闭环"
      },
      {
        "status": "pending",
        "content": "给出评分函数、运行流程、代码骨架与交付物框架",
        "activeForm": "正在给出评分函数、运行流程、代码骨架与交付物框架"
      }
    ]
  },
  "output": {
    "count": 3,
    "todos": [
      {
        "status": "completed",
        "content": "提炼赛题要求与用户研究方向",
        "activeForm": "正在提炼赛题要求与用户研究方向"
      },
      {
        "status": "in_progress",
        "content": "设计多智能体系统架构与数据闭环",
        "activeForm": "正在设计多智能体系统架构与数据闭环"
      },
      {
        "status": "pending",
        "content": "给出评分函数、运行流程、代码骨架与交付物框架",
        "activeForm": "正在给出评分函数、运行流程、代码骨架与交付物框架"
      }
    ],
    "success": true
  }
}
```

> **思考过程**
> 
> **Finalizing the code skeleton**
> 
> I need to detail the data schema, which consists of several tables. The maps table will have fields like map_id, timestamp, and obstacle_ratio, among others. The algorithm performance table will include time metrics and success rates. The run log will document inputs and reviewer feedback. For algo rules, I’ll outline constraints and hyperparameters.
> 
> The scoring formula requires careful attention, particularly on weights for success, time, path, and robustness. I need to factor in dynamic rules for compute limitations.

> **思考过程**
> 
> **Refining the exclusion criteria**
> 
> I need to set exclusion criteria based on success rates, which could be thresholded at low (0.85), medium (0.75), and high (0.65). Since I don’t have actual data, I should allow for user-defined thresholds rather than inventing my own. It's important to clarify that the threshold comes from training/validation and should be configurable.
> 
> I'll also exclude cases where p95 time exceeds compute budget unless all exceed, in which case I’ll keep the best and mark human review. The algorithm must be in an allowed set. 
> 
> For production responses, I’ll keep it short, including a rationale in the logs. The steps of the pipeline involve receiving data, validating it, classifying complexity, querying a knowledge base, filtering candidates, and scoring them.

```json
{
  "toolName": "todoWrite",
  "state": "output-available",
  "input": {
    "todos": [
      {
        "status": "completed",
        "content": "提炼赛题要求与用户研究方向",
        "activeForm": "正在提炼赛题要求与用户研究方向"
      },
      {
        "status": "completed",
        "content": "设计多智能体系统架构与数据闭环",
        "activeForm": "正在设计多智能体系统架构与数据闭环"
      },
      {
        "status": "in_progress",
        "content": "给出评分函数、运行流程、代码骨架与交付物框架",
        "activeForm": "正在给出评分函数、运行流程、代码骨架与交付物框架"
      }
    ]
  },
  "output": {
    "count": 3,
    "todos": [
      {
        "status": "completed",
        "content": "提炼赛题要求与用户研究方向",
        "activeForm": "正在提炼赛题要求与用户研究方向"
      },
      {
        "status": "completed",
        "content": "设计多智能体系统架构与数据闭环",
        "activeForm": "正在设计多智能体系统架构与数据闭环"
      },
      {
        "status": "in_progress",
        "content": "给出评分函数、运行流程、代码骨架与交付物框架",
        "activeForm": "正在给出评分函数、运行流程、代码骨架与交付物框架"
      }
    ],
    "success": true
  }
}
```

> **思考过程**
> 
> 

```json
{
  "toolName": "todoWrite",
  "state": "output-available",
  "input": {
    "todos": [
      {
        "status": "completed",
        "content": "提炼赛题要求与用户研究方向",
        "activeForm": "正在提炼赛题要求与用户研究方向"
      },
      {
        "status": "completed",
        "content": "设计多智能体系统架构与数据闭环",
        "activeForm": "正在设计多智能体系统架构与数据闭环"
      },
      {
        "status": "completed",
        "content": "给出评分函数、运行流程、代码骨架与交付物框架",
        "activeForm": "正在给出评分函数、运行流程、代码骨架与交付物框架"
      }
    ]
  },
  "output": {
    "count": 3,
    "todos": [
      {
        "status": "completed",
        "content": "提炼赛题要求与用户研究方向",
        "activeForm": "正在提炼赛题要求与用户研究方向"
      },
      {
        "status": "completed",
        "content": "设计多智能体系统架构与数据闭环",
        "activeForm": "正在设计多智能体系统架构与数据闭环"
      },
      {
        "status": "completed",
        "content": "给出评分函数、运行流程、代码骨架与交付物框架",
        "activeForm": "正在给出评分函数、运行流程、代码骨架与交付物框架"
      }
    ],
    "success": true
  }
}
```

> **思考过程**
> 
> 

下面给你一套**“基于 Qwen 的多智能体路径规划算法自适应选型 AI Scientist 系统”完整设计框架**。它严格围绕你给出的研究方向：在复杂动态随机地图中，根据障碍物占比、地图尺寸、连通性、拓扑结构、算力限制和历史性能数据库，从 **A\***、**ACO 蚁群算法**、**PSO 粒子群算法**、**SA 模拟退火算法**、**混合优化算法** 这 5 类算法中自动选出当前最优路径规划算法。

---

# 一、项目定位

## 1. 项目名称

**基于国产开源大模型的动态随机地图路径规划算法自适应选型 AI Scientist 系统**

或更学术化一点：

**A Qwen-based Multi-Agent AI Scientist for Adaptive Path Planning Algorithm Selection in Dynamic Random Maps**

---

## 2. 核心研究问题

传统路径规划系统通常需要人工根据经验选择算法，例如：

- 障碍物少时用 A\*；
- 环境复杂时用 ACO 或混合优化算法；
- 随机拓扑复杂时尝试 PSO；
- 算力紧张时优先选择耗时低的算法。

但这种方式存在几个问题：

1. **依赖人工经验**；
2. **无法适应动态地图频繁变化**；
3. **缺少可解释的算法选择逻辑**；
4. **没有充分利用历史算法性能数据**；
5. **不同算法在不同复杂度环境下的适配边界不清晰**。

因此，本项目要构建一个多智能体系统，使其能够自动完成：

> 动态环境感知 → 环境复杂度分级 → 知识库检索 → 算法性能评估 → 候选算法筛除 → 最优算法推荐 → 人在回路校验 → 结果可解释输出。

---

# 二、整体系统目标

该系统不是直接做路径规划，而是做**路径规划算法决策层**，也就是在不同地图环境下自动判断：

> 当前场景应该调用 A\*、ACO、PSO、SA 还是混合优化算法。

系统最终输出必须满足你给定的格式：

```text
当前场景等级：高复杂度
选定最优算法名称：混合优化算法
简短选型依据：障碍物占比为 62%，属于高复杂度场景；历史知识库显示混合优化算法在该类场景下成功率最高，虽然耗时较长，但当前算力允许，因此优先选择成功率更高的混合优化算法。
```

---

# 三、系统总体架构

建议采用 **“中央调度智能体 + 多专业智能体协作”** 架构。

整体结构如下：

```text
用户 / 动态地图环境输入
        ↓
[任务调度智能体 Orchestrator Agent]
        ↓
--------------------------------------------------
| 1. 数据接收智能体 Data Receiver Agent          |
| 2. 环境特征分析智能体 Environment Agent        |
| 3. 知识库检索智能体 Knowledge Retrieval Agent  |
| 4. 规则约束智能体 Rule Constraint Agent        |
| 5. 算法评估智能体 Algorithm Evaluation Agent   |
| 6. 决策生成智能体 Decision Agent               |
| 7. 解释生成智能体 Explanation Agent            |
| 8. 人在回路校验智能体 Human-in-the-loop Agent  |
| 9. 实验验证智能体 Experiment Agent             |
| 10. 报告生成智能体 Report Agent                |
--------------------------------------------------
        ↓
输出：场景等级 + 最优算法 + 选型依据 + 可验证研究计划
```

---

# 四、各智能体详细设计

---

## Agent 1：任务调度智能体 Orchestrator Agent

### 作用

负责统一管理整个多智能体流程，类似系统大脑。

### 输入

- 用户提交的实时地图参数；
- 地图文件或仿真环境数据；
- 历史算法性能数据库；
- 当前算力限制；
- 用户是否允许人工微调。

### 输出

将任务分配给其他智能体，并汇总结果。

### 核心职责

1. 检查输入是否完整；
2. 触发环境分级；
3. 调用知识库检索；
4. 组织算法评分；
5. 触发最终决策；
6. 若参数异常，转入人在回路流程。

### 示例伪代码

```python
class OrchestratorAgent:
    def run(self, env_input):
        validated_input = DataReceiverAgent().validate(env_input)
        env_profile = EnvironmentAgent().classify(validated_input)
        algo_records = KnowledgeRetrievalAgent().retrieve(env_profile)
        filtered_algos = RuleConstraintAgent().filter(env_profile, algo_records)
        ranked_algos = AlgorithmEvaluationAgent().score(env_profile, filtered_algos)
        decision = DecisionAgent().select_best(env_profile, ranked_algos)
        explanation = ExplanationAgent().explain(env_profile, decision)
        final_output = HumanLoopAgent().check(env_profile, decision, explanation)
        return final_output
```

---

## Agent 2：数据接收智能体 Data Receiver Agent

### 作用

负责读取和校验输入数据。

### 必须读取的字段

根据你给出的任务，至少包括：

| 字段 | 含义 | 示例 |
|---|---|---|
| obstacle_ratio | 地图障碍物占比 | 0.35 |
| map_width | 地图宽度 | 100 |
| map_height | 地图高度 | 100 |
| connectivity | 通道连通性 | 0.72 |
| topology_randomness | 随机拓扑结构复杂度 | 0.65 |
| compute_limit | 实时算力限制 | low / medium / high |
| dynamic_change_rate | 动态变化率 | 0.30 |
| start_point | 起点 | [0, 0] |
| target_point | 终点 | [99, 99] |

### 输入示例

```json
{
  "obstacle_ratio": 0.42,
  "map_width": 100,
  "map_height": 100,
  "connectivity": 0.68,
  "topology_randomness": 0.57,
  "compute_limit": "medium",
  "dynamic_change_rate": 0.25,
  "start_point": [0, 0],
  "target_point": [99, 99]
}
```

### 校验规则

```text
1. obstacle_ratio 必须在 0 到 1 之间；
2. map_width 和 map_height 必须大于 0；
3. connectivity 必须在 0 到 1 之间；
4. topology_randomness 必须在 0 到 1 之间；
5. compute_limit 只能为 low、medium、high；
6. 起点和终点不能落在障碍物区域；
7. 若地图重新启动或环境变化，则必须重新计算，不允许沿用历史决策。
```

---

## Agent 3：环境特征分析智能体 Environment Agent

### 作用

负责对当前地图复杂度进行量化和分级。

### 基础分级规则

根据你给出的硬性规则：

```text
障碍物占比 < 20%：低复杂度
20% ≤ 障碍物占比 ≤ 50%：中复杂度
障碍物占比 > 50%：高复杂度
```

### 输出示例

```json
{
  "scene_level": "中复杂度",
  "obstacle_ratio": 0.42,
  "connectivity": 0.68,
  "topology_randomness": 0.57,
  "compute_limit": "medium"
}
```

### 可扩展复杂度评分

除了单纯使用障碍物占比，还可以引入综合复杂度指数：

\[
C = 0.45 \times O + 0.25 \times (1 - K) + 0.20 \times R + 0.10 \times D
\]

其中：

| 符号 | 含义 |
|---|---|
| \(O\) | 障碍物占比 |
| \(K\) | 通道连通性 |
| \(R\) | 拓扑随机性 |
| \(D\) | 动态变化率 |

但是注意：  
**最终场景等级仍然优先按照你规定的障碍物占比规则划分**，综合复杂度指数只作为辅助解释。

---

## Agent 4：知识库检索智能体 Knowledge Retrieval Agent

### 作用

负责从历史算法性能数据库中检索五种算法在相似环境下的表现。

### 知识库内容

知识库应该保存五种算法在不同复杂度场景下的历史表现，包括：

| 算法 | 场景等级 | 平均耗时 | 平均路径长度 | 成功率 | 稳定性 | 适配边界 |
|---|---|---|---|---|---|---|
| A\* | 低复杂度 | 0.12s | 108 | 0.98 | 高 | 障碍少、连通性好 |
| ACO | 中复杂度 | 1.80s | 115 | 0.91 | 中 | 复杂通道、局部搜索 |
| PSO | 中复杂度 | 1.50s | 120 | 0.87 | 中 | 连续空间优化 |
| SA | 中复杂度 | 1.20s | 125 | 0.82 | 中 | 可跳出局部最优 |
| 混合优化算法 | 高复杂度 | 2.80s | 112 | 0.94 | 高 | 高障碍、高随机拓扑 |

注意：这里的数据只是结构示例。  
正式参赛时必须换成你的**实测动态数据集**结果。

### 数据库字段设计

可以使用 Excel、CSV、SQLite、MySQL 或向量数据库保存。

推荐表结构：

```sql
CREATE TABLE algorithm_performance (
    id INTEGER PRIMARY KEY,
    algorithm_name TEXT,
    scene_level TEXT,
    obstacle_ratio_min FLOAT,
    obstacle_ratio_max FLOAT,
    avg_time FLOAT,
    avg_path_length FLOAT,
    success_rate FLOAT,
    stability_score FLOAT,
    compute_cost FLOAT,
    map_size_range TEXT,
    connectivity_range TEXT,
    topology_randomness_range TEXT,
    evidence_source TEXT
);
```

### 检索逻辑

```python
def retrieve_algorithm_records(scene_level):
    records = db.query(
        "SELECT * FROM algorithm_performance WHERE scene_level = ?",
        scene_level
    )
    return records
```

---

## Agent 5：规则约束智能体 Rule Constraint Agent

### 作用

负责根据硬性规则筛除不适配算法。

这一步非常关键，因为你的要求里明确写了：

> 只能在指定 5 种算法内择优，禁止编造未定义路径算法。

所以该智能体必须保证系统永远只在以下集合中选择：

```python
ALLOWED_ALGORITHMS = ["A*", "ACO", "PSO", "SA", "混合优化算法"]
```

---

## 规则库设计

### 规则 1：低复杂度场景

```text
若 obstacle_ratio < 0.2：
    优先考虑 A*
    若算力限制低，则进一步强化 A* 的优先级
    ACO、PSO、SA、混合优化算法可作为备选，但需要证明其路径质量收益大于耗时成本
```

### 规则 2：中复杂度场景

```text
若 0.2 ≤ obstacle_ratio ≤ 0.5：
    A* 若出现路径绕行严重或成功率下降，则降低优先级
    ACO、PSO、SA 进入主要候选集
    若拓扑随机性较高，ACO 和混合优化算法加权提高
    若算力限制低，则降低混合优化算法权重
```

### 规则 3：高复杂度场景

```text
若 obstacle_ratio > 0.5：
    优先考量成功率
    A* 若历史成功率低于阈值，则排除或降权
    SA 若成功率不足，则排除或降权
    混合优化算法和 ACO 优先进入候选集
```

### 规则 4：算力受限

```text
若 compute_limit = low：
    优先考量 avg_time
    对高耗时算法增加惩罚项
```

### 规则 5：复杂障碍环境

```text
若 obstacle_ratio > 0.5 或 connectivity < 0.4：
    优先考量 success_rate
    成功率低于阈值的算法直接降权
```

---

## Agent 6：算法评估智能体 Algorithm Evaluation Agent

### 作用

根据历史性能数据对候选算法进行综合评分。

### 评分指标

| 指标 | 含义 |
|---|---|
| avg_time | 平均寻路耗时 |
| avg_path_length | 平均路径长度 |
| success_rate | 寻路成功率 |
| stability_score | 稳定性 |
| compute_cost | 算力消耗 |
| adaptability | 动态环境适应性 |

---

## 归一化方法

不同指标量纲不同，需要先归一化。

### 耗时归一化

耗时越低越好：

\[
T_{score}(a) = 1 - \frac{T_a - T_{min}}{T_{max} - T_{min}}
\]

### 路径长度归一化

路径越短越好：

\[
L_{score}(a) = 1 - \frac{L_a - L_{min}}{L_{max} - L_{min}}
\]

### 成功率归一化

成功率越高越好：

\[
S_{score}(a) = SuccessRate_a
\]

### 综合评分

\[
Score(a) = w_t T_{score}(a) + w_l L_{score}(a) + w_s S_{score}(a) + w_r R_{score}(a) - Penalty(a)
\]

其中：

| 权重 | 含义 |
|---|---|
| \(w_t\) | 耗时权重 |
| \(w_l\) | 路径长度权重 |
| \(w_s\) | 成功率权重 |
| \(w_r\) | 稳定性权重 |
| Penalty | 规则惩罚项 |

---

## 不同场景下的权重建议

### 低复杂度场景

障碍少，重点是快和路径短：

```python
weights = {
    "time": 0.45,
    "path_length": 0.30,
    "success_rate": 0.15,
    "stability": 0.10
}
```

### 中复杂度场景

需要平衡效率、路径质量和成功率：

```python
weights = {
    "time": 0.25,
    "path_length": 0.30,
    "success_rate": 0.30,
    "stability": 0.15
}
```

### 高复杂度场景

优先保证能找到路：

```python
weights = {
    "time": 0.15,
    "path_length": 0.20,
    "success_rate": 0.50,
    "stability": 0.15
}
```

### 算力受限场景修正

如果 `compute_limit = low`：

```python
weights["time"] += 0.20
weights["success_rate"] -= 0.10
weights["path_length"] -= 0.10
```

同时对高耗时算法增加惩罚项：

```python
if compute_limit == "low" and avg_time > time_threshold:
    penalty += 0.15
```

---

## Agent 7：决策生成智能体 Decision Agent

### 作用

负责选择评分最高的算法，并生成最终决策。

### 决策逻辑

```python
best_algorithm = max(candidate_algorithms, key=lambda x: x["score"])
```

但要加上硬性检查：

```python
if best_algorithm not in ALLOWED_ALGORITHMS:
    raise ValueError("非法算法，系统只能选择 A*、ACO、PSO、SA、混合优化算法")
```

### 输出内容

```json
{
  "scene_level": "高复杂度",
  "best_algorithm": "混合优化算法",
  "score": 0.89,
  "reason": "障碍物占比高、拓扑随机性强，历史数据库中混合优化算法在该类场景下成功率最高。"
}
```

---

## Agent 8：解释生成智能体 Explanation Agent

### 作用

将算法选择过程转化为人类可理解的推理依据。

### 解释必须包含

1. 当前场景等级；
2. 关键环境特征；
3. 调取的历史性能数据；
4. 排除哪些算法以及原因；
5. 为什么最终算法最优；
6. 是否存在人工微调建议。

### 示例输出

```text
当前场景等级：高复杂度
选定最优算法名称：混合优化算法
简短选型依据：当前障碍物占比为 58%，属于高复杂度场景；通道连通性为 0.36，说明可通行区域碎片化明显。历史数据库显示，在高复杂度场景下，混合优化算法平均成功率为 94%，高于 A*、PSO 和 SA。虽然其平均耗时较高，但当前算力限制为 high，因此优先选择成功率和稳定性更高的混合优化算法。
```

这正好满足你的输出格式要求。

---

## Agent 9：人在回路校验智能体 Human-in-the-loop Agent

### 作用

当系统发现输入异常、规则冲突或算法评分接近时，触发人工校验。

### 触发条件

```text
1. obstacle_ratio 缺失或超出 0~1；
2. connectivity 缺失或异常；
3. compute_limit 未知；
4. 前两名算法评分差距小于 0.05；
5. 高复杂度场景下所有算法成功率都低于设定阈值；
6. 地图发生重启但未重新上传环境数据；
7. 历史知识库中缺少对应复杂度场景数据。
```

### 人工微调接口

可以提供如下界面选项：

```text
请选择优化优先级：
A. 优先最短耗时
B. 优先最短路径
C. 优先最高成功率
D. 平衡模式
```

### 微调后权重修改

例如用户选择“优先最高成功率”：

```python
weights = {
    "time": 0.15,
    "path_length": 0.20,
    "success_rate": 0.55,
    "stability": 0.10
}
```

---

## Agent 10：实验验证智能体 Experiment Agent

### 作用

负责验证系统选型是否可靠。

它需要调用五种算法在同一批动态随机地图上进行实验，记录：

- 平均耗时；
- 平均路径长度；
- 寻路成功率；
- 节点扩展数量；
- 碰撞率；
- 重规划次数；
- 动态障碍变化下的鲁棒性。

---

# 五、完整数据闭环设计

系统应形成以下闭环：

```text
动态地图输入
    ↓
环境特征提取
    ↓
场景复杂度分级
    ↓
历史性能数据库检索
    ↓
五种算法候选集构建
    ↓
规则筛除与权重调整
    ↓
算法综合评分
    ↓
最优算法输出
    ↓
实际路径规划执行
    ↓
记录本次算法表现
    ↓
更新历史性能数据库
    ↓
下一次地图变化时重新计算
```

关键点：

> 每次动态地图重启或环境变量发生变化时，必须重新走完整流程，不能沿用上一次的选型结果。

---

# 六、系统核心模块设计

## 1. 输入层

输入包括两类：

### 静态地图输入

```text
地图尺寸
障碍物占比
起点
终点
基础拓扑结构
```

### 动态环境输入

```text
动态障碍物变化率
实时算力限制
通道连通性
随机拓扑扰动程度
历史算法表现
```

---

## 2. 知识库层

知识库分为两部分：

### 算法知识库

保存算法机制和适配场景。

示例：

```json
{
  "A*": {
    "advantages": ["速度快", "确定性强", "低复杂度场景路径质量高"],
    "disadvantages": ["高障碍物环境下搜索空间膨胀", "动态环境下重规划开销较大"],
    "suitable_scene": ["低复杂度", "连通性好", "算力受限"]
  },
  "ACO": {
    "advantages": ["全局搜索能力较强", "适合复杂路径搜索"],
    "disadvantages": ["收敛速度较慢", "参数敏感"],
    "suitable_scene": ["中复杂度", "高复杂度", "多路径候选"]
  },
  "PSO": {
    "advantages": ["适合连续空间优化", "全局搜索能力较好"],
    "disadvantages": ["离散栅格地图中需要编码转换", "可能早熟收敛"],
    "suitable_scene": ["中复杂度", "连续空间路径优化"]
  },
  "SA": {
    "advantages": ["可跳出局部最优", "实现简单"],
    "disadvantages": ["收敛速度和退火参数相关", "高复杂度下稳定性不足"],
    "suitable_scene": ["中复杂度", "局部路径优化"]
  },
  "混合优化算法": {
    "advantages": ["兼顾全局搜索和局部优化", "高复杂度场景成功率较高"],
    "disadvantages": ["计算成本较高", "系统复杂度较高"],
    "suitable_scene": ["高复杂度", "动态障碍", "随机拓扑强"]
  }
}
```

### 性能数据库

保存实测性能数据。

示例：

```json
[
  {
    "algorithm": "A*",
    "scene_level": "低复杂度",
    "avg_time": 0.12,
    "avg_path_length": 108.4,
    "success_rate": 0.98,
    "stability_score": 0.95
  },
  {
    "algorithm": "ACO",
    "scene_level": "中复杂度",
    "avg_time": 1.80,
    "avg_path_length": 115.7,
    "success_rate": 0.91,
    "stability_score": 0.86
  }
]
```

---

# 七、核心决策流程

完整流程可以写成如下形式：

```text
Step 1：读取实时输入
    输入障碍物占比、地图尺寸、通道连通性、随机拓扑结构、算力限制。

Step 2：环境分级
    按照障碍物占比分为低复杂度、中复杂度、高复杂度。

Step 3：知识库检索
    查询五种算法在对应复杂度下的历史平均耗时、路径长度、成功率。

Step 4：规则约束
    根据算力限制、复杂障碍程度、连通性，排除或降低劣势算法权重。

Step 5：综合评分
    对五种算法进行耗时、路径长度、成功率、稳定性加权评分。

Step 6：确定最优算法
    选择综合评分最高的算法。

Step 7：生成解释
    输出场景等级、算法名称、选型依据。

Step 8：人在回路
    若输入异常或评分接近，提示人工确认或调整权重。

Step 9：实验反馈
    执行路径规划实验，记录真实性能，更新数据库。
```

---

# 八、可落地代码框架

下面给一个简化版 Python 框架，后续你可以扩展为 FastAPI 后端、Streamlit 前端或百炼智能体应用。

```python
ALLOWED_ALGORITHMS = ["A*", "ACO", "PSO", "SA", "混合优化算法"]


class DataReceiverAgent:
    def validate(self, env):
        required_fields = [
            "obstacle_ratio",
            "map_width",
            "map_height",
            "connectivity",
            "topology_randomness",
            "compute_limit"
        ]

        for field in required_fields:
            if field not in env:
                raise ValueError(f"缺少必要字段: {field}")

        if not 0 <= env["obstacle_ratio"] <= 1:
            raise ValueError("obstacle_ratio 必须在 0 到 1 之间")

        if not 0 <= env["connectivity"] <= 1:
            raise ValueError("connectivity 必须在 0 到 1 之间")

        if not 0 <= env["topology_randomness"] <= 1:
            raise ValueError("topology_randomness 必须在 0 到 1 之间")

        if env["compute_limit"] not in ["low", "medium", "high"]:
            raise ValueError("compute_limit 必须为 low、medium 或 high")

        if env["map_width"] <= 0 or env["map_height"] <= 0:
            raise ValueError("地图尺寸必须大于 0")

        return env


class EnvironmentAgent:
    def classify(self, env):
        obstacle_ratio = env["obstacle_ratio"]

        if obstacle_ratio < 0.2:
            scene_level = "低复杂度"
        elif obstacle_ratio <= 0.5:
            scene_level = "中复杂度"
        else:
            scene_level = "高复杂度"

        complexity_index = (
            0.45 * env["obstacle_ratio"] +
            0.25 * (1 - env["connectivity"]) +
            0.20 * env["topology_randomness"] +
            0.10 * env.get("dynamic_change_rate", 0)
        )

        env["scene_level"] = scene_level
        env["complexity_index"] = round(complexity_index, 4)

        return env


class KnowledgeRetrievalAgent:
    def __init__(self):
        self.performance_db = [
            {
                "algorithm": "A*",
                "scene_level": "低复杂度",
                "avg_time": 0.12,
                "avg_path_length": 108,
                "success_rate": 0.98,
                "stability_score": 0.95
            },
            {
                "algorithm": "ACO",
                "scene_level": "低复杂度",
                "avg_time": 1.20,
                "avg_path_length": 112,
                "success_rate": 0.96,
                "stability_score": 0.90
            },
            {
                "algorithm": "PSO",
                "scene_level": "低复杂度",
                "avg_time": 1.10,
                "avg_path_length": 116,
                "success_rate": 0.92,
                "stability_score": 0.86
            },
            {
                "algorithm": "SA",
                "scene_level": "低复杂度",
                "avg_time": 0.90,
                "avg_path_length": 118,
                "success_rate": 0.90,
                "stability_score": 0.84
            },
            {
                "algorithm": "混合优化算法",
                "scene_level": "低复杂度",
                "avg_time": 1.80,
                "avg_path_length": 109,
                "success_rate": 0.97,
                "stability_score": 0.93
            },

            {
                "algorithm": "A*",
                "scene_level": "中复杂度",
                "avg_time": 0.75,
                "avg_path_length": 142,
                "success_rate": 0.82,
                "stability_score": 0.80
            },
            {
                "algorithm": "ACO",
                "scene_level": "中复杂度",
                "avg_time": 1.80,
                "avg_path_length": 130,
                "success_rate": 0.91,
                "stability_score": 0.87
            },
            {
                "algorithm": "PSO",
                "scene_level": "中复杂度",
                "avg_time": 1.50,
                "avg_path_length": 136,
                "success_rate": 0.87,
                "stability_score": 0.84
            },
            {
                "algorithm": "SA",
                "scene_level": "中复杂度",
                "avg_time": 1.20,
                "avg_path_length": 139,
                "success_rate": 0.84,
                "stability_score": 0.81
            },
            {
                "algorithm": "混合优化算法",
                "scene_level": "中复杂度",
                "avg_time": 2.20,
                "avg_path_length": 128,
                "success_rate": 0.93,
                "stability_score": 0.90
            },

            {
                "algorithm": "A*",
                "scene_level": "高复杂度",
                "avg_time": 2.40,
                "avg_path_length": 190,
                "success_rate": 0.55,
                "stability_score": 0.60
            },
            {
                "algorithm": "ACO",
                "scene_level": "高复杂度",
                "avg_time": 2.60,
                "avg_path_length": 158,
                "success_rate": 0.88,
                "stability_score": 0.86
            },
            {
                "algorithm": "PSO",
                "scene_level": "高复杂度",
                "avg_time": 2.20,
                "avg_path_length": 170,
                "success_rate": 0.78,
                "stability_score": 0.76
            },
            {
                "algorithm": "SA",
                "scene_level": "高复杂度",
                "avg_time": 1.90,
                "avg_path_length": 176,
                "success_rate": 0.72,
                "stability_score": 0.73
            },
            {
                "algorithm": "混合优化算法",
                "scene_level": "高复杂度",
                "avg_time": 3.00,
                "avg_path_length": 152,
                "success_rate": 0.94,
                "stability_score": 0.91
            }
        ]

    def retrieve(self, scene_level):
        return [
            record for record in self.performance_db
            if record["scene_level"] == scene_level
            and record["algorithm"] in ALLOWED_ALGORITHMS
        ]


class RuleConstraintAgent:
    def filter_and_penalize(self, env, records):
        processed = []

        for record in records:
            penalty = 0.0
            algorithm = record["algorithm"]

            # 算力受限时惩罚高耗时算法
            if env["compute_limit"] == "low" and record["avg_time"] > 1.5:
                penalty += 0.15

            # 高复杂度场景优先成功率，低成功率算法惩罚
            if env["scene_level"] == "高复杂度" and record["success_rate"] < 0.80:
                penalty += 0.20

            # 低复杂度场景中，对过度复杂算法稍微惩罚
            if env["scene_level"] == "低复杂度" and algorithm == "混合优化算法":
                penalty += 0.10

            # 连通性差时，惩罚成功率较低算法
            if env["connectivity"] < 0.4 and record["success_rate"] < 0.85:
                penalty += 0.15

            record = record.copy()
            record["penalty"] = penalty
            processed.append(record)

        return processed


class AlgorithmEvaluationAgent:
    def get_weights(self, env):
        scene_level = env["scene_level"]

        if scene_level == "低复杂度":
            weights = {
                "time": 0.45,
                "path_length": 0.30,
                "success_rate": 0.15,
                "stability": 0.10
            }
        elif scene_level == "中复杂度":
            weights = {
                "time": 0.25,
                "path_length": 0.30,
                "success_rate": 0.30,
                "stability": 0.15
            }
        else:
            weights = {
                "time": 0.15,
                "path_length": 0.20,
                "success_rate": 0.50,
                "stability": 0.15
            }

        if env["compute_limit"] == "low":
            weights["time"] += 0.20
            weights["path_length"] -= 0.10
            weights["success_rate"] -= 0.10

        return weights

    def normalize_reverse(self, value, min_value, max_value):
        if max_value == min_value:
            return 1.0
        return 1 - (value - min_value) / (max_value - min_value)

    def score(self, env, records):
        weights = self.get_weights(env)

        times = [r["avg_time"] for r in records]
        lengths = [r["avg_path_length"] for r in records]

        min_time, max_time = min(times), max(times)
        min_length, max_length = min(lengths), max(lengths)

        scored = []

        for record in records:
            time_score = self.normalize_reverse(
                record["avg_time"],
                min_time,
                max_time
            )
            length_score = self.normalize_reverse(
                record["avg_path_length"],
                min_length,
                max_length
            )
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
            scored.append(record)

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored


class DecisionAgent:
    def select_best(self, env, scored_records):
        if not scored_records:
            raise ValueError("没有可用算法候选，请检查知识库数据")

        best = scored_records[0]

        if best["algorithm"] not in ALLOWED_ALGORITHMS:
            raise ValueError("非法算法，系统只能从指定五种算法中选择")

        return {
            "scene_level": env["scene_level"],
            "best_algorithm": best["algorithm"],
            "best_score": best["score"],
            "ranking": scored_records
        }


class ExplanationAgent:
    def explain(self, env, decision):
        best_algo = decision["best_algorithm"]
        best_score = decision["best_score"]

        reason = (
            f"当前障碍物占比为 {env['obstacle_ratio']:.2f}，"
            f"按照规则判定为{env['scene_level']}；"
            f"通道连通性为 {env['connectivity']:.2f}，"
            f"拓扑随机性为 {env['topology_randomness']:.2f}，"
            f"实时算力限制为 {env['compute_limit']}。"
            f"结合历史性能数据库中五种算法的平均耗时、路径长度、成功率和稳定性综合评分，"
            f"{best_algo} 的综合得分最高，为 {best_score}，因此被选为当前最优路径规划算法。"
        )

        return {
            "line1": f"当前场景等级：{env['scene_level']}",
            "line2": f"选定最优算法名称：{best_algo}",
            "line3": f"简短选型依据：{reason}"
        }


class HumanLoopAgent:
    def check(self, decision):
        ranking = decision["ranking"]

        if len(ranking) >= 2:
            gap = ranking[0]["score"] - ranking[1]["score"]
            if gap < 0.05:
                decision["need_human_check"] = True
                decision["human_check_reason"] = "前两名算法评分差距小于 0.05，建议人工确认优化优先级。"
            else:
                decision["need_human_check"] = False

        return decision


class PathPlanningDecisionSystem:
    def run(self, env_input):
        env = DataReceiverAgent().validate(env_input)
        env = EnvironmentAgent().classify(env)

        records = KnowledgeRetrievalAgent().retrieve(env["scene_level"])
        records = RuleConstraintAgent().filter_and_penalize(env, records)

        scored_records = AlgorithmEvaluationAgent().score(env, records)

        decision = DecisionAgent().select_best(env, scored_records)
        decision = HumanLoopAgent().check(decision)

        explanation = ExplanationAgent().explain(env, decision)

        return explanation, decision


if __name__ == "__main__":
    env_input = {
        "obstacle_ratio": 0.58,
        "map_width": 100,
        "map_height": 100,
        "connectivity": 0.36,
        "topology_randomness": 0.72,
        "compute_limit": "high",
        "dynamic_change_rate": 0.30
    }

    system = PathPlanningDecisionSystem()
    explanation, decision = system.run(env_input)

    print(explanation["line1"])
    print(explanation["line2"])
    print(explanation["line3"])
```

---

# 九、系统输出示例

假设输入：

```json
{
  "obstacle_ratio": 0.58,
  "map_width": 100,
  "map_height": 100,
  "connectivity": 0.36,
  "topology_randomness": 0.72,
  "compute_limit": "high",
  "dynamic_change_rate": 0.30
}
```

输出可以是：

```text
当前场景等级：高复杂度
选定最优算法名称：混合优化算法
简短选型依据：当前障碍物占比为 0.58，按照规则判定为高复杂度；通道连通性为 0.36，拓扑随机性为 0.72，实时算力限制为 high。结合历史性能数据库中五种算法的平均耗时、路径长度、成功率和稳定性综合评分，混合优化算法的综合得分最高，因此被选为当前最优路径规划算法。
```

---

# 十、面向比赛 PDF 要求的作品包装方式

根据 PDF 中对 AI Scientist 的要求，你的系统不能只做一个规则程序，而要体现：

1. 文献挖掘与事实提取；
2. 逻辑驱动的假设生成；
3. 论证可行与多轮迭代；
4. 智能体思辨与人在回路；
5. 输出标准化的科学假设与研究计划。

所以可以把项目包装成如下形式。

---

## 1. 待研究问题 Problem Statement

在复杂动态随机地图中，不同路径规划算法的性能受障碍物密度、地图尺寸、通道连通性、随机拓扑结构和实时算力约束影响显著。传统路径规划系统通常依赖人工经验选择算法，缺少基于实测数据和动态环境特征的自适应选型机制，导致在高复杂度或算力受限场景下可能出现寻路失败、路径冗长或计算延迟过高等问题。

---

## 2. 解决思路 Rationale

本项目提出一个基于 Qwen 大模型的多智能体路径规划算法决策系统。系统将动态地图环境特征、算法知识库和历史性能数据库进行融合，通过环境分级、知识检索、规则推理、加权评分和人在回路校验，从 A\*、ACO、PSO、SA、混合优化算法五类候选算法中自动选择当前最优算法。

核心假设是：

> 在动态随机地图中，若能将障碍物占比、连通性、拓扑随机性和算力限制转化为结构化环境特征，并结合历史算法性能数据进行规则约束和加权评分，则可以比固定算法策略获得更高的平均寻路成功率和更好的综合路径规划表现。

---

## 3. 必要技术手段 Technical Details

系统需要使用以下技术：

| 模块 | 技术 |
|---|---|
| 基座模型 | Qwen 开源模型 |
| 模型调用平台 | 阿里云百炼平台 |
| 后端框架 | Python / FastAPI |
| 智能体编排 | 多智能体调度框架，可自研或基于 LangGraph、AutoGen 等思想实现 |
| 数据存储 | SQLite / MySQL / PostgreSQL |
| 地图仿真 | Python 栅格地图仿真 |
| 算法实现 | A\*、ACO、PSO、SA、混合优化算法 |
| 评估指标 | 耗时、路径长度、成功率、稳定性、重规划次数 |
| 可视化 | Streamlit / Vue / React |
| 报告生成 | 自动生成科学假设与研究计划 PDF |

---

## 4. 数据集 Datasets

### Source：历史数据

包括：

1. 随机生成的栅格地图；
2. 不同障碍物占比的地图集合；
3. 不同连通性水平的地图集合；
4. 不同动态障碍变化率的地图集合；
5. 五种算法在上述地图中的运行结果。

数据字段包括：

```text
map_id
map_width
map_height
obstacle_ratio
connectivity
topology_randomness
dynamic_change_rate
algorithm_name
avg_time
path_length
success_rate
collision_count
replan_count
stability_score
```

### Target：验证数据

系统后续验证需要采集：

```text
新地图环境参数
系统推荐算法
实际执行耗时
实际路径长度
是否成功到达目标点
是否发生碰撞
重规划次数
与其他算法对比结果
```

---

## 5. 方法论 Methods

可以写成以下五阶段：

### 阶段一：动态随机地图生成

构建不同尺寸和障碍物占比的栅格地图：

```text
50 × 50
100 × 100
200 × 200
```

障碍物占比分为：

```text
低复杂度：0% ~ 20%
中复杂度：20% ~ 50%
高复杂度：50% 以上
```

---

### 阶段二：五种路径规划算法运行

在同一批地图上分别运行：

```text
A*
ACO
PSO
SA
混合优化算法
```

记录每种算法的：

```text
平均耗时
路径长度
成功率
稳定性
重规划次数
```

---

### 阶段三：构建算法性能知识库

把实验结果写入数据库，作为智能体决策依据。

---

### 阶段四：多智能体协同决策

由多个智能体完成：

```text
数据接收 → 环境分级 → 知识库检索 → 规则筛除 → 综合评分 → 决策输出 → 人工校验
```

---

### 阶段五：闭环更新

系统执行推荐算法后，把真实表现重新写入数据库。

这样下一轮动态地图变化时，智能体可以基于更丰富的数据重新决策。

---

# 十一、实验设计 Experiments

## 1. Baselines 基线方法

建议设置以下基线：

| 基线 | 含义 |
|---|---|
| 固定 A\* | 所有场景都使用 A\* |
| 固定 ACO | 所有场景都使用 ACO |
| 固定 PSO | 所有场景都使用 PSO |
| 固定 SA | 所有场景都使用 SA |
| 固定混合优化算法 | 所有场景都使用混合优化算法 |
| 人工规则选择 | 按人工经验选择算法 |
| 本系统 | 多智能体自适应选型 |

---

## 2. Metrics 评估指标

| 指标 | 说明 |
|---|---|
| Success Rate | 寻路成功率 |
| Average Time | 平均寻路耗时 |
| Average Path Length | 平均路径长度 |
| Replanning Count | 动态环境下重规划次数 |
| Collision Rate | 路径碰撞率 |
| Decision Accuracy | 选型结果是否接近真实最优算法 |
| Robustness | 不同地图随机种子下表现稳定性 |
| Explainability Score | 专家对解释合理性的评分 |

---

## 3. 实验分组

### 低复杂度地图组

```text
障碍物占比：0% ~ 20%
主要验证系统是否能优先选择高效率算法，如 A*
```

### 中复杂度地图组

```text
障碍物占比：20% ~ 50%
主要验证系统是否能平衡耗时、路径长度和成功率
```

### 高复杂度地图组

```text
障碍物占比：50% 以上
主要验证系统是否能优先考虑成功率和鲁棒性
```

### 算力受限组

```text
固定计算时间预算
验证系统是否能主动降低高耗时算法优先级
```

### 动态障碍组

```text
障碍物随时间变化
验证系统是否能在环境重启或变化后重新决策
```

---

# 十二、预期实验结果 Results

可以设定如下预期：

1. 在低复杂度场景下，系统大多数情况下选择 A\*，平均耗时低于群智能类算法；
2. 在中复杂度场景下，系统会根据连通性和拓扑随机性在 ACO、PSO、SA 和混合优化算法之间动态选择；
3. 在高复杂度场景下，系统更倾向于选择混合优化算法或 ACO，以提高寻路成功率；
4. 在算力受限场景下，系统会主动提高耗时指标权重；
5. 相比固定单一算法策略，多智能体自适应选型系统在综合评分上更优。

---

# 十三、前端演示页面设计

建议做一个简单交互前端，方便比赛展示。

## 页面 1：输入页面

用户可以输入：

```text
地图尺寸
障碍物占比
通道连通性
拓扑随机性
动态变化率
算力限制
起点
终点
```

---

## 页面 2：地图可视化页面

展示：

```text
随机地图
障碍物区域
起点
终点
当前推荐算法路径
```

---

## 页面 3：算法对比页面

展示五种算法的：

```text
耗时柱状图
路径长度折线图
成功率对比图
综合评分雷达图
```

---

## 页面 4：智能体推理页面

展示每个智能体的工作结果：

```text
Data Agent：已读取输入
Environment Agent：判定为高复杂度
Knowledge Agent：已检索历史性能数据
Rule Agent：A* 因成功率低被降权
Evaluation Agent：混合优化算法综合得分最高
Decision Agent：选择混合优化算法
Human Agent：无需人工干预
```

---

## 页面 5：最终输出页面

严格展示三行核心结果：

```text
当前场景等级：高复杂度
选定最优算法名称：混合优化算法
简短选型依据：……
```

并附加可下载的：

```text
科学假设与研究计划
算法性能对比报告
实验日志
源代码说明
```

---

# 十四、最终参赛材料结构建议

技术方案 PDF 可以这样写：

```text
1. 项目背景与问题定义
2. 研究目标
3. 系统总体架构
4. 多智能体模块设计
5. 动态地图数据集构建
6. 五种路径规划算法实现
7. 算法性能知识库设计
8. 自适应选型评分模型
9. 人在回路机制
10. 实验设计与评估指标
11. 系统演示与案例
12. 结果分析
13. 创新点总结
14. 可复现说明
15. 未来扩展方向
```

---

# 十五、项目创新点总结

你的作品可以突出以下创新点：

1. **从路径规划算法执行层上升到算法决策层**  
   不再固定使用某一种算法，而是根据环境自动选型。

2. **多智能体协作架构**  
   将数据接收、环境分级、知识检索、规则推理、算法评分、人在回路分离成多个智能体。

3. **结合历史实测数据进行决策**  
   避免大模型凭空判断，满足“所有决策结论必须依托数据与知识库”的要求。

4. **可解释算法推荐**  
   不只输出算法名称，还输出障碍物占比、成功率、耗时、路径长度等依据。

5. **动态环境重计算机制**  
   每次地图重启或环境变化都重新执行完整流程。

6. **人在回路校验机制**  
   当前两名算法评分接近、输入异常或知识库不足时，引入人工微调。

7. **符合 AI Scientist 比赛要求**  
   具备问题理解、知识整合、关联发现、可验证假设生成和标准化研究计划输出能力。

---

# 十六、一句话总结框架

你可以把这个系统定义为：

> 一个基于 Qwen 大模型和多智能体架构的路径规划算法决策 AI Scientist，通过动态地图环境感知、算法性能知识库检索、规则约束推理和多指标评分，在 A\*、ACO、PSO、SA、混合优化算法五种候选算法中自动选择当前最优路径规划策略，并通过人在回路和实验反馈实现可解释、可验证、可复现的闭环优化。
