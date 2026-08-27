# 路径规划虚拟仿真闭环 AI 科学家系统

以 Qwen 大模型为核心的多智能体"AI 科学家"系统，解决 **2D 栅格地图路径规划算法的自适应选型**问题。系统不仅选择算法，更构建了一条完整的科学发现闭环：从地图输入到环境分析、文献检索、五算法统一实验、数据驱动选型、科学假设生成、实验验证、反思修正，最终输出可追溯的研究报告。

本仓库的唯一开发主线是 [`路径规划虚拟仿真闭环AI科学家系统/`](路径规划虚拟仿真闭环AI科学家系统/)。
近期目标是完成可复现、可解释、可演示的 **2D 栅格地图比赛版闭环**。

## 核心特性

- **可复现**：统一随机种子、超时与重复次数，实验结果可复核；每图×算法×重复的种子确定性派生，元启发式算法内部 RNG 全部受种子控制
- **可解释**：LLM 生成选型依据 + 推理链可视化
- **可证伪**：假设含变量/对照/阈值/否证条件/实验计划
- **可追溯**：每条外部结论定位到文献，每条系统结论定位到实验记录；逐次原始运行（run_raw）入库，聚合值可由明细重算
- **诚实失败**：独立路径校验（起终点/邻接/碰撞/越界）区分"算法自报成功"与"校验后成功"；时间预算超时如实标记 timeout
- **离线降级**：无 Qwen API 时实验与选型仍可运行（规则路径兜底）

## 实验可信性机制

| 机制 | 说明 |
|---|---|
| 种子贯通 | 每次运行种子 = base_seed + algo_index×100 + run_idx，地图生成与算法内部 RNG 均受控 |
| 时间预算 | `RUNTIME_BUDGET_S`（low=0.05s / medium=0.5s / high=2.0s，可 env 覆盖），超时协作式中断并打 `timeout` 标记 |
| 逐次原始运行 | `run_raw` 表保存每次运行的种子/耗时/双轨成功/校验原因/几何长度，聚合行与明细自洽 |
| 独立路径校验 | `evaluation/path_validator.py`：Bresenham 逐段碰撞检查，产出 reported/valid_success 双轨 |
| 基准集归一化 | `tools/build_normalization_baseline.py` 预生成各场景等级九维指标区间，评分跨场景可比（缺失时自动降级当批 min/max 并标注） |
| 文献受控导入 | 候选先入 `literature/literature_pending.json` 暂存区，经 `tools/review_literature.py` 人工复核后才进可信库与 RAG 检索 |

## 技术栈

| 类别 | 技术 |
|---|---|
| 核心计算 | numpy、scipy、networkx |
| LLM | Qwen（DashScope OpenAI 兼容接口）、DeepSeek（开发期回退）、OpenAI（可选） |
| Web 服务 | FastAPI + uvicorn（REST API）、Streamlit（GUI） |
| 数据存储 | SQLite（实验数据库）、JSON（知识库/文献库） |
| 可视化 | matplotlib、plotly |
| 文档/报告 | python-docx、pypdfium2、pandas、openpyxl |
| 测试 | pytest |
| 外部检索 | Semantic Scholar Graph API（文献） |

## 目录结构

