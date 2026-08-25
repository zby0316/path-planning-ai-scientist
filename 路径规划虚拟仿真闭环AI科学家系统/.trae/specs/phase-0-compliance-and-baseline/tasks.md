# Tasks

> 范围：Phase 0 合规体检与基础版封版，对应提示词 0-1 ~ 0-4。
> 实现阶段需先阅读 `.trae/specs/phase-0-compliance-and-baseline/spec.md`。

- [x] Task 1（提示词 0-1）：统一项目定位与 `config.py` 顶部注释
  - [x] SubTask 1.1：在 `config.py` 第 1 行添加项目全称注释：`基于 Qwen 多智能体系统的动态随机地图路径规划算法适配边界发现与科学假设生成系统`
  - [x] SubTask 1.2：新建仓库根目录 `TECHNICAL_BOUNDARY.md`，完整写入 5 条边界声明（Qwen 核心基础模型 / DeepSeek 临时测试 / 算法选择由数据决定 / 算法白名单 / Qwen 智能体职责）
  - [x] SubTask 1.3：仓库根目录无 README.md，按 spec 约定不创建新文件；任务视为 N/A

- [x] Task 2（提示词 0-1）：新建 `TECHNICAL_BOUNDARY.md` 的内容自检
  - [x] SubTask 2.1：验证 `TECHNICAL_BOUNDARY.md` 包含 5 条边界声明
  - [x] SubTask 2.2：验证 `config.py` 第 1 行注释完整且与 `TECHNICAL_BOUNDARY.md` 表述一致

- [x] Task 3（提示词 0-2）：统一 `llm/qwen_client.py` 注释与 docstring
  - [x] SubTask 3.1：将文件头注释更新为：`Qwen API 客户端（本系统核心基础模型为 Qwen 大模型；开发初期曾临时使用 DeepSeek API 进行功能测试验证，待获取 Qwen API 权限后即切换为正式方案）`
  - [x] SubTask 3.2：将 `QwenClient` 类 docstring 更新为：本系统以 Qwen 大模型为智能体核心基础模型，对外统一称为 Qwen 多智能体系统
  - [x] SubTask 3.3：在 `__init__` 中添加注释：API Key 来自环境变量、DeepSeek 仅开发初期临时用于功能测试，正式部署以 Qwen API 为准
  - [x] SubTask 3.4：执行 `python -c "from llm.qwen_client import QwenClient; print('import OK')"`，确认导入正常

- [x] Task 4（提示词 0-3）：扩展 `agents/data_agent.py` 校验逻辑
  - [x] SubTask 4.1：在 `DataReceiverAgent` 类中新增 `OPTIONAL_FIELDS = ["start_point", "target_point", "dynamic_change_rate"]`
  - [x] SubTask 4.2：在 `validate` 方法中：若 `start_point`/`target_point` 存在，必须为长度 2 且元素均为 `int` 的序列；若 `dynamic_change_rate` 存在，必须在 `[0, 1]` 区间
  - [x] SubTask 4.3：校验通过后，向 `env` 写入 `input_validated: True` 与 `validation_timestamp`（ISO-8601 字符串，UTC）
  - [x] SubTask 4.4：将所有校验异常统一包装为 `ValueError`，异常信息包含字段名与非法值
  - [x] SubTask 4.5：执行 `python -c "from agents.data_agent import DataReceiverAgent; a=DataReceiverAgent(); r=a.validate({'obstacle_ratio':0.3,'map_width':100,'map_height':100,'connectivity':0.6,'topology_randomness':0.5,'compute_limit':'medium'}); print(r.get('input_validated'))"`，输出应为 `True`
  - [x] SubTask 4.6：传入 `start_point: "invalid"` 必须抛出 `ValueError`

- [x] Task 5（提示词 0-4）：完善 `config.py` 中文注释
  - [x] SubTask 5.1：为每个阈值常量添加 `# 含义（取值范围/单位）` 形式的中文注释
  - [x] SubTask 5.2：为 `WEIGHTS` 字典中每个嵌套键（time/path_length/success_rate/stability）添加子指标含义注释
  - [x] SubTask 5.3：为 `ALGORITHM_PROFILE_PATH` 与 `HISTORICAL_RESULTS_PATH` 旁添加 JSON 格式说明
  - [x] SubTask 5.4：执行 `python -c "import config; print('config OK')"`，确认无报错

# Task Dependencies

- Task 2（自检）依赖 Task 1（生成边界文档）
- Task 3 与 Task 4 与 Task 5 相互独立，可并行执行
- 整体收口（运行验证命令）依赖 Task 1 ~ Task 5 全部完成
