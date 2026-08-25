---
model: GPT 5.5
date: 2026-06-08T11:06:05.827Z
---

下面给你一套**紧扣比赛要求、基于你 01–08 号方案文件的优化升级路线**。核心思路是：不要把系统只做成“路径规划算法推荐器”，而要升级为一个真正符合比赛定义的 **AI Scientist：数据/文献输入 → 知识整合 → 规律发现 → 假设生成 → 实验验证 → 研究报告输出** 的闭环系统。

***

# 一、总目标：从“算法选型系统”升级为“AI Scientist 系统”

你现在基础版已经完成：

```text
环境参数输入 → 场景复杂度判断 → 知识库检索 → 算法评分 → 推荐 A*/ACO/PSO/SA/混合优化算法
```

下一步要补齐比赛最看重的能力：

1. **真实数据输入**：不能只用手写模拟数据，要接入公开 benchmark 或可复现实验数据；
2. **文献输入**：要有路径规划算法文献、数据集文献、算法适配性文献；
3. **知识整合**：把文献事实、实验数据、算法性能边界统一进知识库；
4. **科学假设生成**：不仅输出“选哪个算法”，还要输出“为什么该类场景下这个算法可能更优”的可验证假设；
5. **实验验证**：对假设进行批量地图实验，形成结果表、图表、可信度评估；
6. **人在回路与多智能体思辨**：允许用户调整优先级、质疑结论、查看每个智能体推理过程；
7. **规范研究报告输出**：严格生成比赛方案要求的 10 个字段。

***

# 二、升级路线总览：由易到难

建议分 7 个阶段推进。

| 阶段      | 难度 | 核心目标          | 对应比赛能力            |
| ------- | -: | ------------- | ----------------- |
| Phase 0 |  低 | 合规体检与基础版封版    | 明确作品边界            |
| Phase 1 |  低 | 数据输入升级        | 数据/文献输入           |
| Phase 2 | 中低 | 实验数据库与指标体系升级  | 可验证实验基础           |
| Phase 3 |  中 | 文献知识库与 RAG 升级 | 文献挖掘、事实提取         |
| Phase 4 |  中 | 多智能体协同升级      | 多智能体 AI Scientist |
| Phase 5 | 中高 | 假设生成—实验验证闭环   | 可验证科学假设           |
| Phase 6 | 中高 | 前端展示与人在回路升级   | 可交互、可解释           |
| Phase 7 |  高 | 后端工程化、部署与高级功能 | 可复现、可扩展           |

***

# 三、Phase 0：基础版合规体检与封版

## 目标

先不要急着加复杂功能，先确认基础版满足比赛最低要求。

## 必做事项

### 1. 明确系统定位

把项目名称统一为：

> **基于 Qwen 多智能体系统的动态随机地图路径规划算法适配边界发现与科学假设生成系统**

这个标题比“路径规划算法选型系统”更贴近比赛。

### 2. 明确 Qwen 的作用

基础版中算法评分由 Python 规则和数据库完成，这很好，因为决策稳定。

但是比赛要求基于 Qwen，所以要明确 Qwen 负责：

- 理解用户输入；
- 解释算法选型依据；
- 从文献中抽取算法适配事实；
- 生成科学假设；
- 生成实验计划；
- 生成研究报告；
- 模拟审稿人或反思智能体。