```
路径规划算法自适应选型多智能体 AI Scientist 系统/
├── README.md                              # 项目说明（本文件）
├── requirements.txt                       # Python 依赖清单
├── .gitignore
│
├── 路径规划虚拟仿真闭环AI科学家系统/          # ★ 唯一开发主线
│   ├── main.py                            # CLI 入口（PathPlanningDecisionSystem）
│   ├── config.py                         # 主配置（LLM/路径/评分权重/规则参数）
│   ├── .env.example                      # 环境变量模板（.env 不提交）
│   ├── agents/                           # 多智能体（21 个 .py，详见下表）
│   ├── algorithms/                       # 五算法实现：A*/ACO/PSO/SA/混合
│   ├── api/                              # FastAPI REST 服务
│   ├── data/                             # 数据管理（ExperimentDB SQLite + experiments/logs/raw）
│   ├── evaluation/                       # 评估引擎（benchmark/metrics/scoring/experiment_runner）
│   ├── gui/                              # Streamlit 界面（4 标签页 + 动画 + 可视化）
│   ├── knowledge_base/                   # 算法画像 + 历史结果 JSON
│   ├── literature/                       # 文献库（literature_kb.json + 数据模型）
│   ├── llm/                              # Qwen 客户端 + Prompt 模板
│   ├── map/                              # 地图层（解析/生成/分析/连通性校验）
│   ├── reports/                          # 报告生成器（generated_reports/ 不提交）
│   ├── tools/                            # 工具脚本（LLM 连通检查/文献导入/冒烟测试）
│   ├── tests/                            # 自动化测试（7 个 .py）
│   ├── utils/                            # 日志配置等工具
│   └── .trae/specs/                      # 6 个 Phase 规范（spec/checklist/tasks）
│
├── docs/                                   # 项目文档
│   ├── PROJECT_INVENTORY.md               # 资产分类清单
│   ├── ROADMAP_2D_GRID_COMPETITION.md     # 2D 栅格比赛路线图
│   ├── ASSET_MANIFEST.md                  # 本地资产位置与恢复校验
│   ├── architecture/                      # 技术边界文档
│   ├── competition/                       # 比赛方案与赛题适配
│   ├── planning/                          # 设计与执行方案（10 个 .md）
│   └── reports/                           # 技术报告蓝图/审计/参考文献
│
├── evidence/                               # 可复核的验证实验结果
│   └── validated_experiments/             # 实验清单/CSV/JSON/NPZ/XLSX
│
├── scripts/                                # 报告生成与审计脚本
│   └── reports/                           # step7~step11 脚本（Python/Node/PowerShell）
│
├── archive/                                # 历史归档
│   └── legacy_trae/                       # 旧版 GUI 升级规划文档
│
├── assets/             [本地 / 不提交]       # 大型资产：地图/文献PDF/报告
│   ├── maps/                              # 126 张地图（MovingAI 城市 + 魔兽3）
│   ├── literature/sources/                # 92 个中文学术论文（.md/.pdf/.caj）
│   └── reports/                           # 系统插图/技术报告/QA 渲染
│
└── archive/legacy_backup/  [本地 / 不提交]   # 完整历史镜像备份
```

> 标注 `[本地 / 不提交]` 的目录已被 `.gitignore` 排除，不会上传到 GitHub。
> `.env`（含 API 密钥）、`.venv/`、`*.sqlite`、`*.log`、`generated_reports/` 同样不提交。

## 核心架构

### 三个对等入口

| 入口 | 文件 | 说明 |
|---|---|---|
| CLI | `main.py` | `PathPlanningDecisionSystem`，串联 6 个核心智能体，跑测试场景 |
| Web GUI | `gui/streamlit_app.py` | 4 标签页：地图参数 / 环境分析 / 智能体推理 / 研究报告 |
| REST API | `api/server.py` | FastAPI，含 `/analyze`、`/experiment`、`/report/{id}`、`/health` |

### 智能体一览

