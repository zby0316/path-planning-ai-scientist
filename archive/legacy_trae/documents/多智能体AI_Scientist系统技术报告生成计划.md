# 多智能体 AI Scientist 系统技术报告生成计划

## 一、任务概述

**目标**：以 `ai_scientist_path_planning（备份）` 文件夹内的代码内容和本项目 markdown 设计文档为根据，生成一篇结构完整、内容详实的技术报告，输出为 **Word 文档（.docx）**。

**输出文件**：`报告/多智能体AI_Scientist系统技术报告.docx`

---

## 二、当前状态分析

### 2.1 备份代码库（ai_scientist_path_planning（备份））结构
- 50 个 Python 源文件，约 3500+ 行代码
- 19 个智能体（agents/）：OrchestratorAgent、DataReceiverAgent、EnvironmentAgent、MapAnalysisAgent、KnowledgeRetrievalAgent、LiteratureAgent、FactExtractionAgent、CitationAgent、RAGAgent、RuleConstraintAgent、AlgorithmEvaluationAgent、ParameterAgent、DecisionAgent、HumanLoopAgent、ExplanationAgent、HypothesisAgent、ReflectionAgent、ExperimentAgent 等
- 5 种路径规划算法（algorithms/）：A*、ACO、PSO、SA、Hybrid
- 4 个地图模块（map/）：地图生成器、地图解析器、地图分析器、连通性检查器
- 评估系统（evaluation/）：metrics.py、scoring.py、benchmark.py、experiment_runner.py
- LLM 集成（llm/）：qwen_client.py、prompt_templates.py
- Streamlit GUI（gui/）：streamlit_app.py、visualization.py
- FastAPI 后端（api/）：server.py、schemas.py
- 数据层（data/）：data_manager.py、data_card.py、benchmark_loader.py、experiment_db.py
- 报告系统（reports/）：report_generator.py + 3 份已生成报告
- 文献模块（literature/）：models.py、literature_kb.json
- 知识库（knowledge_base/）：algorithm_profile.json、historical_results.json、47 篇论文

### 2.2 设计文档（本项目根目录 markdown 文件）
- 01-路径规划算法自适应选型AI Scientist系统完整设计框架.md（10 智能体设计 + 数据闭环）
- 02-赛题契合度分析与研究方向升级建议.md
- 03-系统优化方案技术选型与技术难点分析.md
- 04-基础版多智能体系统搭建思路与结构框架.md
- 05-基础版MVP全流程搭建执行方案.md（35 文件、1930 行代码细节）
- 06-升级优化完整版系统搭建执行方案.md（9 大优化方向）
- 07-基础版MVP GUI搭建执行方案.md
- 08-优化版MVP GUI搭建执行方案.md
- 基础版与优化版MVP GUI界面设计方案.md
- 基于国产开源大模型的AI科学家研发与应用比赛方案.md
- AI编程智能体优化升级提示词集-完整版.md（35 条提示词、7 Phase）
- 路径规划算法自适应选型AI Scientist系统-升级路线方案.md（8 Phase 路线图）
- TECHNICAL_BOUNDARY.md（技术边界声明）

### 2.3 技术栈
- **语言**：Python 3.9+
- **大模型**：Qwen（阿里云百炼平台），DeepSeek 仅开发测试
- **前端**：Streamlit + Plotly
- **后端**：FastAPI
- **数据库**：SQLite（Phase 2 升级）、JSON（Phase 1）
- **评估指标**：10 维（time, path_length, success_rate, stability, smoothness, safety_score, expanded_nodes, compute_cost, robustness, reproducibility）

---

## 三、技术报告结构设计

### 报告章节规划（约 12-15 页）

