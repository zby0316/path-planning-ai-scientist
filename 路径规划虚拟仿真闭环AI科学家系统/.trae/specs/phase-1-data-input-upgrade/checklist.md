# Checklist（Phase 1 数据输入升级）

> 验证方法：每个条目在实现完成后由 Sub-Agent 或主流程实际执行/审阅，并通过在条目开头勾选 `[x]` 标记通过。

## DataManager 数据目录（提示词 1-1）

- [x] `data/data_manager.py` 存在并实现 `DataManager` 类
- [x] `DataManager.__init__` 自动创建 12 个子目录（`raw/movingai_2d` / `raw/movingai_3d` / `raw/osm` / `raw/uploaded` / `processed/grid_maps` / `processed/topology_graphs` / `processed/dynamic_maps` / `experiments` / `literature/raw_pdf` / `literature/metadata` / `literature/extracted_facts` / `literature/references`）
- [x] `get_path` 方法覆盖全部 12 个键，未知键抛 `ValueError` 且异常信息包含 `未知的数据类别`
- [x] `list_files` 方法按 `glob` 模式仅返回文件、不含子目录
- [x] `ensure_dir` 静态方法可被其他模块直接调用
- [x] `python -c "from data.data_manager import DataManager; dm=DataManager(); print(dm.get_path('movingai_2d'))"` 输出正确路径
- [x] `data/raw/movingai_2d/` 等 12 个子目录在导入后均已存在

## MapParser 多格式解析（提示词 1-2）

- [x] `map/map_parser.py` 存在并实现 `MapParser` 类
- [x] `.map` 解析：`height` / `width` / `map` 三行格式，`.`→0，`@`/`O`/`T`/`W`→1，返回 `shape==(height, width)` 的 `np.ndarray`
- [x] `.scen` 解析：跳过 `Bucket` 行，返回 `start_x` / `start_y` / `target_x` / `target_y` / `optimal_length` 字典列表
- [x] CSV 解析：`,` 分隔 0/1 矩阵
- [x] JSON 解析：二维数组 JSON
- [x] `.npy` 解析：`np.load()` 直接加载
- [x] 所有解析器返回 `{"grid", "metadata", "tasks"}` 统一结构
- [x] `.map` 解析时若同级存在 `.map.scen` 自动合并 tasks
- [x] 扩展名不支持时抛 `ValueError(f"不支持的地图格式: {ext}")`
- [x] 准备 `data/raw/uploaded/test.csv` 内容 `0,0,0\n0,1,0\n0,0,0`，运行 `MapParser().parse(...)` 返回 `grid.shape==(3,3)` 且 `grid[1,1]==1`
- [x] `MapParser().parse("test.xyz")` 抛 `ValueError("不支持的地图格式: .xyz")`

## BenchmarkLoader Moving AI 下载（提示词 1-3）

- [x] `data/benchmark_loader.py` 存在并实现 `BenchmarkLoader` 类
- [x] `BenchmarkLoader.__init__(data_manager)` 接收 `DataManager` 并使用 `movingai_2d` 路径作为目标
- [x] `download_movingai_2d(map_name)` 使用 `urllib.request` 从 `https://www.movingai.com/benchmarks/grids/` 下载 `.map` 与 `.map.scen`
- [x] 文件已存在时跳过下载，标记 `skipped=True`
- [x] `load_map(map_name)` 调 `MapParser().parse` 解析已下载地图
- [x] `list_available_maps()` 返回 9 个 dao 系列地图集（`arena` / `arena2` / `brc000d` / `brc300d` / `brc600d` / `den000d` / `den300d` / `den600d` / `den900d`）
- [x] 每次下载追加一条 `download_log.json` 记录，包含 `timestamp` / `filename` / `url` / `size_bytes` / `skipped`
- [x] `python -c "from data.benchmark_loader import BenchmarkLoader; bl=BenchmarkLoader(); print(bl.list_available_maps()[:3])"` 输出至少 3 个地图集名称
- [x] 手动调用 `download_movingai_2d("dao/arena")` 后，`data/raw/movingai_2d/` 目录包含 `arena.map`

## DataCardGenerator 数据卡（提示词 1-4）

- [x] `data/data_card.py` 存在并实现 `DataCardGenerator` 类
- [x] `generate(...)` 方法按 10 行结构写出 `data_card.md`（顺序与字段名与 spec 完全一致）
- [x] `generate_from_movingai(map_name)` 自动填 `source = https://www.movingai.com/benchmarks/grids.html`、`license_info = 学术使用`、`map_type = 2D 栅格地图`
- [x] `data/raw/movingai_2d/data_card.md` 存在且内容包含 10 个字段

## Data Agent 文件输入（提示词 1-5）

- [x] `agents/data_agent.py` 的 `validate` 方法新增 `map_filepath: str = None` 可选参数
- [x] 当 `map_filepath` 存在时调用 `MapParser().parse(map_filepath)`，解析失败包装为 `ValueError`，异常信息包含 `map_filepath`
- [x] 未提供 `obstacle_ratio` 时，从 `grid` 自动计算 `np.count_nonzero(grid==1) / grid.size`
- [x] 未提供 `map_height` / `map_width` 时，从 `grid.shape` 自动填充
- [x] `tasks` 非空时，从 `tasks[0]` 自动填 `start_point` / `target_point`（1-based 转 0-based）
- [x] `env` 字典新增 `data_source` 字段，取值 `manual_params` / `map_file` / `benchmark`
- [x] Phase 0 既有 `OPTIONAL_FIELDS` / `input_validated` / `validation_timestamp` 行为保持不变
- [x] 50×50 CSV（20% 障碍物）调用 `validate({"compute_limit":"medium"}, map_filepath="test.csv")` 后，`obstacle_ratio ≈ 0.20`、`map_height == 50`、`map_width == 50`、`data_source == "map_file"`
- [x] 解析到 `tasks` 时 `data_source == "benchmark"`，且 `start_point` / `target_point` 已自动填入
- [x] 不传 `map_filepath` 时 `data_source == "manual_params"`

## 模块导出（提示词 1-1 ~ 1-4）

- [x] `data/__init__.py` 导出 `DataManager` / `BenchmarkLoader` / `DataCardGenerator`
- [x] `map/__init__.py` 导出 `MapParser`
- [x] `python -c "from data import DataManager, BenchmarkLoader, DataCardGenerator; from map import MapParser; print('imports OK')"` 输出 `imports OK`

## 整体收口

- [x] `agents/data_agent.py` 的 `validate` 行为与 Phase 0 一致（合规输入 `input_validated == True`；非法 `start_point` 抛 `ValueError`）
- [x] 所有验证命令全部通过
- [x] 实现阶段所有 Sub-Agent 任务均按 tasks.md 执行完毕
