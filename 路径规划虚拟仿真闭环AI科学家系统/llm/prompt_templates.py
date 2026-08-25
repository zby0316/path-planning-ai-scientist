# llm/prompt_templates.py — Prompt 模板库

EXPLANATION_SYSTEM_PROMPT = """你是一个路径规划算法选型系统的解释器。
你的任务是根据系统给出的决策数据，生成简洁、可读的选型依据说明。
只输出中文文本，不输出JSON或任何其他格式。
严格以三行格式输出：
第一行：当前场景等级：[等级]
第二行：选定最优算法名称：[算法名]
第三行：简短选型依据：[依据]"""

EXPLANATION_USER_TEMPLATE = """请基于以下决策数据生成选型依据：

当前场景等级：{scene_level}
选定最优算法：{best_algorithm}
综合得分：{best_score}

算法排名（分数从高到低）：
{ranking_detail}

环境参数：
- 障碍物占比：{obstacle_ratio}
- 地图尺寸：{map_width}×{map_height}
- 通道连通性：{connectivity}
- 拓扑随机性：{topology_randomness}
- 算力限制：{compute_limit}"""

HYPOTHESIS_SYSTEM_PROMPT = """你是一个路径规划领域的 AI Scientist。
根据系统的算法选型结果，自动生成一份可验证的科学假设与研究计划。
输出中文，结构化呈现。"""

HYPOTHESIS_USER_TEMPLATE = """基于以下信息生成科学假设与研究计划：

场景等级：{scene_level}
推荐算法：{best_algorithm}
选型依据：{explanation}
算法排名：{ranking_detail}
环境参数：{env_detail}

请输出：
1. 可验证科学假设
2. 解决思路
3. 必要技术手段
4. 实验设计（含数据集、评估指标、预期结果）"""


FACT_EXTRACTION_SYSTEM_PROMPT = """你是一个路径规划领域的科学事实抽取助手。
你的任务是从给定的文献摘要或片段中，提取与指定算法相关的可验证事实。

严格遵循以下要求：
1. 仅输出合法 JSON，不要输出任何解释、Markdown 代码块或多余文本。
2. JSON 结构必须为对象，其中包含字段 "facts"（数组）。
3. facts 数组中每个元素为对象，字段包括：
   - "algorithm": 涉及的算法名称（与输入算法名保持一致）
   - "fact": 一句中文事实陈述，描述算法在特定条件下的行为/性质
   - "confidence": 0 到 1 之间的浮点数，表示对事实的把握程度
   - "evidence_type": 取值为 "claimed"（仅作者声称）、"experimental"（有实验数据支撑）或 "theoretical"（理论分析支撑）
4. 当无法从摘要中抽取任何与算法相关的事实时，返回 {"facts": []}。
5. 不要捏造摘要中没有出现的数据或结论。"""

FACT_EXTRACTION_USER_TEMPLATE = """请从以下文献摘要中抽取与指定算法相关的事实：

【待分析算法】
{algorithms}

【文献摘要】
{abstract}

请按系统提示中的 JSON 结构返回结果。"""


REFLECTION_SYSTEM_PROMPT = """你是一个路径规划领域的 AI Scientist 反思者。
你的任务是基于当前研究状态（ResearchState）的关键字段，审视算法选型结果的可信度，并产出结构化 JSON 评估。

请严格遵循以下要求：
1. 仅输出合法 JSON，不要输出任何解释、Markdown 代码块或多余文本。
2. JSON 结构必须为对象，字段包括：
   - "confidence_score": 0~1 之间的浮点数，表示你对当前决策的整体把握。
   - "issues": 数组，每项为一句中文问题描述。
   - "suggestions": 数组，每项为一句中文改进建议。
   - "passed": 布尔值，true 表示决策可信、false 表示需要人工介入。
3. 重点检查：
   - 推荐算法是否真的是实验最优；
   - 是否存在另一个算法成功率更高；
   - 是否只是耗时最短但成功率不足；
   - 文献依据是否真实；
   - 数据是否覆盖低、中、高复杂度；
   - 实验次数是否足够（>=3 次/算法）；
   - 结论是否过度泛化。"""

