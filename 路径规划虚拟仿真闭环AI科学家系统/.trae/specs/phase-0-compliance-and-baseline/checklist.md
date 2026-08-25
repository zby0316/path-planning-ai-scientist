# Checklist（Phase 0 合规体检与基础版封版）

> 验证方法：每个条目在实现完成后由 Sub-Agent 或主流程实际执行/审阅，并通过在条目开头勾选 `[x]` 标记通过。

## 项目定位与边界（提示词 0-1）

- [x] `config.py` 第 1 行包含完整项目名称中文注释：`基于 Qwen 多智能体系统的动态随机地图路径规划算法适配边界发现与科学假设生成系统`
- [x] 仓库根目录存在 `TECHNICAL_BOUNDARY.md`
- [x] `TECHNICAL_BOUNDARY.md` 第 1 条边界声明：Qwen 为核心基础模型
- [x] `TECHNICAL_BOUNDARY.md` 第 2 条边界声明：DeepSeek 仅开发初期临时测试
- [x] `TECHNICAL_BOUNDARY.md` 第 3 条边界声明：算法选择由实验数据决定，Qwen 不直接选算法
- [x] `TECHNICAL_BOUNDARY.md` 第 4 条边界声明：算法白名单 A\*/ACO/PSO/SA/混合优化算法
- [x] `TECHNICAL_BOUNDARY.md` 第 5 条边界声明：Qwen 智能体职责清单（解释选型、抽取事实、生成假设、生成实验计划、撰写报告、反思）

## Qwen 客户端注释（提示词 0-2）

- [x] `llm/qwen_client.py` 文件头注释已替换为以 Qwen 为核心、DeepSeek 为临时测试的声明
- [x] `QwenClient` 类 docstring 已明确以 Qwen 为核心基础模型
- [x] `__init__` 方法注释包含 API Key 来自环境变量、DeepSeek 仅临时使用的说明
- [x] `python -c "from llm.qwen_client import QwenClient; print('import OK')"` 输出 `import OK`
- [x] 阅读 `llm/qwen_client.py` 前 10 行，确认 Qwen 为核心、DeepSeek 为临时测试方案的技术选型描述准确

## Data Agent 输入校验（提示词 0-3）

- [x] `agents/data_agent.py` 中存在 `OPTIONAL_FIELDS = ["start_point", "target_point", "dynamic_change_rate"]`
- [x] `validate` 方法对 `start_point` / `target_point` 进行 `[int, int]` 长度与类型校验
- [x] `validate` 方法对 `dynamic_change_rate` 进行 `[0, 1]` 区间校验
- [x] 校验通过后 `env` 中包含 `input_validated: True`
- [x] 校验通过后 `env` 中包含 `validation_timestamp`（ISO-8601 字符串）
- [x] 所有校验异常被统一包装为 `ValueError`，且异常信息包含字段名与非法值
- [x] 合规输入校验通过：`python -c "from agents.data_agent import DataReceiverAgent; a=DataReceiverAgent(); r=a.validate({'obstacle_ratio':0.3,'map_width':100,'map_height':100,'connectivity':0.6,'topology_randomness':0.5,'compute_limit':'medium'}); print(r.get('input_validated'))"` 输出 `True`
- [x] 非法 `start_point: "invalid"` 抛出 `ValueError`，且异常信息包含 `start_point`

## config.py 中文注释（提示词 0-4）

- [x] `config.py` 第 1 行包含完整项目名称中文注释（与提示词 0-1 共享）
- [x] 所有阈值常量（OBSTACLE_LOW/MEDIUM、PENALTY_*、POOR_CONNECTIVITY_THRESHOLD、SCORE_GAP_THRESHOLD 等）均有 `# 含义（取值范围/单位）` 形式的中文注释
- [x] `WEIGHTS` 字典每个嵌套键（time/path_length/success_rate/stability）已添加子指标含义注释
- [x] `ALGORITHM_PROFILE_PATH` 旁标注文件格式（JSON）
- [x] `HISTORICAL_RESULTS_PATH` 旁标注文件格式（JSON）
- [x] `python -c "import config; print('config OK')"` 输出 `config OK`
- [x] 审阅 `config.py`，确认注释不重复、不矛盾

## 整体收口

- [x] `config.py`、`llm/qwen_client.py`、`agents/data_agent.py` 三处导入/加载无报错
- [x] `TECHNICAL_BOUNDARY.md` 与 `config.py` 第 1 行注释表述一致
- [x] 实现阶段所有 Sub-Agent 任务均按 tasks.md 执行完毕