Qwen API 可以参考阿里云 Model Studio / DashScope 的官方调用说明，官方文档提供了 API Key、环境变量和接口调用入口说明：[Guide for beginners - Alibaba Cloud Model Studio](https://www.alibabacloud.com/help/en/model-studio/getting-started/quick-start/)。

### 3. 明确“不能让大模型凭空选算法”

建议写进技术文档：

```text
最终算法选择由可复现实验数据和评分函数决定；
Qwen 负责解释、归纳、假设生成和报告撰写；
系统禁止 Qwen 直接凭主观判断选择算法。
```

这样可以避免评审认为系统“只是大模型聊天”。

***

# 四、Phase 1：数据输入升级

这是最优先做的部分。比赛强调真实数据和可验证性，因此基础版不能只依赖 15 条手写模拟历史数据。

## 1. 数据输入分三类

### A. 参数输入数据

保留基础版已有字段：

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

### B. 地图文件输入

新增支持：

```text
.map 文件
.scen 文件
.csv 栅格地图
.json 栅格地图
.npy NumPy 地图
```

其中 `.map` 和 `.scen` 建议优先支持 Moving AI 的格式。Moving AI Lab 提供了 2D grid pathfinding benchmark maps 和 benchmark problems，可作为路径规划实验数据来源：[Moving AI 2D Grid Benchmarks](https://www.movingai.com/benchmarks/grids.html)。

### C. 公共 benchmark 数据输入

建议优先使用：

| 数据来源                          | 用途           | 下载位置                                                                           |
| ----------------------------- | ------------ | ------------------------------------------------------------------------------ |
| Moving AI 2D Grid Benchmarks  | 2D 栅格路径规划实验  | [Moving AI 2D Grid Benchmarks](https://www.movingai.com/benchmarks/grids.html) |
| Moving AI 3D Voxel Benchmarks | 后续 3D 地图扩展   | [3D Pathfinding Benchmarks](https://www.movingai.com/benchmarks/voxels.html)   |
| OpenStreetMap 道路网络            | 拓扑图路径规划扩展    | [OpenStreetMap Copyright and License](https://www.openstreetmap.org/copyright) |
| Geofabrik OSM Extracts        | 下载 OSM 区域数据  | [Geofabrik OpenStreetMap Data Extracts](https://download.geofabrik.de/)        |
| 自建随机动态地图                      | 动态障碍、不同障碍率实验 | 用你自己的 `MapGenerator` 生成                                                        |

OpenStreetMap 数据使用时需要遵守 ODbL 署名要求，OpenStreetMap 官方版权页面说明了其开放数据许可和署名要求：[OpenStreetMap Copyright and License](https://www.openstreetmap.org/copyright)。

Geofabrik 提供 OpenStreetMap 数据区域切片下载，包含 `.osm.pbf`、`.gpkg.zip` 等格式，可用于道路网络拓扑图实验：[Geofabrik OpenStreetMap Data Extracts](https://download.geofabrik.de/)。

## 2. 数据目录建议

把基础版目录升级为：

```text
data/
├── raw/
│   ├── movingai_2d/
│   ├── movingai_3d/
│   ├── osm/
│   └── uploaded/
│
├── processed/
│   ├── grid_maps/
│   ├── topology_graphs/
│   └── dynamic_maps/
│
├── experiments/
│   ├── algorithm_runs.sqlite
│   ├── benchmark_summary.xlsx
│   └── failure_cases.jsonl
│
└── literature/
    ├── raw_pdf/
    ├── metadata/
    ├── extracted_facts.jsonl
    └── references.bib
```

## 3. 数据卡 Data Card

每个数据集都生成一个 `data_card.md`：

```text
数据集名称：
来源：
下载链接：
许可协议：
地图类型：
地图数量：
起终点任务数量：
使用目的：
预处理方式：
是否可复现：
```

这会让技术方案文档更像正式科研作品。

***

# 五、Phase 2：实验数据库与指标体系升级

## 1. 从 JSON 升级到 SQLite

基础版 `historical_results.json` 可以保留，但比赛版建议升级为 SQLite。

建议建表：

```sql
CREATE TABLE maps (
    map_id TEXT PRIMARY KEY,
    source TEXT,
    map_type TEXT,
    width INTEGER,
    height INTEGER,
    obstacle_ratio REAL,
    connectivity REAL,
    topology_randomness REAL,
    dynamic_change_rate REAL
);

CREATE TABLE algorithm_runs (
    run_id TEXT PRIMARY KEY,
    map_id TEXT,
    algorithm TEXT,
    parameters TEXT,
    runtime REAL,
    path_length REAL,
    success INTEGER,
    expanded_nodes INTEGER,
    turning_points INTEGER,
    smoothness REAL,
    safety_score REAL,
    stability_score REAL,
    compute_limit TEXT,
    seed INTEGER,
    created_at TEXT
);

CREATE TABLE hypotheses (
    hypothesis_id TEXT PRIMARY KEY,
    scene_condition TEXT,
    hypothesis_text TEXT,
    generated_by TEXT,
    evidence TEXT,
    validation_status TEXT,
    created_at TEXT
);
```

## 2. 指标从 4 个升级到 10 个

基础版已有：

```text
耗时
路径长度
成功率
稳定性
```

升级版建议增加：

| 指标                | 说明          |
| ----------------- | ----------- |
| runtime           | 平均耗时        |
| path\_length      | 路径长度        |
| success\_rate     | 成功率         |
| stability\_score  | 多次运行稳定性     |
| smoothness        | 路径平滑度       |
| safety\_score     | 路径与障碍物距离    |
| expanded\_nodes   | 搜索节点数       |
| replanning\_count | 动态重规划次数     |
| compute\_cost     | 算力消耗代理指标    |
| robustness        | 动态扰动下性能保持能力 |

## 3. 实验分组

建议至少做 3 × 3 × 3 的实验矩阵：

```text
复杂度：
- 低障碍：<20%
- 中障碍：20%~50%
- 高障碍：>50%

地图规模：
- 50×50
- 100×100
- 200×200

算力限制：
- low
- medium
- high
```

每组地图至少：

```text
10 张地图 × 5 种算法 × 3 次重复实验
```

如果时间紧，先做：

```text
3 个复杂度 × 每类 10 张地图 × 5 种算法 = 150 次运行
```

这已经可以支撑比赛演示。

***

# 六、Phase 3：文献知识库与 RAG 升级

比赛方案明确要求文献挖掘、事实提取和真实参考文献，因此这一阶段非常关键。

## 1. 需要收集哪些文献？

建议收集 5 类文献。

### A. 基础路径规划算法文献

用于支撑 A\*、ACO、PSO、SA、混合优化算法的原理与适配场景。

检索关键词：

```text
A* algorithm path planning
ant colony optimization path planning
particle swarm optimization path planning
simulated annealing path planning
hybrid path planning algorithm
robot path planning grid map
dynamic obstacle path planning
```

### B. 路径规划 benchmark 文献

重点引用 Moving AI 2D Grid Benchmark。Moving AI 页面提供了其 grid benchmark 的引用信息，包括 Sturtevant 2012 的 benchmark 论文：[Moving AI 2D Grid Benchmarks](https://www.movingai.com/benchmarks/grids.html)。

### C. 3D 路径规划文献

如果后续扩展 3D，可引用 Moving AI 3D voxel benchmark 页面提供的 Brewer 与 Sturtevant 2018 相关信息：[3D Pathfinding Benchmarks](https://www.movingai.com/benchmarks/voxels.html)。

### D. 动态路径规划与重规划文献

用于解释动态障碍变化时为什么需要重新选型或局部修复。

检索关键词：

```text
dynamic path planning replanning
D* Lite path planning
incremental heuristic search
robot navigation dynamic obstacles
```

注意：D\* Lite 可以作为背景文献，但你的系统最终算法集合仍然限制为：

```text
A*
ACO
PSO
SA
混合优化算法
```

不要把 D\* Lite 加入最终选型集合，避免违反你前面设定的五算法边界。

### E. AI Scientist / LLM for Science 文献

用于解释为什么用 Qwen 和多智能体做科学假设生成。

检索关键词：

```text
AI Scientist scientific hypothesis generation
large language models for scientific discovery
multi-agent system scientific reasoning
LLM literature mining hypothesis generation
```

## 2. 文献从哪里查找？

| 平台                       | 用途                    | 链接                                                                     |
| ------------------------ | --------------------- | ---------------------------------------------------------------------- |
| Semantic Scholar         | 文献检索、元数据、引用信息         | [Semantic Scholar API](https://api.semanticscholar.org/api-docs/graph) |
| arXiv                    | 开源论文 PDF              | [arXiv](https://arxiv.org/)                                            |
| Google Scholar           | 快速查找经典论文              | <https://scholar.google.com>                                           |
| IEEE Xplore              | A\*、PSO、机器人路径规划经典工程论文 | <https://ieeexplore.ieee.org>                                          |
| ACM Digital Library      | 算法与图搜索论文              | <https://dl.acm.org>                                                   |
| ScienceDirect / Springer | 优化算法、机器人导航综述          | <https://www.sciencedirect.com> / <https://link.springer.com>          |
| CNKI                     | 中文路径规划、机器人、智能优化论文     | <https://www.cnki.net>                                                 |

Semantic Scholar 提供 Academic Graph API，可用于构建文献检索模块：[Semantic Scholar Academic Graph API](https://api.semanticscholar.org/api-docs/graph)。

## 3. 文献知识库字段

建议每篇文献存储：

```json
{
  "paper_id": "xxx",
  "title": "xxx",
  "authors": ["xxx"],
  "year": 2020,
  "venue": "xxx",
  "doi": "xxx",
  "url": "xxx",
  "algorithm_related": ["A*", "ACO"],
  "key_facts": [
    "A* 在静态栅格地图中具有较强确定性和较高效率",
    "ACO 在复杂搜索空间中具备较强全局搜索能力"
  ],
  "evidence_level": "paper",
  "citation": "BibTeX"
}
```

## 4. 新增文献智能体

在 `agents/` 下新增：

```text
literature_agent.py        # 文献检索智能体
fact_extraction_agent.py   # 科学事实抽取智能体
citation_agent.py          # 引用核验智能体
rag_agent.py               # 文献知识检索智能体
```

核心要求：

```text
所有进入报告的文献必须有 title、authors、year、URL/DOI；
禁止生成不存在的参考文献；
无法核验的参考文献不能进入最终 References。
```

***

# 七、Phase 4：多智能体协同升级

基础版已有 DataAgent、EnvironmentAgent、KnowledgeAgent、EvaluationAgent、DecisionAgent 等。升级版要让它更像 AI Scientist。

## 1. 推荐多智能体架构

```text
用户输入 / 地图数据 / 文献数据
        ↓
[Orchestrator 总控调度智能体]
        ↓
------------------------------------------------
1. Data Agent：数据接收与校验
2. Map Analysis Agent：地图结构特征分析
3. Literature Agent：文献检索与事实抽取
4. Knowledge Agent：历史性能数据库检索
5. Rule Agent：硬规则与算法边界约束
6. Evaluation Agent：多指标评分与 Pareto 分析
7. Parameter Agent：算法超参数推荐
8. Hypothesis Agent：科学假设生成
9. Experiment Agent：实验验证
10. Reflection Agent：反思与可信度检查
11. Human-loop Agent：人在回路微调
12. Report Agent：研究报告生成
------------------------------------------------
        ↓
标准化科学假设与研究计划
```

## 2. 每个智能体要有统一输入输出

建议定义全局状态对象：

```python
@dataclass
class ResearchState:
    env_input: dict
    map_features: dict
    literature_facts: list
    algorithm_records: list
    scored_algorithms: list
    decision: dict
    recommended_params: dict
    hypothesis: dict
    experiment_results: list
    reflection: dict
    report: str
```

这样可以避免多智能体输出不一致。

## 3. 多智能体协同重点

### 决策原则

```text
程序负责计算；
Qwen 负责解释、归纳、假设和报告；
实验负责验证；
Reflection Agent 负责质疑；
Human-loop Agent 负责人工修正。
```

### 触发人在回路条件

```text
1. 前两名算法得分差 < 0.05；
2. 历史数据库缺少对应场景数据；
3. 推荐算法与实验最佳算法不一致；
4. 高复杂度场景下所有算法成功率都低；
5. 用户选择“安全优先 / 耗时优先 / 成功率优先”；
6. 文献证据不足；
7. 引用无法核验。
```

***

# 八、Phase 5：假设生成—实验验证闭环

这是比赛最核心的部分。

## 1. 系统不能只输出这个

```text
当前场景等级：高复杂度
选定最优算法名称：混合优化算法
简短选型依据：……
```

这只是工程选型输出。

## 2. 必须进一步输出科学假设

例如：

```text
科学假设：
在障碍物占比超过 50%、通道连通性低于 0.4 的动态随机栅格地图中，混合优化算法相比单一 A*、ACO、PSO 和 SA，在寻路成功率和路径稳定性方面具有显著优势；该优势来自其全局搜索与局部优化机制的互补。
```

## 3. 每条假设必须绑定验证实验

```text
验证实验：
构建 50 张高复杂度随机地图，每张地图分别运行 A*、ACO、PSO、SA、混合优化算法 5 次；
记录成功率、平均耗时、路径长度、路径平滑度和稳定性；
若混合优化算法成功率显著高于其他算法，且耗时未超过计算预算，则支持该假设。
```

## 4. 闭环流程

```text
生成假设
    ↓
设计实验
    ↓
运行五算法对比
    ↓
写入实验数据库
    ↓
统计结果
    ↓
Reflection Agent 检查结论
    ↓
更新知识库
    ↓
修正假设或形成最终研究计划
```

## 5. 反思智能体检查内容

```text
1. 推荐算法是否真的是实验最优？
2. 是否存在另一个算法成功率更高？
3. 是否只是耗时最短但成功率不足？
4. 文献依据是否真实？
5. 数据是否覆盖低、中、高复杂度？
6. 实验次数是否足够？
7. 结论是否过度泛化？
```

***

# 九、Phase 6：结果输出升级

比赛方案要求最终生成《科学假设与研究计划》，包含 10 个字段。你的系统必须固定输出这些字段。

## 标准输出模板

```markdown
# 科学假设与研究计划

## 1. 待研究问题 Problem Statement
动态随机地图中，不同路径规划算法在障碍密度、连通性、拓扑随机性和算力约束下表现差异显著，传统人工经验选型难以保证最优。

## 2. 解决思路 Rationale
构建基于 Qwen 的多智能体 AI Scientist，通过地图特征分析、文献事实抽取、历史性能检索、多指标评分和实验验证，发现路径规划算法适配边界。

## 3. 必要技术手段 Technical Details
包括随机栅格地图生成、Moving AI benchmark 解析、A*/ACO/PSO/SA/混合优化算法实现、SQLite 实验数据库、Qwen 文献事实抽取、多智能体协同、Pareto 多目标评分等。

## 4. 数据集 Datasets
Source：Moving AI benchmark、自建随机动态地图、历史算法运行数据库、路径规划文献知识库。
Target：新生成动态随机地图及五算法对比实验结果。

## 5. 论文标题 Paper Title
A Qwen-based Multi-Agent AI Scientist for Adaptive Path Planning Algorithm Selection in Dynamic Random Maps

## 6. 摘要 Paper Abstract
……

## 7. 方法论 Methods
……

## 8. 实验设计 Experiments
包含 Baselines：A*、ACO、PSO、SA、混合优化算法。
包含 Metrics：耗时、路径长度、成功率、稳定性、路径平滑度、安全性、重规划次数等。

## 9. 实验结果 Results
输出实验表格、柱状图、雷达图、假设支持程度。

## 10. 参考论文 References
列出真实可核验文献，禁止虚构。
```

***

# 十、Phase 7：前端 GUI 升级路线

你已有 07 和 08 号 GUI 方案。比赛展示优先建议按下面顺序做。

## 1. 第一优先级：基础展示页

保持 Streamlit，但升级为 4 个 Tab：

```text
Tab 1：地图与数据输入
Tab 2：环境分析与算法评分
Tab 3：多智能体推理链
Tab 4：科学假设与研究报告
```

## 2. Tab 1：数据输入页

新增：

```text
1. 手动输入地图参数；
2. 上传 CSV / JSON / .map / .scen；
3. 选择 Moving AI benchmark 示例；
4. 选择随机地图模板；
5. 设置动态变化率；
6. 设置算力约束；
7. 设置优化偏好：耗时优先 / 成功率优先 / 路径最短 / 平衡模式。
```

## 3. Tab 2：环境分析页

展示：

```text
地图预览
障碍物占比
连通性
拓扑随机性
综合复杂度指数
低/中/高复杂度标签
五算法评分柱状图
五算法雷达图
实验结果表格
```

## 4. Tab 3：多智能体推理链页

每个智能体做成可展开卡片：

```text
Data Agent：输入校验结果
Environment Agent：场景分级依据
Literature Agent：引用了哪些文献事实
Knowledge Agent：检索了哪些历史实验记录
Rule Agent：排除了哪些算法，为什么
Evaluation Agent：评分公式和权重
Decision Agent：最终推荐算法
Hypothesis Agent：生成的科学假设
Reflection Agent：可信度检查
Human-loop Agent：人工可修改权重
```

## 5. Tab 4：研究报告页

提供：

```text
完整报告预览
Markdown 下载
PDF 下载
参考文献 BibTeX 下载
实验数据 Excel 下载
Qwen 调用日志摘要
```

## 6. 前端增强优先级

| 优先级 | 功能         | 原因          |
| --- | ---------- | ----------- |
| P0  | 四 Tab 页面   | 最直接体现比赛流程   |
| P0  | 推理链可视化     | 体现多智能体协同    |
| P0  | 研究报告下载     | 对应比赛交付物     |
| P1  | Plotly 交互图 | 展示效果更好      |
| P1  | 多路径同屏对比    | 强化路径规划特色    |
| P2  | 搜索动画       | 演示效果好但非必须   |
| P2  | 批量实验上传     | 增强科研感       |
| P3  | 3D 地图      | 可作为拓展，不建议优先 |

***

# 十一、Phase 8：后端升级路线

基础版可以只用 Python 类调度。优化版建议逐步后端工程化。

## 1. 后端 API 化

使用 FastAPI：

```text
POST /api/analyze
输入地图参数，返回环境分析结果

POST /api/decide
返回五算法评分与推荐算法

POST /api/experiment/run
运行批量实验

POST /api/hypothesis/generate
调用 Qwen 生成科学假设

POST /api/report/generate
生成 Markdown / PDF 报告

GET /api/runs/{run_id}
查询实验状态
```

## 2. 后端模块结构

```text
backend/
├── api/
│   ├── routes_analysis.py
│   ├── routes_decision.py
│   ├── routes_experiment.py
│   └── routes_report.py
│
├── services/
│   ├── agent_service.py
│   ├── experiment_service.py
│   ├── qwen_service.py
│   └── report_service.py
│
├── db/
│   ├── models.py
│   ├── session.py
│   └── migrations/
│
└── workers/
    └── experiment_worker.py
```

## 3. 数据库升级路径

```text
第一阶段：JSON
第二阶段：SQLite
第三阶段：PostgreSQL
第四阶段：PostgreSQL + 向量数据库
```

## 4. RAG 知识库

如果时间充足，增加：

```text
Chroma / FAISS
```

用于存储：

```text
论文摘要
算法适配事实
实验结论
历史报告片段
```

***

# 十二、推荐的最终比赛版系统流程

最终系统演示时建议按下面顺序走：

```text
1. 用户选择一张高复杂度动态随机地图
2. 系统读取地图并计算障碍物占比、连通性、拓扑随机性
3. 文献智能体检索 A*/ACO/PSO/SA/混合算法相关事实
4. 知识库智能体读取历史实验数据库
5. 评估智能体计算五种算法得分
6. 决策智能体推荐最优算法
7. 参数智能体推荐算法超参数
8. 实验智能体运行五算法对比实验
9. 假设智能体生成科学假设
10. 反思智能体检查假设是否被实验支持
11. 报告智能体生成比赛规范的研究计划
12. 前端展示推理链、图表、报告和下载按钮
```

***

# 十三、最小可交付升级版本

如果时间有限，建议至少完成以下内容。

## 必做 1：真实数据

至少接入：

```text
Moving AI 2D Grid Benchmark
自建随机动态地图
```

## 必做 2：实验数据库

至少保存：

```text
地图编号
算法名称
耗时
路径长度
成功率
稳定性
综合得分
```

## 必做 3：文献知识库

至少收集：

```text
A* 相关文献
ACO 相关文献
PSO 相关文献
SA 相关文献
混合优化算法相关文献
Moving AI benchmark 文献
AI Scientist / LLM for Science 文献
```

## 必做 4：新增三个智能体

```text
LiteratureAgent
HypothesisAgent
ReflectionAgent
```

## 必做 5：标准报告输出

严格输出比赛要求的 10 个字段。

***

# 十四、最终建议优先级

## 第一周建议做

```text
1. 接入 Moving AI 2D 数据；
2. 建 SQLite 实验数据库；
3. 批量运行五算法；
4. 生成真实历史性能表；
5. 前端增加数据上传和实验结果展示。
```

## 第二周建议做

```text
1. 接入 Qwen；
2. 增加文献知识库；
3. 增加 LiteratureAgent、HypothesisAgent、ReflectionAgent；
4. 生成标准科学假设与研究计划；
5. 增加 Markdown / PDF 报告导出。
```

## 第三周建议做

```text
1. GUI 美化；
2. 多智能体推理链可视化；
3. 人在回路权重调整；
4. 演示视频录制；
5. 技术方案 PDF 打磨。
```

***

# 十五、一句话总结

你的基础版已经完成了“算法选型”的核心闭环，下一步应重点升级为：

> **以真实 benchmark 和文献知识为输入，以 Qwen 多智能体为推理与假设生成核心，以五类路径规划算法实验为验证手段，最终输出可解释、可验证、可下载的《科学假设与研究计划》的 AI Scientist 系统。**

这样才能从普通工程决策系统，升级为真正符合比赛要求的 **AI Scientist 原型系统**。

***

来源：

- [Moving AI 2D Grid Benchmarks](https://www.movingai.com/benchmarks/grids.html)
- [3D Pathfinding Benchmarks](https://www.movingai.com/benchmarks/voxels.html)
- [OpenStreetMap Copyright and License](https://www.openstreetmap.org/copyright)
- [Geofabrik OpenStreetMap Data Extracts](https://download.geofabrik.de/)
- [Semantic Scholar Academic Graph API](https://api.semanticscholar.org/api-docs/graph)
- [Guide for beginners - Alibaba Cloud Model Studio](https://www.alibabacloud.com/help/en/model-studio/getting-started/quick-start/)

