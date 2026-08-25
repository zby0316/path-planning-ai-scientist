# Phase 1：数据输入升级 Spec

## Why

当前系统虽然已经在 `config.py` 中预留 `DATA_DIR = "data"` 与 `MAPS_DIR = f"{DATA_DIR}/maps"`，但 `data/` 下实际只有 `experiments/` 一个子目录，缺少标准化的多来源数据存储布局；地图文件目前仅能由 `map/map_generator.py` 程序化生成，无法直接消费已有的 Moving AI `.map` / `.scen` 公开基准、用户上传的 CSV/JSON 栅格或 NumPy 数组；`agents/data_agent.py` 的 `validate` 方法也只接受"全部参数手工传入"一种方式，无法从地图文件反向推导 `obstacle_ratio` / `map_height` / `map_width` / `start_point` / `target_point` 等环境参数。这导致系统在实际使用中必须依赖手工配置，无法与外部数据源对接，难以支撑后续阶段的算法适配实验和复现。

## What Changes

- 在 `data/` 下补齐完整的子目录结构，并新建 `data/data_manager.py` 提供 `DataManager` 类统一管理路径、自动建目录、文件枚举与 `ensure_dir` 静态方法（提示词 1-1）。
- 新建 `map/map_parser.py` 的 `MapParser` 类，支持 `.map`（Moving AI）、`.scen`（Moving AI 场景）、CSV 栅格、JSON 栅格、`.npy` 五种格式的统一解析入口，统一返回 `{grid, metadata, tasks}` 字典结构（提示词 1-2）。
- 新建 `data/benchmark_loader.py` 的 `BenchmarkLoader` 类，基于 `urllib.request` 从 Moving AI 公开站点按需下载 `.map` / `.map.scen`，并提供 `list_available_maps()` 推荐的 9 个 dao 系列地图集与 `download_log.json` 记录（提示词 1-3）。
- 新建 `data/data_card.py` 的 `DataCardGenerator` 类，为每个数据集自动生成 10 字段的 `data_card.md`，并提供 `generate_from_movingai(map_name)` 快捷方法（提示词 1-4）。
- 修改 `agents/data_agent.py` 的 `validate` 方法，新增可选参数 `map_filepath`，自动从地图文件反向推导 `obstacle_ratio` / `map_height` / `map_width` / `start_point` / `target_point`，并在 `env` 中写入 `data_source` 字段记录数据来源（提示词 1-5）。
- 更新 `data/__init__.py` 与 `map/__init__.py`，使上述新增类可被外部 `from data.xxx import ...` / `from map.xxx import ...` 直接导入（提示词 1-1、1-2）。

## Impact

- Affected specs：`phase-0-compliance-and-baseline`（仅受间接影响——`data_agent.validate` 的返回结构新增字段，但已声明的字段未被破坏）。
- Affected code：
  - `data/data_manager.py`（新建）
  - `data/benchmark_loader.py`（新建）
  - `data/data_card.py`（新建）
  - `data/__init__.py`（修改：导出 `DataManager` / `BenchmarkLoader` / `DataCardGenerator`）
  - `map/map_parser.py`（新建）
  - `map/__init__.py`（修改：导出 `MapParser`）
  - `agents/data_agent.py`（修改：`validate` 新增 `map_filepath` 参数、自动推导环境参数、写入 `data_source`）
  - `requirements.txt`（视情况增加/确认标准库依赖；本阶段不强制新增第三方包）
  - `data/raw/` 与 `data/processed/` 与 `data/literature/` 与 `data/experiments/` 下的子目录（由 `DataManager` 在导入时自动创建）

## ADDED Requirements

### Requirement: DataManager 数据目录自动管理

`data/data_manager.py` SHALL 提供 `DataManager` 类，要求：

