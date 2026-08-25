# Tasks

> 范围：Phase 1 数据输入升级，对应提示词 1-1 ~ 1-5。
> 实现阶段需先阅读 `.trae/specs/phase-1-data-input-upgrade/spec.md`。

- [x] Task 1（提示词 1-1）：新建 `data/data_manager.py` 实现 `DataManager`
  - [x] SubTask 1.1：在 `data/__init__.py` 中预留 `from data.data_manager import DataManager` 导出（暂可注释，待类实现后启用）
  - [ ] SubTask 1.2：实现 `DataManager.__init__` 自动创建 12 个子目录（`raw/movingai_2d` / `raw/movingai_3d` / `raw/osm` / `raw/uploaded` / `processed/grid_maps` / `processed/topology_graphs` / `processed/dynamic_maps` / `experiments` / `literature/raw_pdf` / `literature/metadata` / `literature/extracted_facts` / `literature/references`），使用 `pathlib.Path.mkdir(parents=True, exist_ok=True)`
  - [ ] SubTask 1.3：实现 `get_path(category)` 方法，覆盖 12 个类别，未知键抛 `ValueError(f"未知的数据类别: {category}")`
  - [ ] SubTask 1.4：实现 `list_files(category, pattern="*")` 方法，使用 `glob` 仅返回文件
  - [x] SubTask 1.5：实现静态方法 `ensure_dir(path)` 供其他模块复用
  - [ ] SubTask 1.6：执行 `python -c "from data.data_manager import DataManager; dm=DataManager(); print(dm.get_path('movingai_2d'))"` 验证路径正确输出
  - [x] SubTask 1.7：执行 `os.path.isdir('data/raw/movingai_2d')` 验证目录已创建

- [x] Task 2（提示词 1-2）：新建 `map/map_parser.py` 实现 `MapParser`
  - [x] SubTask 2.1：实现 `MapParser.parse(filepath)` 总入口，按扩展名分发
  - [x] SubTask 2.2：实现 `.map` 解析：`height` / `width` / `map` 三行格式，`.`→0、`@`/`O`/`T`/`W`→1
  - [x] SubTask 2.3：实现 `.scen` 解析：跳过 `Bucket` 行，返回任务列表
  - [x] SubTask 2.4：实现 CSV 解析：`,` 分隔的 0/1 矩阵
  - [x] SubTask 2.5：实现 JSON 解析：二维数组
  - [x] SubTask 2.6：实现 `.npy` 解析：`np.load()`
  - [x] SubTask 2.7：所有解析器返回 `{"grid", "metadata", "tasks"}` 统一结构
  - [x] SubTask 2.8：`.map` 解析时若同级存在 `.map.scen` 自动合并 tasks
  - [x] SubTask 2.9：扩展名不支持时抛 `ValueError(f"不支持的地图格式: {ext}")`
  - [x] SubTask 2.10：在 `map/__init__.py` 中导出 `MapParser`
  - [x] SubTask 2.11：准备 `data/raw/uploaded/test.csv` 内容 `0,0,0\n0,1,0\n0,0,0`，验证 `parse` 返回 `shape==(3,3)` 且 `[1,1]==1`
  - [x] SubTask 2.12：调用 `parse("test.xyz")` 验证抛 `ValueError("不支持的地图格式: .xyz")`

- [x] Task 3（提示词 1-3）：新建 `data/benchmark_loader.py` 实现 `BenchmarkLoader`
  - [x] SubTask 3.1：实现 `BenchmarkLoader.__init__(data_manager)` 并使用 `dm.get_path("movingai_2d")` 作为下载目标
  - [x] SubTask 3.2：实现 `download_movingai_2d(map_name)` 方法，基础 URL `https://www.movingai.com/benchmarks/grids/`，下载 `.map` 与 `.map.scen`，使用 `urllib.request`
  - [x] SubTask 3.3：实现文件存在检查，命中时跳过并标记 `skipped=True`
  - [x] SubTask 3.4：实现 `load_map(map_name)` 方法，调用 `MapParser().parse` 解析
  - [x] SubTask 3.5：实现 `list_available_maps()` 返回 9 个 dao 系列地图集
  - [x] SubTask 3.6：每次下载追加一条 `download_log.json` 记录（timestamp / filename / url / size_bytes / skipped）
  - [x] SubTask 3.7：在 `data/__init__.py` 中导出 `BenchmarkLoader`
  - [x] SubTask 3.8：执行 `python -c "from data.benchmark_loader import BenchmarkLoader; bl=BenchmarkLoader(); print(bl.list_available_maps()[:3])"` 验证输出至少 3 个
  - [x] SubTask 3.9：手动调用 `download_movingai_2d("dao/arena")` 验证文件落到 `data/raw/movingai_2d/`

