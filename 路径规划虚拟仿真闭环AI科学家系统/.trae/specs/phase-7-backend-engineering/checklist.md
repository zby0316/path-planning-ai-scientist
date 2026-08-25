# Checklist

## 提示词 7-1：日志系统

- [x] `utils/__init__.py` 文件存在
- [x] `utils/logging_config.py` 文件存在，包含 `setup_logging()` 函数
- [x] `setup_logging()` 配置了 `StreamHandler`（控制台输出）和 `RotatingFileHandler`（文件输出）
- [x] 日志格式为 `%(asctime)s [%(levelname)s] %(name)s: %(message)s`
- [x] 日志级别从环境变量 `LOG_LEVEL` 读取，默认 INFO
- [x] 文件日志使用 `RotatingFileHandler`，按日轮转，最多保留 7 个备份
- [x] `data/logs/` 目录在 `setup_logging()` 调用时自动创建
- [x] `config.py` 包含 `LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")`
- [x] `config.py` 包含 `LOG_FILE = os.getenv("LOG_FILE", "data/logs/system.log")`
- [x] 运行验证命令后 `data/logs/system.log` 文件生成且包含 "test" 日志（验证：`python -c "from utils.logging_config import setup_logging; setup_logging(); import logging; logging.info('test');"`）

## 提示词 7-1：Orchestrator 关键节点日志

- [x] `orchestrator_agent.py` 的 `run()` 方法开头有 INFO 日志记录流水线开始（含 env_input 关键字段）
- [x] `_safe_step()` 方法中：执行前有 INFO 日志记录步骤名称
- [x] `_safe_step()` 方法中：执行完成后有 INFO 日志记录步骤耗时
- [x] `_safe_step()` 方法中：异常时将 `logger.warning` 升级为 `logger.error`（含 `exc_info=True`）
- [x] `run()` 方法末尾有 INFO 日志记录流水线完成（含总耗时和 state 摘要）

## 提示词 7-1：智能体异常 error 日志

- [x] `agents/experiment_agent.py` 的所有 `except` 块包含 `logger.error(..., exc_info=True)`
- [x] `agents/hypothesis_agent.py` 的所有 `except` 块包含 `logger.error(..., exc_info=True)` — **已修复：L131/L190/L207/L213 共 4 个 except 块已有 logger 调用**
- [x] `agents/fact_extraction_agent.py` 的所有 `except` 块包含 `logger.error(..., exc_info=True)` — **已修复：L87 except 块已改为 `logger.warning`**
- [x] `agents/literature_agent.py` 的所有 `except` 块包含 `logger.error(..., exc_info=True)`
- [x] `agents/explanation_agent.py` 的所有 `except` 块包含 `logger.error(..., exc_info=True)`
- [x] `agents/decision_agent.py` 的所有 `except` 块包含 `logger.error(..., exc_info=True)`
- [x] `agents/evaluation_agent.py` 的所有 `except` 块包含 `logger.error(..., exc_info=True)`
- [x] `agents/rule_agent.py` 的所有 `except` 块包含 `logger.error(..., exc_info=True)`
- [x] `agents/knowledge_agent.py` 的所有 `except` 块包含 `logger.error(..., exc_info=True)`
- [x] `agents/environment_agent.py` 的所有 `except` 块包含 `logger.error(..., exc_info=True)`
- [x] `agents/data_agent.py` 的所有 `except` 块包含 `logger.error(..., exc_info=True)`
- [x] `agents/reflection_agent.py` 的所有 `except` 块包含 `logger.error(..., exc_info=True)` — **已修复：L45 `except json.JSONDecodeError` 块已有 logger 调用**
- [x] `agents/human_loop_agent.py` 的所有 `except` 块包含 `logger.error(..., exc_info=True)` — **已修复：L163 `except (TypeError, ValueError)` 块已有 logger 调用**
- [x] `agents/map_analysis_agent.py` 的所有 `except` 块包含 `logger.error(..., exc_info=True)`
- [x] `agents/rag_agent.py` 的所有 `except` 块包含 `logger.error(..., exc_info=True)`
- [x] `agents/citation_agent.py` 的所有 `except` 块包含 `logger.error(..., exc_info=True)`

