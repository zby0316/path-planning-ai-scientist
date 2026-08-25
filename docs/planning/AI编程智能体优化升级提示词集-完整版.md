# 路径规划算法自适应选型 AI Scientist 系统 — AI 编程智能体优化升级提示词集

## 目录

### Phase 0：合规体检与基础版封版（4 条）

- [提示词 0-1：统一项目定位与技术文档](#提示词-0-1统一项目定位与技术文档)
- [提示词 0-2：统一 LLM 客户端命名与注释](#提示词-0-2统一-llm-客户端命名与注释)
- [提示词 0-3：强化 Data Agent 输入校验](#提示词-0-3强化-data-agent-输入校验)
- [提示词 0-4：修复 config.py 中文注释与类型提示](#提示词-0-4修复-configpy-中文注释与类型提示)

### Phase 1：数据输入升级（5 条）

- [提示词 1-1：创建目录结构与数据目录初始化模块](#提示词-1-1创建目录结构与数据目录初始化模块)
- [提示词 1-2：创建多格式地图文件解析器](#提示词-1-2创建多格式地图文件解析器)
- [提示词 1-3：创建 Moving AI Benchmark 下载与加载模块](#提示词-1-3创建-moving-ai-benchmark-下载与加载模块)
- [提示词 1-4：创建 Data Card 自动生成器](#提示词-1-4创建-data-card-自动生成器)
- [提示词 1-5：更新 Data Agent 支持文件输入](#提示词-1-5更新-data-agent-支持文件输入)

### Phase 2：实验数据库与指标体系升级（4 条）

- [提示词 2-1：创建 SQLite 实验数据库模块](#提示词-2-1创建-sqlite-实验数据库模块)
- [提示词 2-2：扩展评估指标体系（4→10 指标）](#提示词-2-2扩展评估指标体系410-指标)
- [提示词 2-3：更新评分函数适配新指标体系](#提示词-2-3更新评分函数适配新指标体系)
- [提示词 2-4：创建批量实验矩阵运行器](#提示词-2-4创建批量实验矩阵运行器)

### Phase 3：文献知识库与 RAG 升级（5 条）

- [提示词 3-1：创建文献数据模型与知识库结构](#提示词-3-1创建文献数据模型与知识库结构)
- [提示词 3-2：创建文献检索智能体 LiteratureAgent](#提示词-3-2创建文献检索智能体-literatureagent)
- [提示词 3-3：创建科学事实抽取智能体 FactExtractionAgent](#提示词-3-3创建科学事实抽取智能体-factextractionagent)
- [提示词 3-4：创建引用核验智能体 CitationAgent](#提示词-3-4创建引用核验智能体-citationagent)
- [提示词 3-5：创建 RAG 智能体与升级 KnowledgeAgent](#提示词-3-5创建-rag-智能体与升级-knowledgeagent)

### Phase 4：多智能体协同升级（5 条）

- [提示词 4-1：创建全局研究状态对象 ResearchState](#提示词-4-1创建全局研究状态对象-researchstate)
- [提示词 4-2：创建地图分析智能体 MapAnalysisAgent](#提示词-4-2创建地图分析智能体-mapanalysisagent)
- [提示词 4-3：升级 Orchestrator 为完整 12 智能体调度器](#提示词-4-3升级-orchestrator-为完整-12-智能体调度器)
- [提示词 4-4：升级 HumanLoopAgent 触发条件（7 种触发）](#提示词-4-4升级-humanloopagent-触发条件7-种触发)
- [提示词 4-5：创建反思智能体 ReflectionAgent](#提示词-4-5创建反思智能体-reflectionagent)

### Phase 5：假设生成—实验验证闭环（4 条）

- [提示词 5-1：升级 HypothesisAgent 生成可验证科学假设](#提示词-5-1升级-hypothesisagent-生成可验证科学假设)
- [提示词 5-2：创建实验验证智能体 ExperimentAgent](#提示词-5-2创建实验验证智能体-experimentagent)
- [提示词 5-3：构建假设-验证-反思闭环流水线](#提示词-5-3构建假设-验证-反思闭环流水线)
- [提示词 5-4：创建标准化研究报告生成器](#提示词-5-4创建标准化研究报告生成器)

### Phase 6：前端展示与人在回路升级（4 条）

- [提示词 6-1：升级 Streamlit Tab 1（地图与数据输入）](#提示词-6-1升级-streamlit-tab-1地图与数据输入)
- [提示词 6-2：升级 Streamlit Tab 2（环境分析与算法评分）](#提示词-6-2升级-streamlit-tab-2环境分析与算法评分)
- [提示词 6-3：升级 Streamlit Tab 3（多智能体推理链）](#提示词-6-3升级-streamlit-tab-3多智能体推理链)
- [提示词 6-4：升级 Streamlit Tab 4（科学假设与研究报告）](#提示词-6-4升级-streamlit-tab-4科学假设与研究报告)

### Phase 7：后端工程化与部署（4 条）

- [提示词 7-1：添加日志系统](#提示词-7-1添加日志系统)
- [提示词 7-2：创建 FastAPI 后端服务](#提示词-7-2创建-fastapi-后端服务)
- [提示词 7-3：完善配置管理与环境变量](#提示词-7-3完善配置管理与环境变量)
- [提示词 7-4：创建 Docker 部署配置](#提示词-7-4创建-docker-部署配置)

***

# Phase 0：合规体检与基础版封版（4 条提示词）

***

### 提示词 0-1：统一项目定位与技术文档

**操作目标**：在 README 和 config.py 中明确系统定位为"基于 Qwen 多智能体的 AI Scientist 系统"，并添加技术边界说明及模型选型背景。

**涉及文件**：

- `config.py`（修改）
- 项目根目录创建 `TECHNICAL_BOUNDARY.md`（新建）

**功能改进点**：

1. 在 `config.py` 顶部添加项目全称注释：`基于 Qwen 多智能体系统的动态随机地图路径规划算法适配边界发现与科学假设生成系统`
2. 新建 `TECHNICAL_BOUNDARY.md`，包含以下声明：
   - 本系统以 Qwen 大模型作为多智能体架构的核心基础模型，所有智能体推理、决策与生成任务均基于 Qwen 实现
   - DeepSeek 模型仅在系统开发初期、尚未获取 Qwen API 访问权限时，被临时用于功能测试与流程验证，并非系统的正式基础模型
   - 最终算法选择由可复现实验数据和评分函数决定，Qwen 智能体不直接选择算法
   - 允许的算法集合限制为 A\*、ACO、PSO、SA、混合优化算法
   - Qwen 智能体负责：解释选型依据、从文献抽取事实、生成科学假设、生成实验计划、撰写研究报告、充当反思智能体

**验证标准**：

- `config.py` 第 1 行包含完整项目名称注释
- 项目根目录存在 `TECHNICAL_BOUNDARY.md` 文件，包含上述 5 条边界声明

***

### 提示词 0-2：统一 LLM 客户端命名与注释

**操作目标**：统一 `qwen_client.py` 内的注释和文档字符串，明确系统实际以 Qwen API 为核心基础模型，并补充说明 DeepSeek 仅在开发初期被临时用于功能测试验证。

**涉及文件**：

- `llm/qwen_client.py`（修改）

**功能改进点**：

1. 文件头部 docstring 更新为：`Qwen API 客户端（本系统核心基础模型为 Qwen 大模型；开发初期曾临时使用 DeepSeek API 进行功能测试验证，待获取 Qwen API 权限后即切换为正式方案）`
2. `QwenClient` 类的 docstring 更新，说明"本系统以 Qwen 大模型为智能体核心基础模型，对外统一称为 Qwen 多智能体系统"
3. 在 `__init__` 方法中添加注释说明：
   - API Key 获取方式与环境变量要求
   - DeepSeek 仅在开发初期临时用于功能测试，正式部署以 Qwen API 为准

**验证标准**：

- 阅读 `llm/qwen_client.py` 前 10 行，确认所有注释已更新且准确反映 Qwen 为核心、DeepSeek 为临时测试方案的技术选型
- 运行 `python -c "from llm.qwen_client import QwenClient; print('import OK')"` 确认导入正常

***

### 提示词 0-3：强化 Data Agent 输入校验

**操作目标**：扩展 `data_agent.py`，增加对 `dynamic_change_rate`、`start_point`、`target_point` 可选字段的类型校验，并输出结构化校验报告。

**涉及文件**：

- `agents/data_agent.py`（修改）

**功能改进点**：

1. 新增 `OPTIONAL_FIELDS` 列表：`["start_point", "target_point", "dynamic_change_rate"]`
2. `validate` 方法增加对可选字段的类型检查：`start_point`/`target_point` 如果存在，必须为 `[int, int]` 格式；`dynamic_change_rate` 如果存在，必须在 0\~1 之间
3. 校验通过后在 `env` 字典中添加字段 `input_validated: True` 和 `validation_timestamp`
4. 捕获所有校验异常后包装为统一的 `ValueError`，附带字段名和非法值信息

**验证标准**：

- 运行 `python -c "from agents.data_agent import DataReceiverAgent; a=DataReceiverAgent(); r=a.validate({'obstacle_ratio':0.3,'map_width':100,'map_height':100,'connectivity':0.6,'topology_randomness':0.5,'compute_limit':'medium'}); print(r.get('input_validated'))"` 输出 True
- 传入 `start_point: "invalid"` 时抛出 ValueError

***

### 提示词 0-4：修复 config.py 中文注释与类型提示

**操作目标**：为 `config.py` 中所有配置常量添加中文注释说明其含义和取值范围。

**涉及文件**：

- `config.py`（修改）

**功能改进点**：

1. 每个阈值常量后添加中文注释，格式：`# 含义（取值范围/单位）`
2. `WEIGHTS` 字典中每个嵌套键添加注释说明子指标含义
3. `ALGORITHM_PROFILE_PATH` 和 `HISTORICAL_RESULTS_PATH` 旁添加注释说明文件格式

**验证标准**：

- 打开 `config.py`，每行配置都有中文注释，且注释不重复、不矛盾
- `python -c "import config; print('config OK')"` 无报错

***

# Phase 1：数据输入升级（5 条提示词）

***

### 提示词 1-1：创建目录结构与数据目录初始化模块

**操作目标**：在 `data/` 下创建完整的子目录结构，并新建 `data/data_manager.py` 负责目录自动创建与路径管理。

**涉及文件**：

- `data/` 目录下创建子目录：`raw/movingai_2d/`, `raw/movingai_3d/`, `raw/osm/`, `raw/uploaded/`, `processed/grid_maps/`, `processed/topology_graphs/`, `processed/dynamic_maps/`, `experiments/`, `literature/raw_pdf/`, `literature/metadata/`, `literature/extracted_facts/`, `literature/references/`
- `data/__init__.py`（修改，添加 data\_manager 导入）
- `data/data_manager.py`（新建）

**功能改进点**：

1. `data_manager.py` 中的 `DataManager` 类在初始化时自动创建所有上述子目录（使用 `pathlib.Path.mkdir(parents=True, exist_ok=True)`）
2. 提供 `get_path(category)` 方法根据类别名称返回对应路径
3. 提供 `list_files(category, pattern)` 方法列出某类数据目录下的文件
4. 提供 `ensure_dir(path)` 静态方法供其他模块使用

**验证标准**：

- 运行 `python -c "from data.data_manager import DataManager; dm=DataManager(); print(dm.get_path('movingai_2d'))"` 输出正确路径
- 检查 `data/raw/movingai_2d/` 目录已存在

***

### 提示词 1-2：创建多格式地图文件解析器

**操作目标**：新建 `map/map_parser.py`，支持解析 `.map`（Moving AI 格式）、`.scen`（Moving AI 场景文件）、CSV 栅格地图、JSON 栅格地图、`.npy` NumPy 地图五种格式。

**涉及文件**：

- `map/map_parser.py`（新建）
- `map/__init__.py`（修改，添加 MapParser 导入）

**功能改进点**：

1. `MapParser` 类提供 `parse(filepath)` 方法，根据文件扩展名自动分发到对应解析器
2. `.map` 格式解析：读取 height、width、map 行，返回 numpy 2D 数组（`.` = 可通行 0, `@`/`O`/`T`/`W` = 障碍 1）
3. `.scen` 格式解析：读取 Bucket 行后的任务行，返回包含 `start_x, start_y, target_x, target_y, optimal_length` 的字典列表
4. CSV 解析：逗号分隔的 0/1 矩阵
5. JSON 解析：二维数组 JSON
6. `.npy` 解析：`np.load()`
7. 所有解析器返回统一格式：`{"grid": np.ndarray, "metadata": dict, "tasks": list}`
8. 不支持格式抛出 `ValueError(f"不支持的地图格式: {ext}")`

**验证标准**：

- 准备一个 3×3 的 CSV 文件内容 `0,0,0\n0,1,0\n0,0,0`，保存到 `data/raw/uploaded/test.csv`，运行解析器确认返回 shape 为 (3,3) 且中间为 1 的 numpy 数组
- 调用 `.parse("test.xyz")` 抛出 ValueError

***

### 提示词 1-3：创建 Moving AI Benchmark 下载与加载模块

**操作目标**：新建 `data/benchmark_loader.py`，支持从 Moving AI 网站下载公开 benchmark 地图并自动解析入库。

**涉及文件**：

- `data/benchmark_loader.py`（新建）
- `data/__init__.py`（修改）
- `requirements.txt`（修改，如需要添加 `wget` 或使用内置 `urllib`）

**功能改进点**：

1. `BenchmarkLoader` 类初始化接收 `DataManager` 实例，确定存储路径
2. `download_movingai_2d(map_name)` 方法：下载指定地图集的 `.map` 和 `.map.scen` 文件到 `data/raw/movingai_2d/`
   - 使用 Python 标准库 `urllib.request`，基础 URL：`https://www.movingai.com/benchmarks/grids/`
   - 下载前检查文件是否已存在，避免重复下载
3. `load_map(map_name)` 方法：调 `MapParser` 解析已下载的地图
4. `list_available_maps()` 返回推荐的地图集列表：`["dao/arena", "dao/arena2", "dao/brc000d", "dao/brc300d", "dao/brc600d", "dao/den000d", "dao/den300d", "dao/den600d", "dao/den900d"]`
5. 每次下载后记录 `download_log.json`：包含时间戳、文件名、URL、文件大小

**验证标准**：

- 运行 `python -c "from data.benchmark_loader import BenchmarkLoader; bl=BenchmarkLoader(); print(bl.list_available_maps()[:3])"` 输出至少 3 个地图集名称
- 手动调用 `download_movingai_2d("dao/arena")` 确认文件下载到 `data/raw/movingai_2d/` 目录

***

### 提示词 1-4：创建 Data Card 自动生成器

**操作目标**：新建 `data/data_card.py`，为每个导入的数据集自动生成标准化的 `data_card.md` 描述文件。

**涉及文件**：

- `data/data_card.py`（新建）
- `data/__init__.py`（修改）

**功能改进点**：

1. `DataCardGenerator` 类提供 `generate(dataset_name, source, download_url, license_info, map_type, map_count, task_count, purpose, preprocessing, reproducible)` 方法
2. 生成的 `data_card.md` 包含 10 个字段，格式如下：
   ```markdown
   # 数据卡：{dataset_name}
   - **数据集名称**：{dataset_name}
   - **来源**：{source}
   - **下载链接**：{download_url}
   - **许可协议**：{license_info}
   - **地图类型**：{map_type}
   - **地图数量**：{map_count}
   - **起终点任务数量**：{task_count}
   - **使用目的**：{purpose}
   - **预处理方式**：{preprocessing}
   - **是否可复现**：{reproducible}
   ```
3. 文件保存到 `data/raw/{category}/data_card.md`
4. 提供 `generate_from_movingai(map_name)` 快捷方法，自动填充 Moving AI 相关信息（来源=<https://www.movingai.com/benchmarks/grids.html，许可=学术使用）>

**验证标准**：

- 运行生成器后检查 `data/raw/movingai_2d/` 目录下存在 `data_card.md` 文件，内容包含 10 个字段

***

### 提示词 1-5：更新 Data Agent 支持文件输入

**操作目标**：修改 `agents/data_agent.py`，使其能够接受文件路径输入，自动调用 `MapParser` 解析并从地图中提取环境参数。

**涉及文件**：

- `agents/data_agent.py`（修改）

**功能改进点**：

1. 在 `validate` 方法中新增可选参数 `map_filepath: str = None`
2. 如果 `map_filepath` 存在，调用 `MapParser.parse(map_filepath)` 获取 grid 和 metadata
3. 从 grid 中自动计算 `obstacle_ratio`（如用户未提供）：`np.count_nonzero(grid == 1) / grid.size`
4. 从 grid.shape 中自动设置 `map_height` 和 `map_width`（如用户未提供）
5. 如果 `.scen` 文件被解析，自动读取第一个任务的 start/target 坐标填充 `start_point`/`target_point`
6. `env` 字典增加 `data_source` 字段，记录数据来源类型（`"manual_params"` / `"map_file"` / `"benchmark"`）

**验证标准**：

- 准备一个 50×50 的 CSV 栅格地图（20% 障碍物），调用 `validate({..., "compute_limit":"medium"}, map_filepath="test.csv")`，确认 `obstacle_ratio` 自动计算正确
- `data_source` 字段值为 `"map_file"`

***

# Phase 2：实验数据库与指标体系升级（4 条提示词）

***

### 提示词 2-1：创建 SQLite 实验数据库模块

**操作目标**：新建 `data/experiment_db.py`，将实验数据从 JSON 迁移到 SQLite，支持结构化查询和历史记录管理。

**涉及文件**：

- `data/experiment_db.py`（新建）
- `data/__init__.py`（修改）
- `requirements.txt`（无需修改，sqlite3 是标准库）

**功能改进点**：

1. `ExperimentDB` 类初始化时在 `data/experiments/experiments.sqlite` 创建数据库连接
2. 自动建表（3 张表）：
   - `maps` 表：`map_id TEXT PK, source TEXT, map_type TEXT, width INTEGER, height INTEGER, obstacle_ratio REAL, connectivity REAL, topology_randomness REAL, dynamic_change_rate REAL, created_at TEXT`
   - `algorithm_runs` 表：`run_id TEXT PK, map_id TEXT FK, algorithm TEXT, parameters TEXT, runtime REAL, path_length REAL, success INTEGER, expanded_nodes INTEGER, turning_points INTEGER, smoothness REAL, safety_score REAL, stability_score REAL, compute_limit TEXT, seed INTEGER, created_at TEXT`
   - `hypotheses` 表：`hypothesis_id TEXT PK, scene_condition TEXT, hypothesis_text TEXT, generated_by TEXT, evidence TEXT, validation_status TEXT, created_at TEXT`
3. 提供 CRUD 方法：`insert_map()`, `insert_run()`, `insert_hypothesis()`, `query_runs_by_map()`, `query_runs_by_algorithm()`, `query_runs_by_scene()`
4. 提供 `get_statistics()` 方法：返回总地图数、总实验次数、各算法平均性能
5. 提供 `import_from_json(json_filepath)` 方法：将 `historical_results.json` 数据导入 SQLite

**验证标准**：

- 运行 `python -c "from data.experiment_db import ExperimentDB; db=ExperimentDB(); db.import_from_json('knowledge_base/historical_results.json'); print(db.get_statistics())"` 输出统计信息
- 确认 `data/experiments/experiments.sqlite` 文件已创建且包含数据

***

### 提示词 2-2：扩展评估指标体系（4→10 指标）

**操作目标**：修改 `evaluation/metrics.py`，将原有 4 个指标扩展为 10 个指标。

**涉及文件**：

- `evaluation/metrics.py`（修改）

**功能改进点**：

1. `evaluate_algorithm` 函数签名增加参数：`grid: np.ndarray`（原有）、`compute_limit: str = "medium"`
2. 返回值从 4 个字段扩展为 10 个字段：
   - `avg_time`：平均耗时（保留）
   - `avg_path_length`：路径长度（保留）
   - `success_rate`：成功率（保留）
   - `stability_score`：时间稳定性（保留，= 1 - std/mean）
   - **新增** **`smoothness`**：路径平滑度 = 路径总转角数 / 路径长度（转角越多越不平滑）
   - **新增** **`safety_score`**：安全得分 = 路径各点与最近障碍物的平均距离 / max(地图宽,高)
   - **新增** **`expanded_nodes`**：搜索过程中扩展的节点数（算法需返回该字段）
   - **新增** **`turning_points`**：路径中的转折点数量
   - **新增** **`compute_cost`**：算力消耗代理指标 = `expanded_nodes * log(expanded_nodes+1) / 10000` 归一化到 0\~1
   - **新增** **`robustness`**：动态扰动下性能保持能力 = 在 3 次动态变化中仍成功完成路径的比例
3. 各算法接口需在返回结果中新增 `expanded_nodes` 和 `turning_points` 字段（如果算法未返回，`expanded_nodes` 默认为 0，`turning_points` 从路径推算）

**验证标准**：

- 运行 `python -c "from evaluation.metrics import evaluate_algorithm; from algorithms.astar import AStar; import numpy as np; g=np.zeros((10,10),dtype=np.int8); r=evaluate_algorithm(AStar().search,g,(0,0),(9,9),n_runs=3); print(len(r))"` 输出 10（10 个指标字段）
- 检查 `smoothness`、`safety_score`、`expanded_nodes`、`turning_points`、`compute_cost`、`robustness` 字段均存在

***

### 提示词 2-3：更新评分函数适配新指标体系

**操作目标**：修改 `evaluation/scoring.py` 和 `agents/evaluation_agent.py`，支持 10 维指标评分。

**涉及文件**：

- `evaluation/scoring.py`（修改）
- `agents/evaluation_agent.py`（修改）
- `config.py`（修改，扩展 WEIGHTS 字典）

**功能改进点**：

1. `config.py` 中 `WEIGHTS` 字典扩展为 10 维权重（每场景等级）：
   ```python
   WEIGHTS = {
       "低复杂度": {"time": 0.25, "path_length": 0.20, "success_rate": 0.15, "stability": 0.08,
                    "smoothness": 0.08, "safety_score": 0.08, "expanded_nodes": 0.05,
                    "compute_cost": 0.05, "robustness": 0.06},
       # ... 中/高复杂度类似调整
   }
   ```
2. `evaluation/scoring.py` 中 `compute_score` 函数扩展为 10 维评分
3. `evaluation_agent.py` 中 `score` 方法同步更新，归一化逻辑扩展：对于 `smoothness`、`expanded_nodes`、`compute_cost` 使用逆向归一化（越小越好），对于 `safety_score`、`robustness` 使用正向归一化（越大越好）

**验证标准**：

- 运行现有测试：`python -m pytest tests/test_scoring.py -v`，确认评分逻辑正常
- 打印评分详情时包含 10 个子维度得分

***

### 提示词 2-4：创建批量实验矩阵运行器

**操作目标**：新建 `evaluation/experiment_runner.py`，支持 3×3×3 实验矩阵自动运行。

**涉及文件**：

- `evaluation/experiment_runner.py`（新建）
- `evaluation/__init__.py`（修改）

**功能改进点**：

1. `ExperimentRunner` 类：
   - 构造函数接收 `ExperimentDB` 实例
   - `run_matrix()` 方法：自动生成 3（复杂度）× 3（规模）× 3（算力）= 27 组实验配置
     - 复杂度：obstacle\_ratio ∈ {0.15, 0.35, 0.65}
     - 规模：{(50,50), (100,100), (200,200)}
     - 算力：{"low", "medium", "high"}
   - 每组生成 10 张随机地图，每张地图运行 5 种算法 × 3 次重复
   - 如果时间有限，提供 `run_quick()` 方法：3 复杂度 × 10 地图 × 5 算法 = 150 次运行
2. 所有结果自动存入 `ExperimentDB`
3. 提供 `generate_summary_xlsx(filepath)` 方法：导出 `benchmark_summary.xlsx` 到 `data/experiments/`
4. 提供 `generate_failure_cases(filepath)` 方法：将 success=0 的案例导出为 `failure_cases.jsonl`

**验证标准**：

- 运行 `python -c "from evaluation.experiment_runner import ExperimentRunner; er=ExperimentRunner(); er.run_quick()"` 确认 150 次运行完成
- 检查 `data/experiments/experiments.sqlite` 中 `algorithm_runs` 表新增了记录

***

# Phase 3：文献知识库与 RAG 升级（5 条提示词）

***

### 提示词 3-1：创建文献数据模型与知识库结构

**操作目标**：新建 `literature/` 模块，定义文献数据模型并创建文献知识库 JSON 存储。

**涉及文件**：

- `literature/__init__.py`（新建）
- `literature/models.py`（新建）
- `literature/literature_kb.json`（新建，至少预置 5 篇真实文献）

**功能改进点**：

1. `models.py` 中定义 `PaperRecord` 数据类：
   ```python
   @dataclass
   class PaperRecord:
       paper_id: str
       title: str
       authors: list
       year: int
       venue: str
       doi: str
       url: str
       algorithm_related: list  # ["A*", "ACO"] 等
       key_facts: list  # ["A* 在静态栅格地图中具有较高效率", ...]
       evidence_level: str  # "review" / "paper" / "benchmark"
       citation_bibtex: str
   ```
2. `literature_kb.json` 预置至少 5 篇真实可核验文献：
   - 至少 1 篇 A\* 相关（如 Hart, Nilsson, Raphael 1968）
   - 至少 1 篇 ACO 相关（如 Dorigo 1996 或后续综述）
   - 至少 1 篇 Moving AI benchmark 相关（Sturtevant 2012）
   - 至少 1 篇混合优化路径规划相关
   - 至少 1 篇 AI Scientist/LLM for Science 相关
3. 每条文献必须包含真实的 title、authors、year、DOI/URL

**验证标准**：

- 运行 `python -c "from literature.models import PaperRecord; print(PaperRecord.__dataclass_fields__.keys())"` 输出字段列表
- 打开 `literature/literature_kb.json`，手动验证 5 篇文献的 DOI 可访问、作者与标题真实

***

### 提示词 3-2：创建文献检索智能体 LiteratureAgent

**操作目标**：新建 `agents/literature_agent.py`，实现基于关键词的文献检索与 Semantic Scholar API 集成。

**涉及文件**：

- `agents/literature_agent.py`（新建）
- `agents/__init__.py`（修改）
- `requirements.txt`（无需修改，使用 requests）

**功能改进点**：

1. `LiteratureAgent` 类：
   - `__init__` 加载 `literature/literature_kb.json` 到内存
   - `search_local(keywords: list)` 方法：在本地知识库中按算法名称和关键词模糊匹配，返回匹配的 PaperRecord 列表
   - `search_semantic_scholar(query: str, limit: int = 5)` 方法：调用 Semantic Scholar API (`https://api.semanticscholar.org/graph/v1/paper/search?query=...`) 搜索
   - `get_paper_facts(algorithm: str)` 方法：返回与该算法相关的所有 `key_facts`
   - `add_paper(paper: PaperRecord)` 方法：将新文献追加到本地知识库 JSON 文件
2. 如果 Semantic Scholar API 不可用（网络问题），降级为仅本地搜索并记录 warning

**验证标准**：

- 运行 `python -c "from agents.literature_agent import LiteratureAgent; la=LiteratureAgent(); facts=la.get_paper_facts('A*'); print(len(facts))"` 输出大于 0 的数值
- 运行 `python -c "from agents.literature_agent import LiteratureAgent; la=LiteratureAgent(); results=la.search_local(['A*', 'grid']); print(len(results))"` 输出至少 1 篇文献

***

### 提示词 3-3：创建科学事实抽取智能体 FactExtractionAgent

**操作目标**：新建 `agents/fact_extraction_agent.py`，使用 LLM 从文献摘要/全文片段中抽取算法适配性事实。

**涉及文件**：

- `agents/fact_extraction_agent.py`（新建）
- `agents/__init__.py`（修改）
- `llm/prompt_templates.py`（修改，添加事实抽取 Prompt）

**功能改进点**：

1. `FactExtractionAgent` 类：
   - 构造函数接收 `QwenClient` 实例
   - `extract(abstract: str, algorithm_names: list)` 方法：将摘要发送给 LLM，要求从中提取与指定算法相关的事实陈述
   - 使用新的 Prompt 模板 `FACT_EXTRACTION_SYSTEM_PROMPT` 和 `FACT_EXTRACTION_USER_TEMPLATE`
2. `prompt_templates.py` 新增两个 Prompt 模板：
   - `FACT_EXTRACTION_SYSTEM_PROMPT`：要求 LLM 以 JSON 格式输出事实列表，每项包含 `algorithm`、`fact`、`confidence`（0\~1）、`evidence_type`（"claimed"/"experimental"/"theoretical"）
   - `FACT_EXTRACTION_USER_TEMPLATE`：包含 `{abstract}` 和 `{algorithms}` 占位符
3. 提供 `batch_extract(papers: list, algorithm_names: list)` 批量处理方法
4. 结果自动追加到 `data/literature/extracted_facts/extracted_facts.jsonl`

**验证标准**：

- 运行 `python -c "from agents.fact_extraction_agent import FactExtractionAgent; fa=FactExtractionAgent(); facts=fa.extract('The A* algorithm finds optimal paths in static grid maps efficiently with admissible heuristics.', ['A*']); print(facts)"` 输出包含算法事实的列表

***

### 提示词 3-4：创建引用核验智能体 CitationAgent

**操作目标**：新建 `agents/citation_agent.py`，负责核验文献引用的真实性，禁止生成不存在的参考文献。

**涉及文件**：

- `agents/citation_agent.py`（新建）
- `agents/__init__.py`（修改）

**功能改进点**：

1. `CitationAgent` 类：
   - `verify(paper: dict)` 方法：通过检查 paper 是否包含 `title`、`authors`、`year`、`doi` 或 `url` 字段来核验引用完整性
   - `validate_references(references: list)` 方法：批量核验，返回 `{"valid": [...], "invalid": [...]}`
   - `check_doi_exists(doi: str)` 方法：尝试通过 `https://doi.org/` API 验证 DOI 是否可解析（HEAD 请求）
   - `generate_bibtex(paper: dict)` 方法：根据字段自动生成 BibTeX 格式引用
2. 核验规则：
   - 缺少 title 或 authors → 标记为 invalid
   - 同时缺少 doi 和 url → 标记为 suspicious
   - DOI 无法解析 → 标记为 invalid
   - 全部通过 → 标记为 valid

**验证标准**：

- 运行 `python -c "from agents.citation_agent import CitationAgent; ca=CitationAgent(); result=ca.validate_references([{'title':'Test','authors':['A'],'year':2020,'doi':'10.1000/xyz'}])"` 确认核验逻辑执行
- 传入空 dict 时返回 `invalid`

***

### 提示词 3-5：创建 RAG 智能体与升级 KnowledgeAgent

**操作目标**：新建 `agents/rag_agent.py` 并修改 `agents/knowledge_agent.py`，整合文献知识检索与历史实验数据检索。

**涉及文件**：

- `agents/rag_agent.py`（新建）
- `agents/knowledge_agent.py`（修改）
- `agents/__init__.py`（修改）

**功能改进点**：

1. `RAGAgent` 类：
   - `__init__` 接收 `LiteratureAgent`、`FactExtractionAgent`、`ExperimentDB` 实例
   - `retrieve(scene_level: str, algorithm: str)` 方法：同时检索文献事实和历史实验数据，返回结构化上下文
   - 返回格式：`{"literature_facts": [...], "historical_performance": {...}, "relevant_papers": [...]}`
2. 修改 `KnowledgeRetrievalAgent`：
   - `__init__` 改为接收可选的 `ExperimentDB` 实例，优先从 SQLite 查询
   - 如无 SQLite 数据，回退到 `historical_results.json`
   - `retrieve` 方法增加 `include_literature: bool = False` 参数
   - 当 `include_literature=True` 时，同时调用 `LiteratureAgent.get_paper_facts()` 获取文献支撑

**验证标准**：

- 运行 `python -c "from agents.knowledge_agent import KnowledgeRetrievalAgent; ka=KnowledgeRetrievalAgent(); records=ka.retrieve('高复杂度'); print(len(records))"` 输出 5（5 种算法记录）
- 运行 `python -c "from agents.rag_agent import RAGAgent; ra=RAGAgent(); ctx=ra.retrieve('高复杂度','ACO'); print('literature_facts' in ctx)"` 输出 True

***

# Phase 4：多智能体协同升级（5 条提示词）

***

### 提示词 4-1：创建全局研究状态对象 ResearchState

**操作目标**：新建 `agents/research_state.py`，定义贯穿所有智能体的统一数据模型。

**涉及文件**：

- `agents/research_state.py`（新建）
- `agents/__init__.py`（修改）

**功能改进点**：

1. 使用 `@dataclass` 定义 `ResearchState`：
   ```python
   @dataclass
   class ResearchState:
       env_input: dict
       map_features: dict = None
       literature_facts: list = None
       algorithm_records: list = None
       scored_algorithms: list = None
       decision: dict = None
       recommended_params: dict = None
       hypothesis: dict = None
       experiment_results: list = None
       reflection: dict = None
       report: str = None
       metadata: dict = None  # 时间戳、pipeline版本等
   ```
2. 提供 `to_dict()` 和 `from_dict()` 序列化方法
3. 提供 `summary()` 方法：返回关键字段的摘要字符串

**验证标准**：

- 运行 `python -c "from agents.research_state import ResearchState; rs=ResearchState(env_input={'test':True}); print(rs.summary())"` 输出非空摘要

***

### 提示词 4-2：创建地图分析智能体 MapAnalysisAgent

**操作目标**：新建 `agents/map_analysis_agent.py`，从 `environment_agent.py` 中拆分出地图结构分析功能。

**涉及文件**：

- `agents/map_analysis_agent.py`（新建）
- `agents/__init__.py`（修改）
- `map/map_analyzer.py`（可能需要微调）

**功能改进点**：

1. `MapAnalysisAgent` 类：
   - `analyze_grid(grid: np.ndarray)` 方法：计算障碍物聚类数、最大连通区域占比、瓶颈通道数量、障碍物分布熵
   - `extract_features(grid, start, target)` 方法：整合 `MapAnalyzer.analyze()` 结果并增加更多结构特征
   - 新增特征：`cluster_count`（障碍物聚类数）、`bottleneck_count`（宽度<3 的必经通道数）、`entropy`（障碍物空间分布熵）、`distance_to_target`（曼哈顿距离）
2. `MapAnalyzer.analyze()` 增加 `cluster_count`、`bottleneck_count`、`entropy` 字段计算
3. 在 `ResearchState` 流程中，`MapAnalysisAgent` 在 `EnvironmentAgent` 之后运行，输出存入 `map_features`

**验证标准**：

- 运行 `python -c "from agents.map_analysis_agent import MapAnalysisAgent; import numpy as np; ma=MapAnalysisAgent(); f=ma.extract_features(np.zeros((20,20),dtype=np.int8),(0,0),(19,19)); print('bottleneck_count' in f)"` 输出 True

***

### 提示词 4-3：升级 Orchestrator 为完整 12 智能体调度器

**操作目标**：修改 `agents/orchestrator_agent.py`，集成全部 12 个智能体并基于 `ResearchState` 流转数据。

**涉及文件**：

- `agents/orchestrator_agent.py`（修改）

**功能改进点**：

1. `OrchestratorAgent.__init__` 中初始化 12 个智能体：
   - DataAgent、MapAnalysisAgent、EnvironmentAgent、LiteratureAgent、FactExtractionAgent、KnowledgeAgent、RuleAgent、EvaluationAgent、ParameterAgent、DecisionAgent、HypothesisAgent、ReflectionAgent（后两个在 Phase 5 完善）、HumanLoopAgent、ExplanationAgent
2. `run(env_input)` 方法改为基于 `ResearchState` 的流水线：
   ```python
   state = ResearchState(env_input=env_input)
   state = self.data_agent.validate(state)
   state = self.map_agent.analyze(state)
   state = self.env_agent.classify(state)
   state = self.literature_agent.enrich(state)
   state = self.knowledge_agent.retrieve(state)
   state = self.rule_agent.filter_and_penalize(state)
   state = self.eval_agent.score(state)
   state = self.decision_agent.select_best(state)
   state = self.human_agent.check(state)
   state = self.explanation_agent.explain(state)
   state = self.hypothesis_agent.generate(state)
   state = self.reflection_agent.reflect(state)
   return state
   ```
3. 每个智能体的输入/输出统一为 `ResearchState`
4. 中间步骤失败时记录错误到 `state.metadata["errors"]` 并继续执行

**验证标准**：

- 所有现有智能体接口改为接收和返回 `ResearchState` 后，运行 `python main.py` 不报错
- 运行 `python -c "from agents.orchestrator_agent import OrchestratorAgent; o=OrchestratorAgent(); result=o.run({'obstacle_ratio':0.35,'map_width':100,'map_height':100,'connectivity':0.68,'topology_randomness':0.55,'compute_limit':'medium'}); print(type(result).__name__)"` 输出 `ResearchState`

***

### 提示词 4-4：升级 HumanLoopAgent 触发条件（7 种触发）

**操作目标**：修改 `agents/human_loop_agent.py`，扩展触发人工校验的条件从 1 种增加到 7 种。

**涉及文件**：

- `agents/human_loop_agent.py`（修改）

**功能改进点**：

1. `check` 方法改为接收 `ResearchState`，检查以下 7 种触发条件：
   - 条件1：前两名算法得分差 < SCORE\_GAP\_THRESHOLD（保留）
   - 条件2：知识库中缺少对应场景等级的历史数据
   - 条件3：推荐算法与 benchmark 实际跑出的最优算法不一致
   - 条件4：高复杂度场景下所有算法成功率 < 0.5
   - 条件5：用户选择了权重偏好（安全优先/耗时优先/成功率优先）
   - 条件6：文献事实数量 < 2 条
   - 条件7：引用中包含无法核验的文献
2. 每条触发条件在 `research_state.metadata["human_check_reasons"]` 中追加具体原因
3. `need_human_check` 为 True 时，`research_state.decision["need_human_check"] = True`

**验证标准**：

- 构造各种边界输入，验证 7 种条件均能正确触发
- 运行 `python -m pytest tests/test_decision_agent.py -v` 确认基本流程不受影响

***

### 提示词 4-5：创建反思智能体 ReflectionAgent

**操作目标**：新建 `agents/reflection_agent.py`，对决策结果进行质疑和可信度检查。

**涉及文件**：

- `agents/reflection_agent.py`（新建）
- `agents/__init__.py`（修改）
- `llm/prompt_templates.py`（修改，添加反思 Prompt）

**功能改进点**：

1. `ReflectionAgent` 类：
   - `__init__` 接收 `QwenClient` 实例
   - `reflect(state: ResearchState)` 方法：对决策进行全面审视
2. `prompt_templates.py` 新增 `REFLECTION_SYSTEM_PROMPT` 和 `REFLECTION_USER_TEMPLATE`
3. 反思检查清单（7 项）：
   - 推荐算法是否真的是实验最优？
   - 是否存在另一个算法成功率更高？
   - 是否只是耗时最短但成功率不足？
   - 文献依据是否真实？
   - 数据是否覆盖低、中、高复杂度？
   - 实验次数是否足够（≥3 次/算法）？
   - 结论是否过度泛化？
4. 输出格式：`{"confidence_score": 0~1, "issues": [...], "suggestions": [...], "passed": bool}`
5. 提供 `_rule_reflect(state)` 回退方法（无 LLM 时使用硬规则检查）

**验证标准**：

- 运行 `python -c "from agents.reflection_agent import ReflectionAgent; ra=ReflectionAgent(use_qwen=False); from agents.research_state import ResearchState; rs=ResearchState(env_input={'test':True}); rs.decision={'best_algorithm':'A*','scene_level':'高复杂度','ranking':[]}; result=ra.reflect(rs); print(result.metadata.get('reflection'))"` 输出反思结果

***

# Phase 5：假设生成—实验验证闭环（4 条提示词）

***

### 提示词 5-1：升级 HypothesisAgent 生成可验证科学假设

**操作目标**：修改 `agents/hypothesis_agent.py`，使其输出的假设具备可验证性并绑定实验方案。

**涉及文件**：

- `agents/hypothesis_agent.py`（修改）
- `llm/prompt_templates.py`（修改）

**功能改进点**：

1. `HYPOTHESIS_SYSTEM_PROMPT` 重写为更严格的结构化要求：
   - 必须输出 4 个部分：科学假设、验证实验设计、预期结果、假设边界条件
   - 科学假设采用"在 X 条件下，算法 Y 相比 Z 在指标 W 上有显著优势"的格式
2. `HypothesisAgent.generate` 方法：
   - 接收 `ResearchState` 而非分散参数
   - 调用 LLM 后解析 JSON 输出（如 LLM 返回非 JSON 则回退到规则生成）
   - 将 hypothesis 存入 `research_state.hypothesis`
3. `_default_hypothesis` 升级为包含 10 字段的模板：
   ```text
   待研究问题、科学假设、解决思路、必要技术手段、数据集、论文标题、摘要、方法论、实验设计、参考论文
   ```
4. hypothesis 对象结构：`{"hypothesis_text": str, "experiment_plan": dict, "expected_results": dict, "boundary_conditions": list}`

**验证标准**：

- 运行 `python -c "from agents.hypothesis_agent import HypothesisAgent; ha=HypothesisAgent(use_qwen=False); from agents.research_state import ResearchState; rs=ResearchState(env_input={'obstacle_ratio':0.65,'connectivity':0.3}); rs.decision={'best_algorithm':'混合优化算法','scene_level':'高复杂度','ranking':[],'best_score':0.85}; h=ha.generate(rs); print('hypothesis_text' in rs.hypothesis)"` 输出 True

***

### 提示词 5-2：创建实验验证智能体 ExperimentAgent

**操作目标**：新建 `agents/experiment_agent.py`，根据假设自动设计并运行验证实验。

**涉及文件**：

- `agents/experiment_agent.py`（新建）
- `agents/__init__.py`（修改）

**功能改进点**：

1. `ExperimentAgent` 类：
   - `__init__` 接收 `ExperimentDB` 和 `BenchmarkRunner` 实例
   - `run_validation(state: ResearchState)` 方法：
     a. 读取 `state.hypothesis["experiment_plan"]`
     b. 生成对应复杂度的 50 张随机地图
     c. 每张地图运行 5 种算法 × 5 次重复
     d. 将结果存入 `ExperimentDB`
     e. 统计各算法成功率、耗时、路径长度等
     f. 判断假设是否得到支持（threshold: 推荐算法成功率 > 次优算法 10%以上且统计显著）
   - `compare_with_hypothesis(state)` 方法：将实验结果与假设预期对比，计算支持度
2. 输出存入 `state.experiment_results`
3. 实验完成后自动调用 `state.metadata["hypothesis_supported"] = True/False`

**验证标准**：

- 运行实验验证流程，确认 `research_state.experiment_results` 包含 5 种算法的对比结果
- 确认 `research_state.metadata` 中有 `hypothesis_supported` 字段

***

### 提示词 5-3：构建假设-验证-反思闭环流水线

**操作目标**：新建 `agents/pipeline.py`，整合 HypothesisAgent → ExperimentAgent → ReflectionAgent 形成闭环。

**涉及文件**：

- `agents/pipeline.py`（新建）
- `agents/__init__.py`（修改）

**功能改进点**：

1. `ScientificDiscoveryPipeline` 类：
   - `run_full_cycle(env_input, max_iterations=3)` 方法：
     a. Orchestrator 运行 → 获取 ResearchState
     b. HypothesisAgent 生成假设
     c. ExperimentAgent 运行验证实验
     d. ReflectionAgent 反思结论
     e. 如果 `confidence_score < 0.7` 且 `iteration < max_iterations`，修正假设并重复 b-e
     f. 最终输出完整的 10 字段研究报告
   - `export_report(state, filepath)` 方法：将最终结果导出为 Markdown 文件到 `reports/generated_reports/`
2. 每次迭代记录到 `state.metadata["iterations"]` 列表

**验证标准**：

- 运行 `python -c "from agents.pipeline import ScientificDiscoveryPipeline; sp=ScientificDiscoveryPipeline(); result=sp.run_full_cycle({'obstacle_ratio':0.65,'map_width':100,'map_height':100,'connectivity':0.3,'topology_randomness':0.7,'compute_limit':'high'}, max_iterations=1); print(result.metadata.get('iterations',[]))"` 输出至少 1 次迭代

***

### 提示词 5-4：创建标准化研究报告生成器

**操作目标**：新建 `reports/report_generator.py`，严格按照 10 字段模板生成研究报告。

**涉及文件**：

- `reports/__init__.py`（新建）
- `reports/report_generator.py`（新建）

**功能改进点**：

1. `ReportGenerator` 类提供 `generate(state: ResearchState)` 方法，输出 10 字段 Markdown：
   ```markdown
   # 科学假设与研究计划
   ## 1. 待研究问题 Problem Statement
   ## 2. 解决思路 Rationale
   ## 3. 必要技术手段 Technical Details
   ## 4. 数据集 Datasets
   ## 5. 论文标题 Paper Title
   ## 6. 摘要 Paper Abstract
   ## 7. 方法论 Methods
   ## 8. 实验设计 Experiments
   ## 9. 实验结果 Results
   ## 10. 参考论文 References
   ```
2. 每个字段自动从 `ResearchState` 各字段中提取内容
3. `References` 部分只包含 `CitationAgent.validate_references()` 验证通过的文献
4. 报告末尾标注生成时间戳和系统版本
5. 提供 `save_to_file(filepath)` 方法自动保存到 `reports/generated_reports/`

**验证标准**：

- 运行报告生成器后，`reports/generated_reports/` 目录下存在 Markdown 文件
- 打开文件确认包含 10 个二级标题且顺序正确

***

# Phase 6：前端展示与人在回路升级（4 条提示词）

***

### 提示词 6-1：升级 Streamlit Tab 1（地图与数据输入）

**操作目标**：修改 `gui/streamlit_app.py` 的 Tab 1，增加文件上传、Benchmark 选择、优化偏好设置。

**涉及文件**：

- `gui/streamlit_app.py`（修改）

**功能改进点**：

1. **新增文件上传区域**：使用 `st.file_uploader` 支持上传 CSV/JSON/.map/.scen/.npy 文件
2. **新增 Benchmark 选择**：下拉菜单选择 Moving AI benchmark 地图集（调用 `BenchmarkLoader.list_available_maps()`）
3. **新增随机地图模板**：预设模板按钮："低障碍(15%)"、"中障碍(35%)"、"高障碍(65%)"、"迷宫型(50%)"
4. **新增优化偏好**：`st.radio` 选择"耗时优先 / 成功率优先 / 路径最短 / 平衡模式"，作为额外输入传给决策流水线
5. **新增算力约束**：保留原有 radio，增加说明 tooltip
6. 上传文件后自动调用 `MapParser` 解析并显示地图预览

**验证标准**：

- 启动 Streamlit 后在 Tab 1 看到文件上传组件、Benchmark 下拉菜单、模板按钮、优化偏好 radio
- 上传 CSV 地图文件后 Tab 1 中自动显示地图预览

***

### 提示词 6-2：升级 Streamlit Tab 2（环境分析与算法评分）

**操作目标**：修改 `gui/streamlit_app.py` 的 Tab 2，增加 10 指标展示和 benchmark 对比。

**涉及文件**：

- `gui/streamlit_app.py`（修改）
- `gui/visualization.py`（可能需要新增辅助函数）

**功能改进点**：

1. Tab 2 展示内容扩展到：
   - 地图预览（保留）
   - 障碍物占比、连通性、拓扑随机性、综合复杂度指数仪表盘（保留）
   - **新增**：障碍物聚类数、瓶颈通道数、分布熵
   - **新增**：10 维指标评分柱状图
   - **新增**：五算法雷达图（扩展为 10 维）
   - **新增**：实验对比结果表格（含 BenchmarkRunner 实际运行结果的 10 个指标列）
   - **新增**：实际运行结果与历史数据库对比的偏差提示
2. 评分颜色编码：绿色（≥0.8）、黄色（0.5\~0.8）、红色（<0.5）

**验证标准**：

- 启动 Streamlit 后在 Tab 2 看到扩展后的指标展示，柱状图包含 10 个维度的分解

***

### 提示词 6-3：升级 Streamlit Tab 3（多智能体推理链）

**操作目标**：修改 `gui/streamlit_app.py` 的 Tab 3，以可展开卡片展示每个智能体的推理过程。

**涉及文件**：

- `gui/streamlit_app.py`（修改）
- `gui/visualization.py`（修改 `render_reasoning_chain` 函数）

**功能改进点**：

1. 将 `render_reasoning_chain` 升级为展示 12 个智能体推理卡片，每个智能体用 `st.expander` 折叠：
   - **Data Agent**：输入校验结果、数据来源类型
   - **Map Analysis Agent**：地图结构特征详情
   - **Environment Agent**：场景分级依据、复杂度计算公式
   - **Literature Agent**：引用的文献事实、来源论文
   - **Knowledge Agent**：检索到的历史实验记录数、覆盖场景
   - **Rule Agent**：触发的规则、惩罚项详情
   - **Evaluation Agent**：10 维评分详细计算过程
   - **Parameter Agent**：推荐的超参数
   - **Decision Agent**：最终决策及置信度
   - **Hypothesis Agent**：生成的科学假设
   - **Reflection Agent**：反思结果、发现的问题
   - **Human-Loop Agent**：触发的人工校验项
2. 每个卡片用彩色边框标识状态：绿色=通过、黄色=警告、红色=异常
3. 可一键展开/折叠所有智能体卡片

**验证标准**：

- 启动 Streamlit 后在 Tab 3 看到至少 8 个可展开的智能体推理卡片（取决于流水线执行情况）

***

### 提示词 6-4：升级 Streamlit Tab 4（科学假设与研究报告）

**操作目标**：修改 `gui/streamlit_app.py` 的 Tab 4，完整渲染 10 字段研究报告并提供导出功能。

**涉及文件**：

- `gui/streamlit_app.py`（修改）

**功能改进点**：

1. Tab 4 渲染完整的 10 字段研究报告：
   - 使用 `st.markdown` 渲染 Markdown 格式报告
   - 每个字段用分隔线隔开
   - `实验结果` 字段内嵌 Plotly 柱状图和雷达图
   - `参考论文` 字段支持可点击链接（DOI/URL）
2. **新增导出按钮**：
   - "📥 导出 Markdown 报告"：下载 `.md` 文件
   - "📥 导出 JSON 数据"：下载完整 `ResearchState` 的 JSON
   - "📥 导出实验数据 CSV"：下载 SQLite 实验记录的 CSV
3. **新增人在回路面板**：
   - 如果 `need_human_check=True`，在 Tab 4 顶部显示红色 alert 提示
   - 提供"调整优化优先级"下拉菜单
   - 提供"质疑结论"输入框，允许用户输入反馈
   - 用户反馈后触发重分析按钮

**验证标准**：

- 启动 Streamlit 后在 Tab 4 看到完整的 10 字段报告
- 报告底部有 3 种导出按钮
- `need_human_check=True` 时显示红色 alert 和人在回路面板

***

# Phase 7：后端工程化与部署（4 条提示词）

***

### 提示词 7-1：添加日志系统

**操作目标**：创建 `utils/logging_config.py`，为整个系统添加分级日志记录。

**涉及文件**：

- `utils/__init__.py`（新建）
- `utils/logging_config.py`（新建）
- `config.py`（修改，添加日志配置项）

**功能改进点**：

1. `logging_config.py` 中 `setup_logging()` 函数：
   - 配置 root logger 输出到 `data/logs/system.log`（文件）和控制台
   - 日志格式：`%(asctime)s [%(levelname)s] %(name)s: %(message)s`
   - 日志级别从环境变量 `LOG_LEVEL` 读取，默认 INFO
   - 文件日志按日轮转（可选，使用 `RotatingFileHandler`）
2. `config.py` 添加：
   ```python
   LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
   LOG_FILE = "data/logs/system.log"
   ```
3. 在 `OrchestratorAgent.run()` 中添加关键节点的 info 日志
4. 在所有智能体的异常捕获处添加 error 日志

**验证标准**：

- 运行 `python -c "from utils.logging_config import setup_logging; setup_logging(); import logging; logging.info('test');"`
- 确认 `data/logs/system.log` 文件生成且包含 "test" 日志

***

### 提示词 7-2：创建 FastAPI 后端服务

**操作目标**：新建 `api/` 模块，提供 RESTful API 供外部调用。

**涉及文件**：

- `api/__init__.py`（新建）
- `api/server.py`（新建）
- `api/schemas.py`（新建，Pydantic 模型）
- `requirements.txt`（修改，添加 `fastapi` 和 `uvicorn`）

**功能改进点**：

1. `api/schemas.py` 定义 Pydantic 请求/响应模型：
   - `EnvInputRequest`：环境参数输入
   - `DecisionResponse`：决策结果
   - `HypothesisResponse`：科学假设
   - `ReportResponse`：完整研究报告
   - `ExperimentRequest` / `ExperimentResponse`：实验请求/响应
2. `api/server.py` 使用 FastAPI 创建以下端点：
   - `POST /analyze`：接收环境参数，返回完整 ResearchState JSON
   - `POST /experiment`：接收实验配置，异步运行实验并返回 run\_id
   - `GET /experiment/{run_id}`：查询实验状态和结果
   - `GET /report/{run_id}`：获取 Markdown 研究报告
   - `GET /health`：健康检查
3. 添加 CORS 中间件允许跨域
4. 添加请求速率限制（简单实现：用内存字典记录 IP 请求次数）

**验证标准**：

- 运行 `uvicorn api.server:app --host 0.0.0.0 --port 8000` 启动服务
- `curl http://localhost:8000/health` 返回 `{"status":"ok"}`
- `curl -X POST http://localhost:8000/analyze -H "Content-Type: application/json" -d '{"obstacle_ratio":0.35,"map_width":100,"map_height":100,"connectivity":0.68,"topology_randomness":0.55,"compute_limit":"medium"}'` 返回决策 JSON

***

### 提示词 7-3：完善配置管理与环境变量

**操作目标**：修改 `config.py`，将所有可变参数迁移到环境变量，完善 `.env.example`。

**涉及文件**：

- `config.py`（修改）
- `.env.example`（修改）

**功能改进点**：

1. 所有路径配置支持从环境变量覆盖：
   ```python
   KNOWLEDGE_BASE_DIR = os.getenv("KB_DIR", "knowledge_base")
   ```
2. 所有阈值支持从环境变量覆盖（附默认值）
3. 评分权重支持从 JSON 文件或环境变量 JSON 字符串加载
4. LLM 配置支持多 provider（`LLM_PROVIDER` 环境变量：`deepseek`/`qwen`/`openai`，默认 `deepseek`）
5. `.env.example` 添加所有可配置项及注释说明：
   ```
   DEEPSEEK_API_KEY=sk-your-key-here
   LLM_PROVIDER=deepseek
   LOG_LEVEL=INFO
   KB_DIR=knowledge_base
   EXPERIMENT_DB_PATH=data/experiments/experiments.sqlite
   # ... 更多配置项
   ```

**验证标准**：

- 设置环境变量 `KB_DIR=test_kb` 后运行 Python，确认 `config.KNOWLEDGE_BASE_DIR` 值为 `test_kb`
- `.env.example` 文件包含至少 15 个配置项

***

### 提示词 7-4：创建 Docker 部署配置

**操作目标**：创建 `Dockerfile` 和 `docker-compose.yml`，支持一键部署。

**涉及文件**：

- `Dockerfile`（新建）
- `docker-compose.yml`（新建）
- `.dockerignore`（新建）

**功能改进点**：

1. `Dockerfile`：
   - 基于 `python:3.11-slim`
   - 安装 `requirements.txt` 依赖
   - 复制项目代码
   - 暴露 8000 端口（FastAPI）和 8501 端口（Streamlit）
   - 启动命令：`uvicorn api.server:app --host 0.0.0.0 --port 8000`
2. `docker-compose.yml`：
   - `api` 服务：FastAPI 后端
   - `streamlit` 服务：GUI 前端
   - `data` 卷挂载：持久化实验数据、日志、报告
   - 环境变量从 `.env` 文件读取
3. `.dockerignore`：
   - 忽略 `__pycache__/`、`.venv/`、`.pytest_cache/`、`*.pyc`、`.git/`

**验证标准**：

- 运行 `docker build -t ai-scientist-path-planning .` 构建成功
- 运行 `docker-compose up` 后访问 `http://localhost:8000/health` 和 `http://localhost:8501` 均可正常访问

***

## 附录：使用说明

### 文件结构影响总览

执行全部 35 条提示词后，项目文件结构将变为：

```
ai_scientist_path_planning/
├── agents/
│   ├── __init__.py
│   ├── research_state.py        # [新增] 全局状态对象
│   ├── data_agent.py            # [修改] 增加文件输入校验
│   ├── environment_agent.py
│   ├── map_analysis_agent.py    # [新增] 地图结构分析
│   ├── knowledge_agent.py       # [修改] 支持 SQLite + 文献
│   ├── literature_agent.py      # [新增] 文献检索
│   ├── fact_extraction_agent.py # [新增] 事实抽取
│   ├── citation_agent.py        # [新增] 引用核验
│   ├── rag_agent.py             # [新增] RAG 检索
│   ├── rule_agent.py
│   ├── evaluation_agent.py      # [修改] 10 维评分
│   ├── parameter_agent.py
│   ├── decision_agent.py
│   ├── orchestrator_agent.py    # [修改] 12 智能体调度
│   ├── human_loop_agent.py      # [修改] 7 种触发条件
│   ├── reflection_agent.py      # [新增] 反思智能体
│   ├── hypothesis_agent.py      # [修改] 可验证假设
│   ├── experiment_agent.py      # [新增] 实验验证
│   ├── pipeline.py              # [新增] 闭环流水线
│   └── explanation_agent.py
├── algorithms/
├── api/
│   ├── __init__.py              # [新增]
│   ├── server.py                # [新增] FastAPI 服务
│   └── schemas.py               # [新增] Pydantic 模型
├── data/
│   ├── __init__.py              # [修改]
│   ├── data_manager.py          # [新增] 目录管理
│   ├── data_card.py             # [新增] 数据卡生成
│   ├── benchmark_loader.py      # [新增] Benchmark 下载
│   ├── experiment_db.py         # [新增] SQLite 数据库
│   ├── raw/
│   ├── processed/
│   └── experiments/
├── evaluation/
│   ├── metrics.py               # [修改] 10 指标扩展
│   ├── scoring.py               # [修改] 10 维评分
│   ├── benchmark.py
│   └── experiment_runner.py     # [新增] 批量实验
├── gui/
│   ├── streamlit_app.py         # [修改] 4 Tab 升级
│   └── visualization.py        # [修改] 新图表函数
├── knowledge_base/
├── literature/
│   ├── __init__.py              # [新增]
│   ├── models.py                # [新增]
│   └── literature_kb.json       # [新增]
├── llm/
├── map/
│   ├── map_parser.py            # [新增] 多格式解析
│   └── map_analyzer.py          # [修改] 扩展特征
├── reports/
│   ├── __init__.py              # [新增]
│   └── report_generator.py      # [新增] 报告生成
├── utils/
│   ├── __init__.py              # [新增]
│   └── logging_config.py        # [新增] 日志配置
├── config.py                    # [修改] 环境变量 + 10 维权重
├── main.py
├── Dockerfile                   # [新增]
├── docker-compose.yml           # [新增]
├── .dockerignore                # [新增]
├── .env.example                 # [修改] 扩展配置项
├── TECHNICAL_BOUNDARY.md        # [新增] 技术边界文档
└── requirements.txt             # [修改] 添加 fastapi/uvicorn
```

### 执行建议

1. **按顺序执行**：每个 Phase 内的提示词有依赖关系，必须从前往后执行
2. **逐条验证**：每条提示词末尾的「验证标准」必须在执行下一条前通过
3. **遇到错误回退**：如果某条执行后测试失败，先让 AI 智能体修复当前问题再继续
4. **Phase 间可以暂停**：每个 Phase 结束后是一个稳定的里程碑，可以提交代码
5. **LLM 相关提示词**：涉及 DeepSeek/Qwen API 调用的提示词，在无 API Key 时使用 `use_qwen=False` 的回退逻辑验证
6. **耗时评估**：Phase 0\~1 约 1\~2 小时（主要是文件结构调整和数据导入），Phase 2\~3 约 2\~4 小时（数据库和文献系统），Phase 4\~5 约 3\~5 小时（核心智能体协同逻辑），Phase 6\~7 约 2\~3 小时（前端和后端工程化）。总计约 8\~14 小时，建议分 3\~4 天完成。
7. **版本控制**：每完成一个 Phase 建议执行一次 `git commit`，便于回退和追踪进度。

