# Phase 7：后端工程化 Spec

## Why

当前系统缺乏统一的分级日志系统，调试只能依赖 `print` 和散落的 `logging.warning` 调用；没有 RESTful API 接口，外部系统无法集成调用；配置管理散落在 `config.py` 硬编码值中，缺乏环境变量覆盖机制。本阶段将补齐这三个工程化短板，使系统具备生产级可观测性、可集成性和可配置性。

## What Changes

- **提示词 7-1**：新建 `utils/logging_config.py`，提供统一的分级日志系统，配置 root logger 同时输出到文件（按日轮转）和控制台，日志级别从环境变量 `LOG_LEVEL` 读取，默认 INFO
- **提示词 7-2**：新建 `api/` 模块（`server.py` + `schemas.py`），提供 FastAPI RESTful 服务，含 5 个端点：`POST /analyze`、`POST /experiment`、`GET /experiment/{run_id}`、`GET /report/{run_id}`、`GET /health`，支持 CORS 跨域和请求速率限制
- **提示词 7-3**：完善 `config.py` 环境变量覆盖机制，所有路径/阈值/权重支持从环境变量或 JSON 文件加载，LLM 配置支持多 provider 切换，`.env.example` 补充至 15+ 个可配置项

## Impact

- Affected specs：无（全新工程化能力层，不修改既有业务逻辑）
- Affected code：
  - `utils/__init__.py`（新建）
  - `utils/logging_config.py`（新建）
  - `api/__init__.py`（新建）
  - `api/server.py`（新建）
  - `api/schemas.py`（新建）
  - `config.py`（修改，添加环境变量覆盖 + 日志配置项）
  - `.env.example`（修改，扩展至 15+ 配置项）
  - `requirements.txt`（修改，添加 `fastapi`、`uvicorn`）
  - `agents/orchestrator_agent.py`（修改，在 `run()` 中添加 info 日志）
  - `agents/` 下各智能体文件（修改，在异常捕获处添加 error 日志）

## ADDED Requirements

### Requirement: 统一分级日志系统

系统 SHALL 提供 `utils/logging_config.py` 模块，通过 `setup_logging()` 函数配置全局日志。

#### Scenario: 日志输出到文件和控制台
- **WHEN** 调用 `setup_logging()` 后使用 `logging.getLogger(__name__).info("test")`
- **THEN** 控制台打印格式为 `2026-06-09 10:00:00,000 [INFO] module_name: test` 的日志
- **AND** `data/logs/system.log` 文件包含相同格式的日志记录

#### Scenario: 日志级别从环境变量读取
- **WHEN** 环境变量 `LOG_LEVEL=DEBUG` 已设置
- **AND** 调用 `setup_logging()`
- **THEN** DEBUG 及以上级别的日志均被输出

#### Scenario: 默认日志级别
- **WHEN** 环境变量 `LOG_LEVEL` 未设置
- **AND** 调用 `setup_logging()`
- **THEN** 日志级别默认为 INFO

#### Scenario: 文件日志按日轮转
- **WHEN** 系统持续运行超过一天
- **THEN** 日志文件自动轮转，旧文件保留（如 `system.log.1`、`system.log.2`），最多保留 7 个备份文件

### Requirement: Orchestrator 关键节点日志

`OrchestratorAgent.run()` SHALL 在以下关键节点输出 INFO 级别日志：
- 流水线开始（含 env_input 摘要）
- 每个智能体步骤执行前（含步骤名称）
- 每个智能体步骤执行完成后（含耗时）
- 流水线完成（含总耗时和 state 摘要）

#### Scenario: 流水线执行日志追踪
- **WHEN** 调用 `OrchestratorAgent().run(env_input)`
- **THEN** 日志文件包含流水线开始、各步骤执行、流水线完成的完整记录

### Requirement: 智能体异常 error 日志

所有智能体的 `except` 块 SHALL 在已有处理逻辑基础上，增加 `logger.error()` 调用，记录完整的异常信息和堆栈。

#### Scenario: 智能体执行失败时记录 error 日志
- **WHEN** 任一智能体的 `_safe_step` 捕获异常
- **THEN** 日志文件包含 ERROR 级别记录，含异常类型和堆栈信息

### Requirement: FastAPI RESTful API 服务

系统 SHALL 提供 `api/server.py` 作为 FastAPI 应用入口。

#### Scenario: 健康检查端点
- **WHEN** 发送 `GET /health` 请求
- **THEN** 返回 `{"status": "ok"}` 和 HTTP 200

#### Scenario: 分析端点
- **WHEN** 发送 `POST /analyze` 请求，Body 为 `{"obstacle_ratio":0.35,"map_width":100,"map_height":100,"connectivity":0.68,"topology_randomness":0.55,"compute_limit":"medium"}`
- **THEN** 返回完整 ResearchState JSON（含 decision、hypothesis 等字段）

#### Scenario: 实验端点
- **WHEN** 发送 `POST /experiment` 请求，Body 含实验配置（算法列表、地图参数、运行次数等）
- **THEN** 返回 `{"run_id": "exp_xxx", "status": "running"}` 和 HTTP 202