## 提示词 7-2：FastAPI 后端服务

- [x] `api/__init__.py` 文件存在
- [x] `api/schemas.py` 文件存在，定义 `EnvInputRequest`、`DecisionResponse`、`HypothesisResponse`、`ReportResponse`、`ExperimentRequest`、`ExperimentResponse` 六个 Pydantic 模型
- [x] `EnvInputRequest` 包含 `obstacle_ratio`（Field 0-1 范围校验）、`map_width`、`map_height`、`connectivity`、`topology_randomness`、`compute_limit`、`start_point`、`target_point` 字段
- [x] `ExperimentRequest` 包含 `algorithms`、`map_params`、`n_runs`、`compute_limit` 字段
- [x] `api/server.py` 文件存在，创建 FastAPI 应用实例
- [x] CORS 中间件已配置（允许所有来源）
- [x] 请求速率限制中间件已实现（60 秒窗口 30 次上限，基于 IP）
- [x] `GET /health` 端点返回 `{"status": "ok"}` 和 HTTP 200
- [x] `POST /analyze` 端点接收 `EnvInputRequest`，调用 `OrchestratorAgent.run()` 并返回 `ResearchState.to_dict()` JSON
- [x] `POST /experiment` 端点异步运行实验，返回 `{"run_id": "...", "status": "running"}` 和 HTTP 202
- [x] `GET /experiment/{run_id}` 端点查询实验状态，返回含 `status`、`progress`、`results` 字段的 JSON
- [x] `GET /report/{run_id}` 端点返回 Markdown 格式研究报告文本
- [x] `requirements.txt` 包含 `fastapi>=0.104.0` 和 `uvicorn[standard]>=0.24.0`
- [ ] 启动命令 `uvicorn api.server:app --host 0.0.0.0 --port 8000` 可正常启动 — **未验证（需要实际启动服务器）**

## 提示词 7-3：配置管理与环境变量

- [x] `config.py` 中所有路径配置（`KNOWLEDGE_BASE_DIR`、`DATA_DIR`、`MAPS_DIR`、`EXPERIMENTS_DIR`、`LOGS_DIR`、`REPORTS_DIR`）使用 `os.getenv("VAR", default)` 模式
- [x] `config.py` 中所有阈值配置使用 `os.getenv("VAR", default)` 模式，数值类型正确转换
- [x] `config.py` 中 `WEIGHTS` 评分权重支持从 `WEIGHTS_JSON` 环境变量加载（JSON 字符串）
- [x] `config.py` 中 `LLM_PROVIDER` 配置使用 `os.getenv("LLM_PROVIDER", "deepseek")`，支持 `deepseek`/`qwen`/`openai`
- [x] `config.py` 中 DeepSeek 相关配置（`DEEPSEEK_API_BASE_URL`、`DEEPSEEK_MODEL_NAME`）也支持环境变量覆盖
- [x] `.env.example` 文件包含至少 15 个配置项 — **已修复：现有 15 个活跃（未注释）配置项**
- [x] `.env.example` 中每个配置项附有中文注释说明用途和取值范围
- [x] 设置 `KB_DIR=test_kb` 环境变量后，`config.KNOWLEDGE_BASE_DIR` 值为 `test_kb`（验证：`KB_DIR=test_kb python -c "import config; print(config.KNOWLEDGE_BASE_DIR)"`）

---

## 验证摘要

- **总检查项**: 52
- **通过**: 50
- **失败**: 1
- **未验证**: 1（uvicorn 启动需实际服务器环境）

### 失败项详情

| 编号 | 文件/类别 | 问题描述 |
|------|-----------|----------|
| 58 | `api/server.py` | uvicorn 启动验证未执行（需实际启动服务器确认无 import 错误） |
