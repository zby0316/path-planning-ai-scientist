# 项目资产清单

更新日期：2026-08-21  
唯一开发主线：`路径规划虚拟仿真闭环AI科学家系统/`  
近期范围：2D 栅格地图比赛版闭环

## A. 核心资产：持续维护

| 位置 | 用途 | 处理原则 |
|---|---|---|
| `路径规划虚拟仿真闭环AI科学家系统/agents/` | 多智能体编排、假设、实验、反思、人在回路 | 核心源码 |
| `algorithms/`、`map/`、`evaluation/` | 五算法、2D 地图、统一基准与评分 | 核心实验引擎 |
| `data/experiment_db.py`、`data/experiments/` | 实验落盘及已有基线 | 数据库文件本地保留、不提交 |
| `api/`、`gui/`、`main.py` | API、比赛演示界面、命令行入口 | 后续统一服务层 |
| `tests/`、`test_full_pipeline.py`、`test_llm.py` | 自动验证与外部能力检查 | 扩充覆盖率 |
| `knowledge_base/`、`literature/` | 算法画像、历史数据、正式文献元数据 | 仅接收可追溯、已复核数据 |
| 主线 `.trae/specs/` | 阶段规范与验收条件 | 保留并逐步迁入正式文档 |

## B. 原始研究资产：保留并接入

| 位置 | 现状 | 下一步 |
|---|---|---|
| `assets/maps/` | 126 张 MovingAI 2D 地图，尚未接入主数据目录 | 建立清单、场景划分和统一加载器 |
| `assets/literature/` | PDF/Markdown 原文池，含重复及领域噪声 | 哈希去重、2D 范围筛选、人工核验 |
| `evidence/validated_experiments/` | 已验证实验表和可视化输入 | 作为比赛证据，补生成脚本与版本信息 |
| 顶层方案文档、`赛题适配改造文档/` | 设计历史和比赛约束 | 只归档，不作为运行时配置 |

## C. 最终交付资产：保留

- `assets/reports/final/路径规划虚拟仿真闭环AI科学家系统技术报告_比赛项目版.docx`
- `docs/reports/路径规划虚拟仿真闭环AI科学家系统技术报告_正文源稿.md`
- 最终 BibTeX、引用映射、审计结论、最终实验数据和图表。
- `assets/reports/qa/render_step11/` 暂保留为最终视觉 QA 证据。

## D. 生成物与本地状态：不提交 Git

- `.env`、`.venv/`、`__pycache__/`、`.pytest_cache/`、日志。
- SQLite 运行数据库、`reports/generated_reports/`。
- 报告逐页渲染和工作簿 QA 中间产物。
- 迁移期间暂存的 `archive/legacy_backup/`。

## E. 已核实的重要差异

- 主线 GUI 是功能更完整的版本，不能被备份 GUI 覆盖。
- 备份中的 47 篇 Markdown 与顶层 `文献/` 原件逐一哈希相同，无需复制。
- 备份的 52 条文献知识库含 OCR 标题错误和领域噪声，不并入正式 RAG。
- 主线现有 5 篇正式文献记录保持不变；新记录必须先进入 `pending` 复核状态。
- 程序当前依赖启动工作目录；从父目录运行会找不到知识库。
- 当前没有历史 Git 提交；2026-08-21 起以新仓库追踪后续变化。