#### Scenario: 实验状态查询
- **WHEN** 发送 `GET /experiment/{run_id}` 请求
- **THEN** 返回该实验的当前状态和结果（含 status、progress、results 字段）

#### Scenario: 报告获取
- **WHEN** 发送 `GET /report/{run_id}` 请求
- **THEN** 返回该 run_id 对应的 Markdown 研究报告文本

#### Scenario: CORS 跨域支持
- **WHEN** 从任意域名的前端页面发送 API 请求
- **THEN** 响应包含正确的 CORS 头，请求不被浏览器拦截

#### Scenario: 请求速率限制
- **WHEN** 同一 IP 在 60 秒内请求超过 30 次
- **THEN** 返回 HTTP 429 `{"detail": "Too many requests"}`

### Requirement: Pydantic 请求/响应模型

`api/schemas.py` SHALL 定义以下 Pydantic BaseModel：

- `EnvInputRequest`：环境参数输入（obstacle_ratio、map_width、map_height、connectivity、topology_randomness、compute_limit、start_point、target_point）
- `DecisionResponse`：决策结果（best_algorithm、best_score、ranking、scene_level、confidence）
- `HypothesisResponse`：科学假设（hypothesis_text、experiment_plan、expected_results、boundary_conditions）
- `ReportResponse`：完整研究报告（title、abstract、sections、references）
- `ExperimentRequest`：实验请求（algorithms、map_params、n_runs、compute_limit）
- `ExperimentResponse`：实验响应（run_id、status、progress、results、created_at）

#### Scenario: 请求参数校验
- **WHEN** 发送 `POST /analyze` 请求，`obstacle_ratio` 字段值为 1.5（超出 0-1 范围）
- **THEN** 返回 HTTP 422 验证错误，含字段名和错误描述

### Requirement: 环境变量全覆盖配置

`config.py` SHALL 支持所有路径、阈值、权重、LLM 配置通过环境变量覆盖。

#### Scenario: 路径从环境变量覆盖
- **WHEN** 设置 `KB_DIR=test_kb` 环境变量
- **THEN** `config.KNOWLEDGE_BASE_DIR` 值为 `"test_kb"`

#### Scenario: 阈值从环境变量覆盖
- **WHEN** 设置 `OBSTACLE_LOW_THRESHOLD=0.15` 环境变量
- **THEN** `config.OBSTACLE_LOW_THRESHOLD` 值为 0.15

#### Scenario: LLM Provider 切换
- **WHEN** 设置 `LLM_PROVIDER=qwen` 环境变量
- **THEN** `config.LLM_PROVIDER` 值为 `"qwen"`
- **WHEN** 未设置 `LLM_PROVIDER`
- **THEN** `config.LLM_PROVIDER` 默认值为 `"deepseek"`

#### Scenario: 评分权重从 JSON 加载
- **WHEN** 设置 `WEIGHTS_JSON='{"低复杂度":{"time":0.30}}'` 环境变量
- **THEN** `config.WEIGHTS["低复杂度"]["time"]` 值为 0.30

### Requirement: .env.example 完备配置模板

`.env.example` SHALL 包含至少 15 个可配置项，每项附中文注释说明用途和取值范围。

#### Scenario: .env.example 完整性
- **WHEN** 检查 `.env.example` 文件
- **THEN** 包含 DEEPSEEK_API_KEY、LLM_PROVIDER、LOG_LEVEL、KB_DIR、EXPERIMENT_DB_PATH、DATA_DIR、MAPS_DIR、LOGS_DIR、REPORTS_DIR、OBSTACLE_LOW_THRESHOLD、OBSTACLE_MEDIUM_THRESHOLD、WEIGHTS_JSON、SCORE_GAP_THRESHOLD、DEFAULT_MAP_WIDTH、DEFAULT_MAP_HEIGHT 等至少 15 个配置项，每项附有中文注释

## MODIFIED Requirements

### Requirement: config.py 路径/阈值/权重/LLM 配置项（来自 Phase 0）

`config.py` 中所有的路径配置（`KNOWLEDGE_BASE_DIR`、`DATA_DIR`、`MAPS_DIR`、`EXPERIMENTS_DIR`、`LOGS_DIR`、`REPORTS_DIR`）、阈值配置（`OBSTACLE_LOW_THRESHOLD`、`OBSTACLE_MEDIUM_THRESHOLD`、`POOR_CONNECTIVITY_THRESHOLD`、`SCORE_GAP_THRESHOLD` 等所有惩罚阈值）、权重配置（`WEIGHTS`）、LLM 配置 SHALL 使用 `os.getenv("VAR", default)` 模式读取，优先环境变量，回退到原硬编码默认值。`config.py` 底部 SHALL 添加 `LOG_LEVEL` 和 `LOG_FILE` 两个日志配置项：

```python
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "data/logs/system.log")
```

新增 LLM Provider 相关配置项：

```python
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "deepseek")
```

## REMOVED Requirements

无。所有原 `config.py` 中的硬编码默认值均保留为回退默认值，不删除任何配置项。