1. 构造时 SHALL 自动创建以下子目录（使用 `pathlib.Path.mkdir(parents=True, exist_ok=True)`）：
   - `data/raw/movingai_2d/`
   - `data/raw/movingai_3d/`
   - `data/raw/osm/`
   - `data/raw/uploaded/`
   - `data/processed/grid_maps/`
   - `data/processed/topology_graphs/`
   - `data/processed/dynamic_maps/`
   - `data/experiments/`
   - `data/literature/raw_pdf/`
   - `data/literature/metadata/`
   - `data/literature/extracted_facts/`
   - `data/literature/references/`
2. SHALL 提供 `get_path(category: str) -> Path` 方法，至少支持 `movingai_2d` / `movingai_3d` / `osm` / `uploaded` / `grid_maps` / `topology_graphs` / `dynamic_maps` / `experiments` / `raw_pdf` / `metadata` / `extracted_facts` / `references` 12 个键的精确映射；未知键 SHALL 抛出 `ValueError(f"未知的数据类别: {category}")`。
3. SHALL 提供 `list_files(category: str, pattern: str = "*") -> list[Path]` 方法，按 `glob` 模式返回某类别目录下的文件路径列表（仅文件、不含子目录）。
4. SHALL 提供静态方法 `ensure_dir(path)` 供其他模块复用。

#### Scenario: 自动建目录与路径查询
- **WHEN** 在仓库根目录执行 `python -c "from data.data_manager import DataManager; dm = DataManager(); print(dm.get_path('movingai_2d'))"`
- **THEN** SHALL 无报错输出，且 `data/raw/movingai_2d/` 目录 SHALL 已被创建

#### Scenario: 未知类别抛出 ValueError
- **WHEN** 调用 `DataManager().get_path("not_existing_category")`
- **THEN** SHALL 抛出 `ValueError`，且异常信息 SHALL 包含 `未知的数据类别`

### Requirement: MapParser 多格式地图解析

`map/map_parser.py` SHALL 提供 `MapParser` 类，要求：

1. SHALL 提供 `parse(filepath: str) -> dict` 入口方法，根据文件扩展名（小写）自动分发到 5 个子解析器；不支持的扩展名 SHALL 抛出 `ValueError(f"不支持的地图格式: {ext}")`。
2. `.map`（Moving AI）解析 SHALL：读取 `height` / `width` / `map` 三行后，将 `.` 映射为可通行 `0`、将 `@` / `O` / `T` / `W` 映射为障碍 `1`，返回 `shape == (height, width)` 的 `np.ndarray`；同时写入 `metadata = {"format": "movingai_map", "height": h, "width": w}`。
3. `.scen`（Moving AI 场景）解析 SHALL：跳过 `Bucket` 开头的版本行，按空白拆分每一任务行，返回 `tasks` 列表，每项为 `{"start_x", "start_y", "target_x", "target_y", "optimal_length"}` 字典（坐标使用 1-based 原始值）。
4. CSV 解析 SHALL：将文件读为 `,` 分隔的 0/1 矩阵，返回 `np.ndarray`；`metadata = {"format": "csv"}`。
5. JSON 解析 SHALL：从 JSON 二维数组还原为 `np.ndarray`；`metadata = {"format": "json"}`。
6. `.npy` 解析 SHALL：使用 `np.load()` 加载；`metadata = {"format": "npy"}`。
7. 所有解析器 SHALL 返回统一结构 `{"grid": np.ndarray, "metadata": dict, "tasks": list}`（`.scen` 解析时 `grid` 可为 `None`，但 `tasks` 非空）。
8. 当 `filepath` 是 `.map` 且同级存在同名 `.map.scen` 文件时，`.map` 解析器 SHALL 顺带加载该 `.scen` 并将 `tasks` 写入返回字典。

#### Scenario: CSV 解析返回正确栅格
- **WHEN** 准备内容为 `0,0,0\n0,1,0\n0,0,0` 的 `data/raw/uploaded/test.csv`，并执行 `MapParser().parse("data/raw/uploaded/test.csv")`
- **THEN** 返回字典的 `grid` SHALL 为 `shape == (3, 3)` 且 `grid[1, 1] == 1` 的 `np.ndarray`