| 智能体 | 文件 | 职责 |
|---|---|---|
| OrchestratorAgent | `orchestrator_agent.py` | 中央调度器，容错串联 12+ 步骤，`ResearchState` 贯穿 |
| DataReceiverAgent | `data_agent.py` | 输入校验，多格式地图解析（.map/.scen/.csv/.npy/.json） |
| MapAnalysisAgent | `map_analysis_agent.py` | 栅格结构特征提取（聚类/瓶颈/熵/目标距离） |
| EnvironmentAgent | `environment_agent.py` | 按障碍率分级复杂度（低/中/高） |
| LiteratureAgent | `literature_agent.py` | 本地 KB + Semantic Scholar 检索 |
| FactExtractionAgent | `fact_extraction_agent.py` | Qwen 抽取文献事实（confidence/evidence_type） |
| KnowledgeRetrievalAgent | `knowledge_agent.py` | SQLite 历史实验聚合查询 |
| RuleConstraintAgent | `rule_agent.py` | 4 条硬规则惩罚（算力/复杂度/连通性） |
| AlgorithmEvaluationAgent | `evaluation_agent.py` | 10 维指标归一化加权评分 |
| DecisionAgent | `decision_agent.py` | 选型决策（best/ranking/scene_level） |
| ParameterAgent | `parameter_agent.py` | 按算力等级缩放推荐运行参数 |
| HumanLoopAgent | `human_loop_agent.py` | 7 条触发条件判定人工复核 |
| ExplanationAgent | `explanation_agent.py` | LLM 可解释选型依据 |
| HypothesisAgent | `hypothesis_agent.py` | Phase 5 结构化科学假设生成 |
| ExperimentAgent | `experiment_agent.py` | 自动实验验证（50 地图 × 5 算法 × 5 重复） |
| ReflectionAgent | `reflection_agent.py` | 7 项硬规则反思检查（confidence_score） |
| CitationAgent | `citation_agent.py` | 报告引用管理 |
| RAG | `rag_agent.py` | 文献 + 历史上下文整合 |
| Pipeline | `pipeline.py` | `ScientificDiscoveryPipeline`，假设-验证-反思闭环 |
| ResearchState | `research_state.py` | 统一快照数据类（env → report 全字段） |

### 三层编排

1. **OrchestratorAgent**（Phase 4）：实例化全部智能体，按 spec 顺序串联，每步 `_safe_step` 容错，失败记入 `metadata["errors"]` 不中断后续步骤
2. **ScientificDiscoveryPipeline**（Phase 5）：`run_full_cycle` → orchestrator → 迭代（Hypothesis → Experiment → Reflection），`confidence_score ≥ 0.7` 收敛，默认最多 3 轮
3. **ResearchState**：统一快照数据类，字段覆盖 `env_input → map_features → literature_facts → algorithm_records → scored_algorithms → decision → recommended_params → hypothesis → experiment_results → reflection → report`

## 算法白名单

A\*、ACO（蚁群）、PSO（粒子群）、SA（模拟退火）、混合优化算法。

## 当前主链路

地图/参数输入 → 环境分析 → 文献与历史实验检索 → 五算法统一实验 →
数据驱动选型与参数推荐 → 科学假设 → 实验验证 → 反思 → 人工复核 → 报告。

## 本地验证

```powershell
cd ".\路径规划虚拟仿真闭环AI科学家系统"
.\.venv\Scripts\python.exe -B -m pytest -p no:cacheprovider tests -q
.\.venv\Scripts\python.exe -B .\main.py

# 重建归一化基准集（参考场景矩阵，约 3 分钟）
.\.venv\Scripts\python.exe -B tools\build_normalization_baseline.py

# 文献导入 → 人工复核 → 入可信库
.\.venv\Scripts\python.exe -B tools\import_literature.py --write
.\.venv\Scripts\python.exe -B tools\review_literature.py --checklist
.\.venv\Scripts\python.exe -B tools\review_literature.py --approve <paper_id> --reviewer <姓名>
```

真实密钥只允许保存在本地 `.env` 或 Streamlit secrets 中，不得提交到 Git。

## 相关文档

- [`docs/PROJECT_INVENTORY.md`](docs/PROJECT_INVENTORY.md) — 资产分类（核心 / 原始研究 / 最终交付 / 生成物）
- [`docs/ROADMAP_2D_GRID_COMPETITION.md`](docs/ROADMAP_2D_GRID_COMPETITION.md) — 2D 栅格比赛建设路线图（P0–P5）
- [`docs/ASSET_MANIFEST.md`](docs/ASSET_MANIFEST.md) — 本地资产位置与恢复校验
- [`docs/architecture/TECHNICAL_BOUNDARY.md`](docs/architecture/TECHNICAL_BOUNDARY.md) — 技术边界

大型地图、文献和二进制报告存放在本地 `assets/`；可复核的小型实验结果位于 `evidence/`。
