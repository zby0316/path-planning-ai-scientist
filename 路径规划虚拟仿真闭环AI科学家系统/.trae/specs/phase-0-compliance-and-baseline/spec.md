# Phase 0：合规体检与基础版封版 Spec

## Why

当前仓库虽然在 README 与代码中已隐含"基于 Qwen 多智能体的 AI Scientist 系统"定位，但 `config.py`、`llm/qwen_client.py`、`agents/data_agent.py` 三处仍残留"DeepSeek 为主、Qwen 仅命名兼容"的早期开发痕迹，且 `config.py` 关键阈值常量缺少中文语义注释、`agents/data_agent.py` 对可选输入字段未做类型与范围校验。这既影响系统的对外技术边界一致性，也使后续阶段的算法选型、实验复现与质量门控缺少稳固的输入护栏。需要在进入正式研究阶段之前完成一次合规体检并封版"基础版"。

## What Changes

- 在 `config.py` 顶部添加项目全称注释，并把所有阈值、权重、路径常量改为带中文语义注释的最终形态（提示词 0-1 + 0-4）。
- 新建项目根目录 `TECHNICAL_BOUNDARY.md`，声明 5 条技术边界：Qwen 为核心基础模型、DeepSeek 仅早期临时测试、算法选择由实验数据决定、算法白名单为 A\*/ACO/PSO/SA/混合优化算法、Qwen 智能体职责清单（提示词 0-1）。
- 统一 `llm/qwen_client.py` 的文件/类/`__init__` 注释，明确以 Qwen 为核心基础模型，DeepSeek 仅在开发初期临时使用（提示词 0-2）。
- 扩展 `agents/data_agent.py`：新增 `OPTIONAL_FIELDS`、`start_point`/`target_point`/`dynamic_change_rate` 类型与范围校验、输出 `input_validated` 与 `validation_timestamp`、校验异常统一包装为 `ValueError`（提示词 0-3）。

## Impact

- Affected specs：无既有 spec（首份 spec 文档）。
- Affected code：
  - `config.py`（修改）
  - `llm/qwen_client.py`（修改）
  - `agents/data_agent.py`（修改）
  - `TECHNICAL_BOUNDARY.md`（新建，仓库根目录）

## ADDED Requirements

### Requirement: 项目定位与技术边界一致化

系统 SHALL 在 `config.py` 顶部以注释形式声明完整项目名称为"基于 Qwen 多智能体系统的动态随机地图路径规划算法适配边界发现与科学假设生成系统"，并 SHALL 通过新建的 `TECHNICAL_BOUNDARY.md` 同时声明以下五项技术边界：

1. 系统以 Qwen 大模型作为多智能体架构的核心基础模型，所有智能体推理、决策与生成任务均基于 Qwen 实现；
2. DeepSeek 仅在系统开发初期、尚未获取 Qwen API 访问权限时，被临时用于功能测试与流程验证，并非系统的正式基础模型；
3. 最终算法选择由可复现实验数据和评分函数决定，Qwen 智能体不直接选择算法；
4. 允许的算法集合限制为 A\*、ACO、PSO、SA、混合优化算法；
5. Qwen 智能体负责：解释选型依据、从文献抽取事实、生成科学假设、生成实验计划、撰写研究报告、充当反思智能体。

#### Scenario: 项目全称注释可见
- **WHEN** 任意用户或工具打开 `config.py`
- **THEN** 第 1 行 SHALL 包含完整项目名称的中文注释

#### Scenario: 技术边界文档可被发现
- **WHEN** 用户在仓库根目录查询 `TECHNICAL_BOUNDARY.md`
- **THEN** 该文件 SHALL 存在，且 SHALL 完整覆盖上述 5 条边界声明

### Requirement: Qwen 客户端注释统一

`llm/qwen_client.py` SHALL 在文件头 docstring 中声明"本系统核心基础模型为 Qwen 大模型；开发初期曾临时使用 DeepSeek API 进行功能测试验证，待获取 Qwen API 权限后即切换为正式方案"；`QwenClient` 类 docstring SHALL 明确"本系统以 Qwen 大模型为智能体核心基础模型，对外统一称为 Qwen 多智能体系统"；`__init__` 方法 SHALL 包含 API Key 获取方式（环境变量）、DeepSeek 仅在开发初期临时用于功能测试的注释。

#### Scenario: 导入与注释一致性
- **WHEN** 执行 `python -c "from llm.qwen_client import QwenClient; print('import OK')"`
- **THEN** 输出 SHALL 为 `import OK`，且模块前 10 行 SHALL 准确反映 Qwen 为核心、DeepSeek 为临时测试方案

### Requirement: Data Agent 可选字段类型校验

`agents/data_agent.py` SHALL 声明 `OPTIONAL_FIELDS = ["start_point", "target_point", "dynamic_change_rate"]`，并在 `validate` 方法中：
- 当 `start_point`/`target_point` 存在时，必须为长度为 2、元素为 `int` 的列表/元组（即 `[int, int]`）；
- 当 `dynamic_change_rate` 存在时，必须在 `[0, 1]` 区间内；
- 校验通过后，SHALL 在返回的 `env` 字典上写入 `input_validated: True` 与 `validation_timestamp`（ISO-8601 字符串）；
- 任何校验失败 SHALL 被包装为统一 `ValueError`，异常信息 SHALL 包含字段名与非法值。

#### Scenario: 合规输入通过校验
- **WHEN** 调用 `DataReceiverAgent().validate({"obstacle_ratio":0.3,"map_width":100,"map_height":100,"connectivity":0.6,"topology_randomness":0.5,"compute_limit":"medium"})`
- **THEN** 返回字典 `env` 的 `input_validated` 字段 SHALL 为 `True`

#### Scenario: 非法 start_point 触发 ValueError
- **WHEN** 调用 `validate({"...","start_point":"invalid", ...})`
- **THEN** SHALL 抛出 `ValueError`，且异常信息 SHALL 包含字段名 `start_point`

### Requirement: config.py 中文注释与类型提示完整

`config.py` SHALL 为每个阈值/路径常量提供中文注释，格式为 `# 含义（取值范围/单位）`；`WEIGHTS` 字典每个嵌套键 SHALL 包含子指标含义注释；`ALGORITHM_PROFILE_PATH` 与 `HISTORICAL_RESULTS_PATH` 旁 SHALL 注明文件格式（JSON）。

#### Scenario: 注释不重复不矛盾
- **WHEN** 用户逐行审阅 `config.py`
- **THEN** 每条配置 SHALL 有清晰且不重复的中文注释

#### Scenario: 配置可被加载
- **WHEN** 执行 `python -c "import config; print('config OK')"`
- **THEN** 输出 SHALL 为 `config OK`，无报错

## MODIFIED Requirements

无（首份 spec 文档）。

## REMOVED Requirements

无（首份 spec 文档）。