| 章节 | 内容 | 信息来源 |
|------|------|----------|
| 封面 | 标题、副标题、日期 | 01 框架文档 + TECHNICAL_BOUNDARY |
| 摘要 | 300 字系统概述 | 综合所有文档 |
| 第1章 引言 | 项目背景、赛题背景、研究意义 | 比赛方案.md + 02 |
| 第2章 系统总体架构 | 分层架构图、数据流、模块依赖关系 | 01/04/06 + 代码结构 |
| 第3章 多智能体设计 | 14 个智能体详细设计（角色/职责/协作方式） | 01/04 + orchestrator_agent.py + research_state.py |
| 第4章 路径规划算法实现 | 5 种算法原理与实现细节 | 05 + algorithms/*.py |
| 第5章 环境建模与地图系统 | 地图生成/解析/分析/连通性、三级复杂度分级 | 01 + map/*.py + config.py |
| 第6章 评估与评分体系 | 10 维指标、归一化、加权评分、规则惩罚、人在回路 | 01/05 + evaluation/*.py + config.py |
| 第7章 大模型集成 | Qwen API 调用、Prompt 工程设计、LLM 在系统中的作用 | 03 + llm/*.py + TECHNICAL_BOUNDARY |
| 第8章 假设-验证-反思闭环 | ResearchState、Pipeline、ExperimentAgent、ReflectionAgent | 06 + pipeline.py + hypothesis_agent.py + reflection_agent.py |
| 第9章 GUI 界面设计 | Streamlit 三栏+Tab 布局、Plotly 可视化 | 07/08 + gui/*.py |
| 第10章 知识库与文献系统 | 论文知识库（47篇）、RAG 检索、CitationAgent | 03/06/升级路线 + literature/*.py |
| 第11章 实验数据库与工程化 | SQLite 数据库、BenchmarkRunner、FastAPI、Docker | 06/升级路线 + data/experiment_db.py + api/*.py |
| 第12章 升级路线与优化方向 | 9 大优化方向、8 Phase 路线图 | 06/升级路线 |
| 第13章 总结与展望 | 系统亮点、局限性、未来方向 | 综合设计文档 |
| 参考文献 | 引用文献列表 | 知识库论文 + 比赛方案参考 |

---

## 四、实施方案

### 4.1 生成工具
- 使用 **python-docx** 库生成 Word 文档
- 先在 `.venv` 中安装：`pip install python-docx`

### 4.2 生成脚本
- 创建独立脚本 `generate_tech_report.py`，位于项目根目录
- 脚本负责：
  1. 创建 `报告/` 输出目录
  2. 设置 Word 文档样式（标题、正文、表格、代码块）
  3. 按章节顺序写入内容
  4. 插入代码引用（从实际源码文件读取关键代码片段）
  5. 生成目录（手动构建）

### 4.3 内容组织策略
- **代码+文档交叉引用**：每个章节同时引用设计文档的描述和实际代码实现
- **代码片段展示**：关键算法和智能体代码以等宽字体代码块展示
- **表格展示**：智能体清单、算法对比、评分权重等用表格
- **流程图用文字描述**：由于 Word 不便于嵌入复杂图形，架构流用文字+编号列表描述

### 4.4 执行步骤

1. 确保 `.venv` 中安装了 `python-docx`
2. 创建 `generate_tech_report.py` 脚本
3. 运行脚本生成 Word 文档
4. 验证输出文档内容完整性

---

## 五、假设与约束

1. **python-docx 需安装**：当前项目未使用该库，需先安装
2. **报告内容基于现有文档与代码**：不引入新知识，严格基于备份代码和设计文档
3. **中文文档**：技术报告使用中文撰写，代码变量名保持英文
4. **页码**：预计 Word 文档 12-15 页
5. **输出位置**：项目根目录下新建 `报告/` 文件夹

---

## 六、验证标准

1. 生成的 `.docx` 文件可在 Microsoft Word / WPS 中正常打开
2. 报告包含所有 13 个章节 + 封面
3. 每个章节至少包含 300+ 字实质性内容
4. 代码引用路径与实际文件一致
5. 报告中涉及的所有数字（智能体数量、文件数、代码行数等）与实际代码库一致
6. 样式统一：正文宋体/小四，标题黑体，代码 Consolas 等宽