#### Scenario: 不支持的扩展名抛出 ValueError
- **WHEN** 调用 `MapParser().parse("test.xyz")`
- **THEN** SHALL 抛出 `ValueError("不支持的地图格式: .xyz")`

#### Scenario: .map 解析符号映射
- **WHEN** 构造一个含 `..@` / `OO.` / `TT.` / `WW.` 的最小 `.map` 解析
- **THEN** 对应坐标 SHALL 全部为 `1`

### Requirement: BenchmarkLoader Moving AI 基准下载

`data/benchmark_loader.py` SHALL 提供 `BenchmarkLoader` 类，要求：

1. 构造时接收 `DataManager` 实例，使用其 `get_path("movingai_2d")` 作为下载目标目录。
2. SHALL 提供 `download_movingai_2d(map_name: str) -> dict` 方法：从 `https://www.movingai.com/benchmarks/grids/{map_name}.map` 与 `https://www.movingai.com/benchmarks/grids/{map_name}.map.scen` 下载文件；下载前 SHALL 检查目标文件是否已存在，存在则跳过并标记 `skipped=True`。
3. SHALL 使用 Python 标准库 `urllib.request` 完成下载（不引入 `wget` 第三方依赖）。
4. SHALL 提供 `load_map(map_name: str) -> dict` 方法：调 `MapParser().parse(...)` 解析已下载的 `.map`（同目录的 `.scen` 任务列表由 `MapParser` 自动合并）。
5. SHALL 提供 `list_available_maps() -> list[str]` 方法，至少返回以下 9 个地图集：`["dao/arena", "dao/arena2", "dao/brc000d", "dao/brc300d", "dao/brc600d", "dao/den000d", "dao/den300d", "dao/den600d", "dao/den900d"]`。
6. 每次成功下载 SHALL 追加一条记录到 `data/raw/movingai_2d/download_log.json`，记录字段至少包含：`timestamp`（ISO-8601）、`filename`、`url`、`size_bytes`、`skipped`。

#### Scenario: list_available_maps 返回至少 3 个地图集
- **WHEN** 执行 `python -c "from data.benchmark_loader import BenchmarkLoader; bl = BenchmarkLoader(); print(bl.list_available_maps()[:3])"`
- **THEN** SHALL 输出一个包含 3 个 `dao/...` 字符串的列表

#### Scenario: 重复下载跳过
- **WHEN** 对同一 `map_name` 连续两次调用 `download_movingai_2d`
- **THEN** 第二次调用 SHALL 不发起网络请求，download_log SHALL 标记 `skipped=True`

### Requirement: DataCardGenerator 数据卡自动生成

`data/data_card.py` SHALL 提供 `DataCardGenerator` 类，要求：

1. SHALL 提供 `generate(dataset_name, source, download_url, license_info, map_type, map_count, task_count, purpose, preprocessing, reproducible, output_dir=None)` 方法，将生成结果写入 `output_dir / "data_card.md"`（`output_dir` 默认使用 `DataManager().get_path("movingai_2d")`）。
2. 生成的 `data_card.md` SHALL 严格按以下 10 行结构输出（顺序与字段名固定）：
   ```
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
3. SHALL 提供 `generate_from_movingai(map_name: str, map_count: int = 1, task_count: int = 0) -> Path` 快捷方法，自动填充：`source = "https://www.movingai.com/benchmarks/grids.html"`、`license_info = "学术使用"`、`map_type = "2D 栅格地图"`，并写入 `data/raw/movingai_2d/data_card.md`。

#### Scenario: 手动调用 generate 写出文件
- **WHEN** 调用 `DataCardGenerator().generate(dataset_name="demo", source="x", download_url="x", license_info="x", map_type="2D", map_count=1, task_count=0, purpose="x", preprocessing="x", reproducible=True)`
- **THEN** SHALL 在 `data/raw/movingai_2d/data_card.md` 写出文件，且内容 SHALL 包含上述 10 行

#### Scenario: generate_from_movingai 自动填充来源
- **WHEN** 调用 `DataCardGenerator().generate_from_movingai("dao/arena")`
- **THEN** 生成的 `data_card.md` 中 `来源` 字段 SHALL 为 `https://www.movingai.com/benchmarks/grids.html`，`许可协议` 字段 SHALL 为 `学术使用`