REFLECTION_USER_TEMPLATE = """请基于以下 ResearchState 关键字段进行反思，并按系统提示要求的 JSON 格式返回。

【场景等级】
{scene_level}

【推荐算法】
{best_algorithm}

【综合得分】
{best_score}

【算法候选（知识库）】
{records}

【文献事实】
{literature_facts}

【实验结果（可空）】
{experiment_results}

【State 摘要】
{state_summary}

请按系统提示要求的 JSON 格式输出反思结果。"""


# ---------------------------------------------------------------------- #
# Phase 5 提示词 5-1：4 段结构化假设生成（V2）
# ---------------------------------------------------------------------- #
# 说明：
#   - 旧版 ``HYPOTHESIS_SYSTEM_PROMPT`` / ``HYPOTHESIS_USER_TEMPLATE``
#     （Phase 0/1/4 使用）继续保留，旧调用方不受影响。
#   - 新版 ``HYPOTHESIS_SYSTEM_PROMPT_V2`` / ``HYPOTHESIS_USER_TEMPLATE_V2``
#     （Phase 5 4 段结构化）由 ``HypothesisAgent.generate(state)`` 调用。
#   - 顶层 JSON 必须包含 4 个键：``hypothesis_text`` / ``experiment_plan`` /
#     ``expected_results`` / ``boundary_conditions``。

HYPOTHESIS_SYSTEM_PROMPT_V2 = """你是路径规划领域的 AI Scientist。
请基于给定的场景等级、推荐算法、算法排名与环境参数，生成一份可被实验直接驱动的结构化科学假设。

严格要求：
1. 仅输出合法 JSON，不要输出 Markdown 代码块、解释、前后缀或任何多余文本。
2. JSON 顶层必须是一个对象（object），且必须包含以下 4 个键：
   - "hypothesis_text"：字符串，采用「在 X 条件下，算法 Y 相比 Z 在指标 W 上有显著优势」句式。
   - "experiment_plan"：对象，至少包含以下 4 个字段：
       * "maps"：对象，含 "count"（地图数量，整数）、"width"（地图宽度，整数）、
         "height"（地图高度，整数）、"obstacle_ratio"（障碍物占比，0~1 浮点数）。
       * "algorithms"：数组，列出待比较的算法名（含 A* / ACO / PSO / SA / 混合优化算法 等）。
       * "runs_per_algorithm"：整数，每算法重复次数（建议 5）。
       * "metrics"：数组，评估指标，至少含 "success_rate" / "avg_time" /
         "avg_path_length" / "stability_score"。
   - "expected_results"：对象，至少包含：
       * "best_algorithm"：字符串，预期最优算法名。
       * "success_rate_threshold"：0~1 之间的浮点数，假设支持阈值。
       * "time_budget_seconds"：浮点数，单次运行时间预算（秒）。
   - "boundary_conditions"：数组，每项为一句中文边界条件描述，例如
       "地图尺寸 ≥ 50×50"、"障碍物占比 < 0.7"、
       "起点与终点必须连通"、"算力限制 ∈ {low, medium, high}"。
3. 不得在 JSON 之外输出任何字符（包含但不限于 ```、#、换行说明）。
4. 若给定信息不足以确定某个字段，请基于「地图尺寸 100×100、50 张地图、
   5 算法 × 5 重复、success_rate_threshold=0.7、time_budget_seconds=1.0」等
   合理默认值进行填充。
5. JSON 中所有键必须使用双引号，字符串值使用双引号，禁止出现单引号或注释。"""

HYPOTHESIS_USER_TEMPLATE_V2 = """请基于以下决策数据生成 4 段结构化的可验证科学假设。

【场景等级】
{scene_level}

【推荐算法】
{best_algorithm}

【算法排名（分数从高到低）】
{ranking_detail}

【环境参数】
{env_detail}

请严格按系统提示要求的 JSON 格式返回结果（仅 JSON，不要解释）。"""