- [x] Task 4（提示词 1-4）：新建 `data/data_card.py` 实现 `DataCardGenerator`
  - [x] SubTask 4.1：实现 `generate(...)` 方法按 10 行结构写出 `data_card.md`
  - [x] SubTask 4.2：实现 `generate_from_movingai(map_name)` 快捷方法，自动填 `source` / `license_info` / `map_type`
  - [x] SubTask 4.3：在 `data/__init__.py` 中导出 `DataCardGenerator`
  - [x] SubTask 4.4：调用 `generate_from_movingai("dao/arena")` 后，检查 `data/raw/movingai_2d/data_card.md` 存在且包含 10 个字段

- [x] Task 5（提示词 1-5）：扩展 `agents/data_agent.py` 的 `validate` 方法
  - [x] SubTask 5.1：新增可选参数 `map_filepath: str = None`
  - [x] SubTask 5.2：若 `map_filepath` 存在则调 `MapParser().parse(map_filepath)`，解析失败包装为 `ValueError`，异常信息包含 `map_filepath`
  - [x] SubTask 5.3：未提供 `obstacle_ratio` 时，从 `grid` 自动计算 `np.count_nonzero(grid==1) / grid.size`
  - [x] SubTask 5.4：未提供 `map_height` / `map_width` 时，从 `grid.shape` 自动填充
  - [x] SubTask 5.5：解析结果 `tasks` 非空时，从 `tasks[0]` 自动填 `start_point` / `target_point`（1-based 转 0-based）
  - [x] SubTask 5.6：在 `env` 上新增 `data_source` 字段（`manual_params` / `map_file` / `benchmark`）
  - [x] SubTask 5.7：保留 Phase 0 既有 `OPTIONAL_FIELDS` / `input_validated` / `validation_timestamp` 行为
  - [x] SubTask 5.8：准备 50×50 CSV（20% 障碍物），调 `validate({"compute_limit":"medium"}, map_filepath="test.csv")`，验证 `obstacle_ratio ≈ 0.20`、`map_height == 50`、`map_width == 50`、`data_source == "map_file"`
  - [x] SubTask 5.9：解析到 `tasks` 时，验证 `data_source == "benchmark"` 且 `start_point` / `target_point` 已自动填入
  - [x] SubTask 5.10：不传 `map_filepath` 时，验证 `data_source == "manual_params"`

- [x] Task 6（提示词 1-1 ~ 1-4）：更新 `data/__init__.py` 与 `map/__init__.py` 导出
  - [x] SubTask 6.1：`data/__init__.py` 导出 `DataManager` / `BenchmarkLoader` / `DataCardGenerator`
  - [x] SubTask 6.2：`map/__init__.py` 导出 `MapParser`
  - [x] SubTask 6.3：执行 `python -c "from data import DataManager, BenchmarkLoader, DataCardGenerator; from map import MapParser; print('imports OK')"` 验证全部可导入

# Task Dependencies

- Task 1（DataManager）独立，可最先开始
- Task 2（MapParser）独立，可与 Task 1 并行
- Task 3（BenchmarkLoader）依赖 Task 1（需 `DataManager` 注入）与 Task 2（需 `MapParser.load_map`）
- Task 4（DataCardGenerator）依赖 Task 1（默认输出目录）
- Task 5（DataAgent 扩展）依赖 Task 2（需 `MapParser`）与 Task 1（间接）
- Task 6（导出）依赖 Task 1 ~ Task 5 全部完成
- 整体收口（验证命令）依赖 Task 1 ~ Task 6 全部完成