### Requirement: Data Agent 支持文件输入

`agents/data_agent.py` 的 `DataReceiverAgent.validate` 方法 SHALL 扩展，要求：

1. 新增可选参数 `map_filepath: str = None`。
2. 当 `map_filepath` 存在时 SHALL 调用 `MapParser().parse(map_filepath)` 获取 `grid` 与 `metadata`；若解析失败 SHALL 抛出统一 `ValueError`，异常信息 SHALL 包含 `map_filepath`。
3. 若 `env` 中未提供 `obstacle_ratio` 且 `grid` 非 `None`，SHALL 自动计算 `obstacle_ratio = float(np.count_nonzero(grid == 1)) / grid.size`。
4. 若 `env` 中未提供 `map_height` / `map_width` 且 `grid` 非 `None`，SHALL 自动以 `int(grid.shape[0])` / `int(grid.shape[1])` 填充。
5. 若解析结果 `tasks` 非空且 `env` 中未提供 `start_point` / `target_point`，SHALL 取 `tasks[0]`，并将 `start_point = [int(tasks[0]["start_x"] - 1), int(tasks[0]["start_y"] - 1)]`、`target_point = [int(tasks[0]["target_x"] - 1), int(tasks[0]["target_y"] - 1)]` 填入 `env`（Moving AI 场景坐标为 1-based，需转为 0-based）。
6. `env` 字典 SHALL 始终新增 `data_source` 字段，取值规则：
   - `map_filepath` 提供且 `tasks` 非空 → `"benchmark"`
   - `map_filepath` 提供但无 `tasks` → `"map_file"`
   - 未提供 `map_filepath` → `"manual_params"`
7. 既有 Phase 0 的 `OPTIONAL_FIELDS` / 范围校验 / `input_validated` / `validation_timestamp` 行为 SHALL 保持不变。

#### Scenario: 文件输入自动推导 obstacle_ratio
- **WHEN** 准备一个 50×50 的 CSV（20% 障碍物），调用 `DataReceiverAgent().validate({"compute_limit": "medium"}, map_filepath="test.csv")`
- **THEN** 返回字典 SHALL 包含 `obstacle_ratio ≈ 0.20`（±0.01）、`map_height == 50`、`map_width == 50`、`data_source == "map_file"`

#### Scenario: 带 .scen 时 data_source 标记为 benchmark
- **WHEN** 解析后 `tasks` 非空
- **THEN** `data_source` SHALL 为 `"benchmark"`，且 `start_point` / `target_point` SHALL 已自动填入

#### Scenario: 无文件输入时 data_source 为 manual_params
- **WHEN** 仅提供手工参数且不传 `map_filepath`
- **THEN** `data_source` SHALL 为 `"manual_params"`

## MODIFIED Requirements

### Requirement: Data Agent 可选字段类型校验（来自 Phase 0）

`agents/data_agent.py` SHALL 保留 Phase 0 既有 `OPTIONAL_FIELDS = ["start_point", "target_point", "dynamic_change_rate"]`、`[int, int]` 校验、`[0,1]` 校验、`input_validated: True`、`validation_timestamp`、`ValueError` 统一包装等行为不变。**新增** `map_filepath` 参数为可选扩展，**新增** `data_source` 字段。

## REMOVED Requirements

无。
