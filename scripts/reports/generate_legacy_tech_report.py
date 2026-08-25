import os
from datetime import datetime
from pathlib import Path
from docx import Document
from docx.shared import Pt, Inches, Cm, RGBColor, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKUP_DIR = REPO_ROOT / "archive" / "legacy_backup"
OUTPUT_DIR = REPO_ROOT / "assets" / "reports" / "final"
OUTPUT_FILE = OUTPUT_DIR / "多智能体AI_Scientist系统技术报告.docx"


def set_cell_shading(cell, color):
    shading_elm = OxmlElement('w:shd')
    shading_elm.set(qn('w:fill'), color)
    shading_elm.set(qn('w:val'), 'clear')
    cell._tc.get_or_add_tcPr().append(shading_elm)


def add_table_row(table, cells_text, bold=False, header=False):
    row = table.add_row()
    for i, text in enumerate(cells_text):
        cell = row.cells[i]
        cell.text = ""
        p = cell.paragraphs[0]
        run = p.add_run(str(text))
        run.font.size = Pt(9)
        run.font.name = "宋体"
        run._element.rPr.rFonts.set(qn('w:eastAsia'), "宋体")
        run.bold = bold
        if header:
            set_cell_shading(cell, "2F5496")
            run.font.color.rgb = RGBColor(255, 255, 255)
    return row


def add_heading(doc, text, level=1):
    heading = doc.add_heading(text, level=level)
    for run in heading.runs:
        run.font.name = "黑体"
        run._element.rPr.rFonts.set(qn('w:eastAsia'), "黑体")
    return heading


def add_para(doc, text, bold=False, font_size=12, indent=False):
    p = doc.add_paragraph()
    if indent:
        p.paragraph_format.first_line_indent = Cm(0.74)
    p.paragraph_format.line_spacing = 1.5
    run = p.add_run(text)
    run.font.size = Pt(font_size)
    run.font.name = "宋体"
    run._element.rPr.rFonts.set(qn('w:eastAsia'), "宋体")
    run.bold = bold
    return p


def add_code_block(doc, code_text):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(1)
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(4)
    run = p.add_run(code_text)
    run.font.size = Pt(8)
    run.font.name = "Consolas"
    run._element.rPr.rFonts.set(qn('w:eastAsia'), "Consolas")
    return p


def add_bullet(doc, text, level=0):
    p = doc.add_paragraph(style='List Bullet')
    p.clear()
    run = p.add_run(text)
    run.font.size = Pt(11)
    run.font.name = "宋体"
    run._element.rPr.rFonts.set(qn('w:eastAsia'), "宋体")
    if level > 0:
        p.paragraph_format.left_indent = Cm(1.5 * (level + 1))
    return p


def read_file_snippet(filepath, start_line=None, end_line=None):
    full_path = os.path.join(BACKUP_DIR, filepath)
    if not os.path.exists(full_path):
        return f"[文件不存在: {filepath}]"
    with open(full_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    if start_line is None:
        start_line = 1
    if end_line is None:
        end_line = len(lines)
    snippet = "".join(lines[max(0, start_line - 1):min(len(lines), end_line)])
    return snippet


def create_cover(doc):
    for _ in range(6):
        doc.add_paragraph()
    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title_p.add_run("多智能体 AI Scientist 系统技术报告")
    run.font.size = Pt(28)
    run.font.name = "黑体"
    run._element.rPr.rFonts.set(qn('w:eastAsia'), "黑体")
    run.bold = True
    run.font.color.rgb = RGBColor(47, 84, 150)

    sub_p = doc.add_paragraph()
    sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = sub_p.add_run("——基于 Qwen 多智能体系统的动态随机地图路径规划算法自适应选型与科学假设生成系统")
    run.font.size = Pt(14)
    run.font.name = "宋体"
    run._element.rPr.rFonts.set(qn('w:eastAsia'), "宋体")
    run.font.color.rgb = RGBColor(89, 89, 89)

    for _ in range(4):
        doc.add_paragraph()

    info_items = [
        f"版本：Phase 4-7 完整版",
        f"日期：{datetime.now().strftime('%Y年%m月%d日')}",
        "基座模型：阿里云通义千问 (Qwen)",
        "技术栈：Python + FastAPI + Streamlit + SQLite",
        "代码规模：50+ Python 源文件，约 3500+ 行",
    ]
    for item in info_items:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(item)
        run.font.size = Pt(12)
        run.font.name = "宋体"
        run._element.rPr.rFonts.set(qn('w:eastAsia'), "宋体")
    doc.add_page_break()


def generate_report():
    doc = Document()

    style = doc.styles['Normal']
    style.font.name = "宋体"
    style.font.size = Pt(12)
    style._element.rPr.rFonts.set(qn('w:eastAsia'), "宋体")

    create_cover(doc)

    # ================================================================
    add_heading(doc, "摘要", level=1)
    add_para(doc,
        "本报告系统阐述了一套面向路径规划领域的多智能体 AI Scientist 系统。该系统基于阿里云通义千问（Qwen）大模型构建，"
        "采用14个专业化智能体协同工作的架构，集成A*、蚁群优化（ACO）、粒子群优化（PSO）、模拟退火（SA）及混合优化算法五种路径规划算法，"
        "实现了从地图输入、环境建模、算法自适应选型、假设生成、实验验证到反思迭代的完整科学发现闭环。"
        "系统以 Streamlit 为前端交互框架，FastAPI 为后端服务层，SQLite 为实验数据库，支持动态随机地图的路径规划算法智能选型决策与可验证科学假设的自动生成。"
        "本报告从系统架构、多智能体设计、算法实现、评估体系、大模型集成、知识库管理等多个维度对该系统进行了全面深入的技术阐述。",
        indent=True
    )
    add_para(doc, "关键词：多智能体系统；AI Scientist；路径规划；算法自适应选型；大语言模型；科学假设生成", bold=True, indent=True)

    # ================================================================
    add_heading(doc, "第1章 引言", level=1)

    add_heading(doc, "1.1 项目背景", level=2)
    add_para(doc,
        "路径规划是移动机器人、自动驾驶、无人机巡检、仓储物流等领域的核心技术问题。"
        "随着应用场景的日益复杂化，单一的路径规划算法难以在所有场景下均表现最优。"
        "如何根据地图特征、算力约束和任务需求，自适应地选择或组合最优算法，成为一个亟待解决的关键问题。",
        indent=True
    )
    add_para(doc,
        "与此同时，大语言模型（LLM）技术的快速发展为构建具备推理、解释和假设生成能力的智能系统提供了新的可能。"
        "阿里巴巴\u201c基于国产开源大模型的AI科学家研发与应用比赛\u201d（编号 XH-202619）正是旨在探索如何将大语言模型与科学发现流程深度融合，"
        "构建能够自动生成可验证科学假设的 AI Scientist 系统。",
        indent=True
    )

    add_heading(doc, "1.2 研究目标", level=2)
    add_para(doc,
        "本系统的研究目标是构建一个面向动态随机地图路径规划场景的多智能体 AI Scientist 系统，实现以下核心能力：",
        indent=True
    )
    add_bullet(doc, "基于地图结构特征和算力约束，自动进行路径规划算法的适应性选型")
    add_bullet(doc, "综合历史实验数据和文献知识，生成可验证的科学假设")
    add_bullet(doc, "自动执行对比实验，验证假设的正确性")
    add_bullet(doc, "通过反思机制迭代优化假设质量，形成完整的科学发现闭环")
    add_bullet(doc, "输出标准化的10字段科学假设与研究计划报告")

    add_heading(doc, "1.3 技术边界声明", level=2)
    add_para(doc,
        "本系统明确以 Qwen 大模型作为多智能体架构的核心基础模型。DeepSeek 仅在开发初期未获取 Qwen API 时临时用于功能验证。"
        "算法的最终选择由可复现实验数据和评分函数决定，Qwen 智能体不直接选择算法，仅负责解释选型依据、抽取文献事实、生成科学假设、"
        "制定实验计划、撰写研究报告和充当反思角色。系统允许的算法集合严格限定为 A*、ACO、PSO、SA 和混合优化算法五种。",
        indent=True
    )

    # ================================================================
    add_heading(doc, "第2章 系统总体架构", level=1)

    add_heading(doc, "2.1 分层架构设计", level=2)
    add_para(doc,
        "系统采用分层架构设计，自上而下分为表现层、业务逻辑层、数据层和基础设施层四个层次：",
        indent=True
    )

    layers = [
        ("表现层（Presentation Layer）", "基于 Streamlit 构建的 Web GUI，提供地图参数输入、环境分析展示、智能体推理链可视化、研究报告呈现等交互功能。前端采用「左-中-右三栏 + 底部报告区」布局，支持 4 个 Tab 页面导航。"),
        ("业务逻辑层（Business Logic Layer）", "系统的核心层，包含 14 个智能化智能体的协同调度、5 种路径规划算法的执行引擎、10 维指标评分体系、假设生成与验证闭环等。以 OrchestratorAgent 为中央调度器，基于 ResearchState 统一数据模型串联全流程。"),
        ("数据层（Data Layer）", "包含 SQLite 实验数据库（3 张核心表）、JSON 知识库（算法画像、历史结果）、文献知识库（47 篇中文路径规划论文）、地图数据管理（支持 .map/.scen/.csv/.json/.npy 多格式）。"),
        ("基础设施层（Infrastructure Layer）", "包含 Qwen 大模型 API 调用（通过阿里云百炼平台）、FastAPI 后端服务（5-6 个 RESTful 端点）、日志系统、Docker 容器化部署配置。"),
    ]
    for name, desc in layers:
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Cm(0.74)
        run = p.add_run(f"{name}：")
        run.bold = True
        run.font.size = Pt(12)
        run.font.name = "宋体"
        run._element.rPr.rFonts.set(qn('w:eastAsia'), "宋体")
        run = p.add_run(desc)
        run.font.size = Pt(12)
        run.font.name = "宋体"
        run._element.rPr.rFonts.set(qn('w:eastAsia'), "宋体")
        p.paragraph_format.line_spacing = 1.5

    add_heading(doc, "2.2 核心数据流", level=2)
    add_para(doc,
        "系统的核心数据处理流程遵循以下路径：动态地图输入 → 环境特征提取与复杂度分级 → 文献知识检索 → 历史算法性能查询 → "
        "规则约束筛除 → 多维度加权评分 → 最优算法决策 → 人在回路校验 → 选型依据解释 → 科学假设生成（4段结构化）→ "
        "实验验证执行 → 反思评估 → 标准化报告输出。整个流程由 OrchestratorAgent 统一调度，"
        "各智能体通过 ResearchState 数据类传递中间结果，确保数据一致性和可追溯性。",
        indent=True
    )

    add_heading(doc, "2.3 项目目录结构", level=2)
    add_para(doc, "系统代码按功能模块组织，主要目录结构如下：", indent=True)

    dirs = [
        ("agents/", "19 个智能体实现文件，含 orchestrator_agent.py（总调度）、pipeline.py（闭环流水线）、research_state.py（统一状态）"),
        ("algorithms/", "5 种路径规划算法：astar.py、aco.py、pso.py、sa.py、hybrid.py"),
        ("map/", "4 个地图模块：地图生成器、地图解析器、地图分析器、连通性检查器"),
        ("evaluation/", "4 个评估模块：metrics.py、scoring.py、benchmark.py、experiment_runner.py"),
        ("llm/", "Qwen 大模型调用与 Prompt 模板管理：qwen_client.py、prompt_templates.py"),
        ("gui/", "Streamlit 前端：streamlit_app.py、visualization.py"),
        ("api/", "FastAPI 后端：server.py、schemas.py"),
        ("data/", "数据管理：data_manager.py、experiment_db.py、benchmark_loader.py"),
        ("knowledge_base/", "算法画像 JSON、历史结果 JSON、47 篇论文文献"),
        ("reports/", "报告生成器与已生成报告样本"),
        ("literature/", "文献模型与文献知识库 JSON"),
        ("tests/", "7 个单元测试与集成测试文件"),
        ("utils/", "日志配置模块"),
    ]
    for d, desc in dirs:
        add_bullet(doc, f"{d} — {desc}")

    # ================================================================
    add_heading(doc, "第3章 多智能体设计", level=1)

    add_heading(doc, "3.1 设计理念", level=2)
    add_para(doc,
        "本系统采用「中央调度 + 专业智能体协作」的多智能体架构。每个智能体专注于单一职责，通过 ResearchState 统一数据对象进行信息传递。"
        "OrchestratorAgent 作为中央调度器，负责按预定顺序调用各智能体，并在任一智能体失败时进行容错处理，保证流程的健壮性。",
        indent=True
    )

    add_heading(doc, "3.2 智能体清单与职责", level=2)
    add_para(doc, "系统共设计 14 个核心智能体，各司其职：", indent=True)

    agents = [
        ("1. Orchestrator Agent", "总控调度器", "实例化全部智能体，按流水线顺序调度执行；每个步骤用 try/except 包裹，失败不中断后续智能体"),
        ("2. Data Receiver Agent", "数据接收校验器", "校验输入字段完整性（obstacle_ratio、map_width、map_height、connectivity、compute_limit 等7个基础字段+3个扩展字段）"),
        ("3. Map Analysis Agent", "地图结构分析器", "提取地图结构特征：障碍物聚类数（cluster_count）、瓶颈数（bottleneck_count）、结构熵（entropy）、起点到终点距离（distance_to_target）"),
        ("4. Environment Agent", "环境复杂度分级器", "按障碍物占比进行三级分级：低（<20%）、中（20%-50%）、高（>50%），计算综合复杂度指数"),
        ("5. Literature Agent", "文献检索智能体", "通过 Semantic Scholar API 检索与当前场景/算法相关的学术文献，为假设生成提供文献支撑"),
        ("6. Fact Extraction Agent", "事实抽取智能体", "从检索到的文献中抽取与路径规划算法相关的科学事实和实验结论"),
        ("7. Knowledge Retrieval Agent", "知识检索智能体", "从历史实验数据库中根据场景等级检索各算法的历史性能记录，支持 JSON/向量相似度检索"),
        ("8. Rule Constraint Agent", "规则约束智能体", "实施4条惩罚规则：算力受限惩罚、低成功率惩罚、过度复杂惩罚、连通性差惩罚"),
        ("9. Algorithm Evaluation Agent", "算法评估智能体", "进行10维指标的逆向/正向归一化，应用场景化动态权重进行加权评分"),
        ("10. Parameter Agent", "参数推荐智能体", "根据场景特征和所选算法，推荐最优的超参数配置（如ACO信息素蒸发率、PSO惯性权重等）"),
        ("11. Decision Agent", "决策智能体", "从评分排序中选择综合得分最高的算法，执行白名单校验，触发人在回路条件判断"),
        ("12. Human-Loop Agent", "人在回路校验器", "7种触发条件（前两名差距<0.05、所有成功率<80%等）下请求人工干预"),
        ("13. Explanation Agent", "可解释性智能体", "调用 Qwen 生成选型依据的自然语言解释，输出标准化三行格式"),
        ("14. Hypothesis Agent", "假设生成智能体", "调用 Qwen V2 提示词生成4段结构化科学假设（hypothesis_text、experiment_plan、expected_results、boundary_conditions）"),
    ]

    table = doc.add_table(rows=1, cols=3)
    table.style = 'Table Grid'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = table.rows[0]
    for i, text in enumerate(["智能体名称", "角色", "核心职责"]):
        cell = hdr.cells[i]
        cell.text = ""
        p = cell.paragraphs[0]
        run = p.add_run(text)
        run.font.size = Pt(9)
        run.font.name = "宋体"
        run._element.rPr.rFonts.set(qn('w:eastAsia'), "宋体")
        run.bold = True
        set_cell_shading(cell, "2F5496")
        run.font.color.rgb = RGBColor(255, 255, 255)

    for name, role, duty in agents:
        add_table_row(table, [name, role, duty])

    doc.add_paragraph()

    add_heading(doc, "3.3 Orchestrator Agent 调度机制", level=2)
    add_para(doc,
        "OrchestratorAgent 在 __init__ 中实例化全部 14 个智能体，run() 方法接收环境输入字典，返回 ResearchState 对象。"
        "每个智能体步骤通过 _safe_step() 包装，执行前记录日志，成功时更新 ResearchState，失败时将异常追加到 "
        "state.metadata[\"errors\"] 并继续执行后续步骤。ParameterAgent 在流水线末尾独立调用，为最终决策推荐算法参数。"
        "整个流水线耗时约 3-10 秒（取决于是否启用 Qwen LLM 调用）。",
        indent=True
    )

    add_para(doc, "OrchestratorAgent 核心调度代码结构：", indent=True)
    code = read_file_snippet("agents/orchestrator_agent.py", 70, 148)
    add_code_block(doc, code)

    add_heading(doc, "3.4 ResearchState 统一数据模型", level=2)
    add_para(doc,
        "ResearchState 是贯穿 14 个智能体完整流水线的统一数据快照。它采用 Python dataclass 设计，包含 12 个核心字段"
        "（env_input、map_features、literature_facts、algorithm_records、scored_algorithms、decision、"
        "recommended_params、hypothesis、experiment_results、reflection、report、metadata），"
        "支持 to_dict() 和 from_dict() 序列化，以及 summary() 方法输出关键字段摘要。"
        "该设计确保了各智能体之间的数据契约清晰、状态可追溯、日志可审计。",
        indent=True
    )

    add_para(doc, "ResearchState 数据类核心定义：", indent=True)
    code = read_file_snippet("agents/research_state.py", 32, 79)
    add_code_block(doc, code)

    # ================================================================
    add_heading(doc, "第4章 路径规划算法实现", level=1)

    add_heading(doc, "4.1 算法体系概述", level=2)
    add_para(doc,
        "系统实现并集成了五种经典的路径规划算法，涵盖图搜索、群体智能、随机优化和混合策略四大范式。"
        "所有算法均在统一接口下运行，通过 BenchmarkRunner 进行公平比较。算法集合被严格限定在白名单 ALLOWED_ALGORITHMS 中。",
        indent=True
    )

    add_heading(doc, "4.2 A* 算法", level=2)
    add_para(doc,
        "A* 是启发式图搜索算法的代表，通过 f(n)=g(n)+h(n) 的代价函数引导搜索方向。系统实现中采用曼哈顿距离作为启发式函数，"
        "支持8邻域（含对角线）移动。A* 在低障碍物密度的静态栅格地图中表现最优，具有路径最短和完备性保证，"
        "但随障碍物密度增加，搜索空间和时间开销呈指数增长。实现约 150 行代码，核心为优先队列驱动的节点扩展循环。",
        indent=True
    )
    code = read_file_snippet("algorithms/astar.py", 1, 50)
    add_code_block(doc, code)

    add_heading(doc, "4.3 蚁群优化算法（ACO）", level=2)
    add_para(doc,
        "ACO 模拟蚂蚁觅食的信息素机制，通过正反馈逐步收敛到最优路径。系统实现中包含信息素初始化、概率选择、局部/全局信息素更新三个核心阶段。"
        "ACO 在高复杂度（>50%障碍物占比）和带动态障碍的场景中表现突出，具有较强的全局搜索能力和避障鲁棒性。实现约 80 行代码。",
        indent=True
    )
    code = read_file_snippet("algorithms/aco.py", 1, 40)
    add_code_block(doc, code)

    add_heading(doc, "4.4 粒子群优化算法（PSO）", level=2)
    add_para(doc,
        "PSO 通过模拟鸟群觅食行为进行连续空间优化，将路径规划问题转化为多维空间中的粒子搜索问题。"
        "每个粒子维护位置和速度向量，通过个体最优和全局最优引导搜索。PSO 在中等复杂度、算力受限场景下具有收敛速度快的优势。实现约 100 行代码。",
        indent=True
    )
    code = read_file_snippet("algorithms/pso.py", 1, 45)
    add_code_block(doc, code)

    add_heading(doc, "4.5 模拟退火算法（SA）", level=2)
    add_para(doc,
        "SA 模拟固体退火过程，通过温度逐步下降避免局部最优。以 Metropolis 准则接受概率较差解，在高温阶段广泛探索、低温阶段精细搜索。"
        "SA 适用于需要快速获得可行解、对路径最优性要求不极端的场景。实现约 80 行代码。",
        indent=True
    )

    add_heading(doc, "4.6 混合优化算法（Hybrid）", level=2)
    add_para(doc,
        "混合优化算法结合了 A* 的全局最优性保证和局部平滑优化策略。首先使用 A* 找到初始路径，"
        "然后应用路径平滑（去除冗余节点、直线化）降低路径长度。该算法在大规模稀疏障碍地图上成功率与耗时均优于单一算法。实现约 60 行代码。",
        indent=True
    )

    add_heading(doc, "4.7 算法对比总结", level=2)
    algo_table = doc.add_table(rows=1, cols=5)
    algo_table.style = 'Table Grid'
    algo_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(["算法", "类型", "最优场景", "代码行数", "核心优势"]):
        cell = algo_table.rows[0].cells[i]
        cell.text = ""
        p = cell.paragraphs[0]
        run = p.add_run(h)
        run.font.size = Pt(9)
        run.font.name = "宋体"
        run._element.rPr.rFonts.set(qn('w:eastAsia'), "宋体")
        run.bold = True
        set_cell_shading(cell, "2F5496")
        run.font.color.rgb = RGBColor(255, 255, 255)

    algo_data = [
        ("A*", "图搜索", "低复杂度（<20%障碍物）", "150", "路径最短、完备性保证"),
        ("ACO", "群体智能", "高复杂度（>50%障碍物）", "80", "全局搜索强、鲁棒性好"),
        ("PSO", "群体智能", "中复杂度、算力受限", "100", "收敛快、参数少"),
        ("SA", "随机优化", "快速可行解需求", "80", "实现简单、跳出局部最优"),
        ("Hybrid", "组合策略", "大规模稀疏地图", "60", "兼顾最优性与平滑性"),
    ]
    for row_data in algo_data:
        add_table_row(algo_table, row_data)
    doc.add_paragraph()

    # ================================================================
    add_heading(doc, "第5章 环境建模与地图系统", level=1)

    add_heading(doc, "5.1 地图模块架构", level=2)
    add_para(doc,
        "地图模块负责地图的生成、解析、分析和连通性验证，是整个决策系统的输入基础。模块包含四个核心组件：",
        indent=True
    )
    add_bullet(doc, "map_generator.py：生成指定尺寸和障碍物占比的随机栅格地图，支持起点和终点设置")
    add_bullet(doc, "map_parser.py：解析多格式地图文件（.map、.scen、.csv、.json、.npy），支持 Moving AI 2D Benchmark 标准格式")
    add_bullet(doc, "map_analyzer.py：提取地图结构特征（障碍物聚类数、瓶颈数、结构熵、起点到终点距离），为算法选型提供多维环境信息")
    add_bullet(doc, "connectivity_checker.py：验证起点到终点的连通性，不达标时自动重试（最多5次）")

    add_heading(doc, "5.2 环境复杂度三级分级", level=2)
    add_para(doc,
        "系统根据障碍物占比（obstacle_ratio）进行三级复杂度分级，该阈值可在 config.py 中配置：",
        indent=True
    )

    level_table = doc.add_table(rows=1, cols=4)
    level_table.style = 'Table Grid'
    level_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(["等级", "障碍物占比", "权重策略", "推荐算法倾向"]):
        cell = level_table.rows[0].cells[i]
        cell.text = ""
        p = cell.paragraphs[0]
        run = p.add_run(h)
        run.font.size = Pt(9)
        run.font.name = "宋体"
        run._element.rPr.rFonts.set(qn('w:eastAsia'), "宋体")
        run.bold = True
        set_cell_shading(cell, "2F5496")
        run.font.color.rgb = RGBColor(255, 255, 255)

    level_data = [
        ("低复杂度", "< 20%", "偏重耗时指标（权重 0.25）", "A*"),
        ("中复杂度", "20% - 50%", "各指标均衡", "PSO / Hybrid"),
        ("高复杂度", "> 50%", "偏重成功率（权重 0.30）和鲁棒性（0.15）", "ACO"),
    ]
    for row_data in level_data:
        add_table_row(level_table, row_data)
    doc.add_paragraph()

    add_para(doc,
        "综合复杂度指数 C 的计算公式为：C = 0.45 × O + 0.25 × (1-K) + 0.20 × R + 0.10 × D，"
        "其中 O 为障碍物占比归一化值，K 为连通性，R 为拓扑随机性，D 为节点度分布方差。"
        "该公式综合考虑了障碍物密度、通道通过性、地图随机性和结构复杂度四个维度。",
        indent=True
    )

    add_heading(doc, "5.3 动态地图支持", level=2)
    add_para(doc,
        "优化版系统增加了动态障碍物支持（dynamic_obstacle.py）和动态场景重规划（replanning_agent.py）。"
        "重规划采用三级响应策略：当环境变化小于 10% 时进行局部路径修正，在 10%-30% 之间保持当前算法重新搜索，超过 30% 则重新触发全流程算法选型。"
        "此外，系统扩展支持三维体素地图（map_3d.py）、拓扑地图（topology_map.py）和连续空间地图（continuous_map.py），满足不同应用场景需求。",
        indent=True
    )

    # ================================================================
    add_heading(doc, "第6章 评估与评分体系", level=1)

    add_heading(doc, "6.1 评估指标体系", level=2)
    add_para(doc,
        "系统采用 10 维评估指标体系，从多个角度对算法性能进行全面评估：",
        indent=True
    )

    metrics_table = doc.add_table(rows=1, cols=3)
    metrics_table.style = 'Table Grid'
    metrics_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(["指标", "归一化方向", "说明"]):
        cell = metrics_table.rows[0].cells[i]
        cell.text = ""
        p = cell.paragraphs[0]
        run = p.add_run(h)
        run.font.size = Pt(9)
        run.font.name = "宋体"
        run._element.rPr.rFonts.set(qn('w:eastAsia'), "宋体")
        run.bold = True
        set_cell_shading(cell, "2F5496")
        run.font.color.rgb = RGBColor(255, 255, 255)

    metric_data = [
        ("time", "逆向（越小越好）", "平均运行耗时"),
        ("path_length", "逆向（越小越好）", "平均路径长度"),
        ("success_rate", "正向（越大越好）", "规划成功率"),
        ("stability", "正向（越大越好）", "多次运行结果稳定性"),
        ("smoothness", "逆向（越小越好）", "路径平滑度（曲率变化）"),
        ("safety_score", "正向（越大越好）", "安全分数（与障碍物距离）"),
        ("expanded_nodes", "逆向（越小越好）", "搜索过程展开节点数"),
        ("compute_cost", "逆向（越小越好）", "计算资源消耗估算"),
        ("robustness", "正向（越大越好）", "对噪声/微扰动的鲁棒性"),
        ("reproducibility", "正向（越大越好）", "多次实验可复现性（Phase 2新增）"),
    ]
    for row_data in metric_data:
        add_table_row(metrics_table, row_data)
    doc.add_paragraph()

    add_heading(doc, "6.2 加权评分机制", level=2)
    add_para(doc,
        "评分函数采用逆向/正向归一化后加权求和的方式。逆向归一化公式为 score = 1 - (Ti - Tmin) / (Tmax - Tmin)，"
        "正向归一化公式为 score = (Si - Smin) / (Smax - Smin)。综合评分 = Σ(权重_i × 维度得分_i) - 惩罚项。",
        indent=True
    )
    add_para(doc,
        "权重根据场景等级动态调整，通过 WEIGHTS 字典在 config.py 中配置。低复杂度场景偏重耗时（权重 0.25），"
        "中复杂度场景各指标均衡，高复杂度场景偏重成功率（权重 0.30）和鲁棒性（权重 0.15）。"
        "算力受限时额外应用 COMPUTE_LIMIT_WEIGHT_ADJUST 进行权重修正（如耗时权重增加 +0.15）。",
        indent=True
    )

    add_heading(doc, "6.3 规则惩罚机制", level=2)
    add_para(doc, "系统实施四条规则惩罚，确保选型结果在特定约束下的合理性和可靠性：", indent=True)
    add_bullet(doc, "算力受限高耗时惩罚：当 compute_limit='low' 且某算法耗时超过阈值1.5倍时，惩罚 -0.15")
    add_bullet(doc, "低成功率惩罚：当某算法成功率低于 80% 时，惩罚 -0.20")
    add_bullet(doc, "过度复杂惩罚：在低复杂度场景使用复杂算法（如ACO），惩罚 -0.10（避免杀鸡用牛刀）")
    add_bullet(doc, "连通性差惩罚：当连通性<0.4 且某算法成功率低于 85% 时，惩罚 -0.15")

    add_heading(doc, "6.4 人在回路机制", level=2)
    add_para(doc,
        "HumanLoopAgent 在 7 种条件下触发人工校验：前两名得分差距小于 0.05、所有算法成功率低于 80%、"
        "所选算法与预期算法不一致、选型结果置信度低于阈值、排名前二算法类型差异过大、"
        "地图特征异常（如障碍物聚类数>10、瓶颈数>5）、首次运行新地图类型。"
        "触发后，GUI 界面会高亮显示候选算法并提供参数调整接口，等待用户确认后继续流程。",
        indent=True
    )

    # ================================================================
    add_heading(doc, "第7章 大模型集成", level=1)

    add_heading(doc, "7.1 Qwen 大模型调用架构", level=2)
    add_para(doc,
        "系统通过 qwen_client.py 封装对阿里云通义千问（Qwen）大模型的调用。采用 OpenAI 兼容的 API 接口格式，"
        "支持 Qwen-Plus/Qwen-Max/Qwen-Turbo 等模型的切换。客户端通过 DashScope（百炼平台）的 compatible-mode 端点进行通信。"
        "使用 python-dotenv 管理 API Key，避免密钥泄露。系统同时保留了 DeepSeek 和 OpenAI 的备用接口，"
        "通过 LLM_PROVIDER 环境变量进行切换。",
        indent=True
    )

    add_heading(doc, "7.2 Prompt 工程设计", level=2)
    add_para(doc,
        "系统的 Prompt 模板分为 V1 和 V2 两个版本。V1 用于 Phase 0-4 的基础假设生成，输出为自由文本。"
        "V2 升级版用于 Phase 5+ 的结构化假设生成，要求 Qwen 返回 JSON 格式的 4 段结构化输出，"
        "包含 hypothesis_text（假设文本）、experiment_plan（实验计划，含地图参数/算法列表/运行次数/评估指标）、"
        "expected_results（预期结果）和 boundary_conditions（边界条件）。"
        "通过正则表达式提取 JSON 段并用 json.loads 解析，解析失败时自动回退到离线规则生成器，保证系统可用性。",
        indent=True
    )

    add_heading(doc, "7.3 LLM 在系统中的职能分工", level=2)
    add_para(doc,
        "Qwen 在系统中承担以下六类核心职责，但不直接参与算法选择（算法选择由数据和评分函数决定）：",
        indent=True
    )
    add_bullet(doc, "解释选型依据：根据10维评分结果，生成自然语言解释，说明为何选中某算法")
    add_bullet(doc, "文献事实抽取：从学术文献中提取与路径规划算法相关的科学事实和实验结论")
    add_bullet(doc, "科学假设生成：基于场景特征、历史数据和文献事实，生成可验证的科学假设")
    add_bullet(doc, "实验计划制定：自动生成实验方案的各项参数（地图数量、算法列表、运行次数等）")
    add_bullet(doc, "研究报告撰写：按照10字段模板撰写标准化的科学报告")
    add_bullet(doc, "反思与批判：作为 ReflectionAgent 的核心推理引擎，检查假设的逻辑一致性和实验可靠性")

    add_para(doc,
        "系统支持 use_qwen=False 模式，此时所有 LLM 相关功能回退到离线规则生成器，"
        "基于模板和实验数据生成假设和解释，确保在无网络或 API 不可用的情况下系统仍可正常运行。",
        indent=True
    )

    # ================================================================
    add_heading(doc, "第8章 假设-验证-反思闭环", level=1)

    add_heading(doc, "8.1 闭环流水线设计", level=2)
    add_para(doc,
        "ScientificDiscoveryPipeline 整合了 OrchestratorAgent → HypothesisAgent → ExperimentAgent → ReflectionAgent，"
        "形成完整的「假设生成 → 实验验证 → 反思评估」闭环。核心实现位于 agents/pipeline.py，支持多轮迭代（默认最多 3 轮），"
        "当 ReflectionAgent 的 confidence_score ≥ 0.7 时提前收敛退出。",
        indent=True
    )

    add_para(doc, "闭环流水线核心代码：", indent=True)
    code = read_file_snippet("agents/pipeline.py", 44, 119)
    add_code_block(doc, code)

    add_heading(doc, "8.2 HypothesisAgent 结构化假设生成", level=2)
    add_para(doc,
        "HypothesisAgent 在 Phase 5 进行了重大升级，从 V1 自由文本输出升级为 V2 的 4 段结构化 JSON 输出。"
        "调用 Qwen 时使用 HYPOTHESIS_SYSTEM_PROMPT_V2 和 HYPOTHESIS_USER_TEMPLATE_V2 提示词模板，"
        "生成的 JSON 经正则提取和 json.loads 解析后，规整为四段结构化字段写入 state.hypothesis。"
        "离线模式下，_default_hypothesis_struct() 基于 ResearchState 中的决策和地图特征自动生成假设。",
        indent=True
    )

    add_para(doc, "四段结构化假设包含：", indent=True)
    add_bullet(doc, "hypothesis_text：一句话科学假设（格式：「在{场景等级}条件下，{算法}相比{次优算法}在{指标}上具有显著优势」）")
    add_bullet(doc, "experiment_plan：实验计划（maps、algorithms、runs_per_algorithm、metrics 子字段）")
    add_bullet(doc, "expected_results：预期结果（best_algorithm、success_rate_threshold、time_budget_seconds）")
    add_bullet(doc, "boundary_conditions：边界条件列表（地图尺寸、障碍物占比上限、连通性要求、算力限制）")

    add_heading(doc, "8.3 ReflectionAgent 反思评估", level=2)
    add_para(doc,
        "ReflectionAgent 负责对假设和实验结果进行7项反思检查：假设逻辑一致性、实验设计是否充分、"
        "结果是否支持假设、是否存在混淆因素、结论是否足够泛化、是否有数据泄露风险、"
        "与其他研究的关联性。反思结果包含 issues（问题列表）、suggestions（改进建议）和 "
        "confidence_score（置信度评分），用于指导下轮迭代的假设修正方向。",
        indent=True
    )

    add_heading(doc, "8.4 ExperimentAgent 自动实验验证", level=2)
    add_para(doc,
        "ExperimentAgent 基于假设中的实验计划自动运行验证实验。默认在 50 张随机地图上对 5 种算法各运行 5 次，"
        "使用 BenchmarkRunner 统一执行，将结果写入 ExperimentDB（SQLite）。支持批量实验矩阵"
        "（3 复杂度 × 3 规模 × 3 算力 = 27 组配置），实验结果自动参与后续迭代的算法选型决策。",
        indent=True
    )

    # ================================================================
    add_heading(doc, "第9章 GUI 界面设计", level=1)

    add_heading(doc, "9.1 界面架构", level=2)
    add_para(doc,
        "系统前端基于 Streamlit 构建，采用「左-中-右三栏 + 底部报告区」的宽屏布局（layout='wide'），"
        "顶部设置 4 个 Tab 导航页面：地图参数、环境分析、智能体推理、研究报告。"
        "前端代码集中在 gui/streamlit_app.py（约 350 行）和 gui/visualization.py（约 200 行）两个文件中。",
        indent=True
    )

    add_heading(doc, "9.2 Tab 页面功能详解", level=2)

    tabs = [
        ("Tab 1 — 地图参数", "左侧面板提供地图参数设置（障碍物占比滑块、地图尺寸、算力限制单选按钮、高级参数折叠区），中部实时渲染地图网格预览（含障碍物、起点、终点标识），右侧显示参数摘要。支持连通性不达标时自动重试（最多 5 次）。"),
        ("Tab 2 — 环境分析", "上部展示场景分析卡片（复杂度等级、综合复杂度指数、决策摘要），下部通过 Plotly 绘制算法性能雷达图（4-10 维度可切换）、柱状图对比和详细数据表。优化版增加了 10 指标雷达图、误差线与置信区间、Pareto 前沿高亮和分面柱状图。"),
        ("Tab 3 — 智能体推理", "左侧展示决策结果卡片（场景等级、推荐算法、综合得分），右侧以 Expandable 组件展示 7-12 个智能体的推理链（每个智能体的输入、处理逻辑、输出），下方提供人在回路交互区（优化优先级选择、自定义权重滑块）和参数推荐区。"),
        ("Tab 4 — 研究报告", "全宽展示 10 字段科学假设与研究计划（Markdown 渲染），包括待研究问题、解决思路、必要技术手段、数据集、论文标题、摘要、方法论、实验设计、实验结果、参考论文。底部提供 Markdown 复制和 PDF 下载按钮。"),
    ]
    for name, desc in tabs:
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Cm(0.74)
        run = p.add_run(f"{name}：")
        run.bold = True
        run.font.size = Pt(12)
        run.font.name = "宋体"
        run._element.rPr.rFonts.set(qn('w:eastAsia'), "宋体")
        run = p.add_run(desc)
        run.font.size = Pt(12)
        run.font.name = "宋体"
        run._element.rPr.rFonts.set(qn('w:eastAsia'), "宋体")
        p.paragraph_format.line_spacing = 1.5

    add_heading(doc, "9.3 Session State 管理", level=2)
    add_para(doc,
        "系统通过 Streamlit 的 session_state 管理 9 个关键对象（decision、benchmark_results、grid、"
        "start、target、env_input、features、params、hypothesis），确保页面切换时状态不丢失。"
        "核心执行逻辑抽取为 execute_decision_pipeline() 函数，供各 Tab 复用，避免重复计算。",
        indent=True
    )

    add_heading(doc, "9.4 可视化增强", level=2)
    add_para(doc,
        "优化版 GUI 全面升级为 Plotly 可视化，支持搜索过程动画（A*/ACO/PSO 的帧动画，帧率 ≥ 10fps）、"
        "多路径同屏叠加对比、3D 体素地图渲染（Three.js）、多智能体辩论可视化、敏感度分析报告"
        "（对每个指标 ±0.05 观察推荐算法变化）、权重动态调整实时重算等功能。"
        "PDF 导出通过 pdfkit 实现（中文需配置字体），LaTeX 论文导出在 Phase 3 中规划。",
        indent=True
    )

    # ================================================================
    add_heading(doc, "第10章 知识库与文献系统", level=1)

    add_heading(doc, "10.1 算法知识库", level=2)
    add_para(doc,
        "知识库以 JSON 文件为核心存储格式，包含 algorithm_profile.json（5 种算法的标准化画像，"
        "含适用场景、时间复杂度、优缺点、典型参数范围）和 historical_results.json（15 条模拟性能数据，"
        "覆盖 5 算法 × 3 复杂度等级的历史实验记录）。Phase 2 升级中将这些数据迁移至 SQLite 数据库，"
        "通过 ExperimentDB 类提供结构化查询接口。",
        indent=True
    )

    add_heading(doc, "10.2 文献知识库", level=2)
    add_para(doc,
        "系统集成了 47 篇中文路径规划领域学术论文，覆盖无人机路径规划、移动机器人导航、车辆避障、"
        "多机器人协同、物流配送等应用领域。文献以 Markdown 格式存储于 knowledge_base/papers/ 目录，"
        "通过 LiteratureAgent 和 RAGAgent 实现智能检索和知识增强生成。",
        indent=True
    )

    add_heading(doc, "10.3 LiteratureAgent 文献检索", level=2)
    add_para(doc,
        "LiteratureAgent 支持两种检索模式：本地文献知识库检索（基于关键词匹配和向量相似度）和联网检索"
        "（通过 Semantic Scholar API 实时查询）。检索结果经 FactExtractionAgent 提取科学事实后，"
        "通过 RAGAgent 与当前场景的实验数据融合，为 HypothesisAgent 的假设生成提供上下文增强。",
        indent=True
    )

    add_heading(doc, "10.4 CitationAgent 引用管理", level=2)
    add_para(doc,
        "CitationAgent 负责对文献引用进行核验和格式化。核验规则包括：缺少标题或作者 → 标记为 invalid；"
        "同时缺少 DOI 和 URL → 标记为 suspicious；DOI 无法解析 → 标记为 invalid。"
        "核验通过的引用按照标准格式（作者 (年份). *标题*. DOI: xxx）输出到报告参考论文字段。",
        indent=True
    )

    # ================================================================
    add_heading(doc, "第11章 实验数据库与工程化", level=1)

    add_heading(doc, "11.1 实验数据库设计", level=2)
    add_para(doc,
        "SQLite 实验数据库（experiment_db.py）包含三张核心表：experiments（实验记录，含 map_id、"
        "algorithm、scene_level、10 维指标值、timestamp）、maps（地图元数据，含 obstacle_ratio、"
        "map_width、map_height、map_features JSON）、和 benchmarks（基准测试汇总，含 avg_success_rate、"
        "avg_time、rank 等统计值）。ExperimentDB 类提供增删改查的 ORM 风格接口。",
        indent=True
    )

    add_heading(doc, "11.2 BenchmarkRunner 基准测试", level=2)
    add_para(doc,
        "BenchmarkRunner（evaluation/benchmark.py）是自动实验对比的核心执行引擎。它接收实验配置"
        "（地图列表、算法列表、每算法运行次数、评估指标），依次对每张地图 × 每个算法运行实验，"
        "调用 metrics.py 收集 10 维指标，最终输出排序结果和统计摘要。支持批量实验矩阵运行（experiment_runner.py），"
        "实验结果通过 data_card.py 生成标准化的 Data Card 文档。",
        indent=True
    )

    add_heading(doc, "11.3 FastAPI 后端服务", level=2)
    add_para(doc,
        "系统提供 FastAPI 驱动的 RESTful API 后端（api/server.py），包含以下端点：POST /decide（接收环境参数，"
        "返回算法选型决策）、POST /experiment（提交实验请求，异步执行并返回任务 ID）、GET /experiment/{id}（查询实验结果）、"
        "GET /algorithms（返回可用算法列表与画像）、POST /report（根据 ResearchState 生成标准化报告）、"
        "GET /health（健康检查）。所有端点通过 Pydantic schema（api/schemas.py）进行请求/响应验证。",
        indent=True
    )

    add_heading(doc, "11.4 日志与部署", level=2)
    add_para(doc,
        "系统通过 utils/logging_config.py 配置全局日志系统，支持控制台和文件双通道输出，日志级别可通过环境变量 LOG_LEVEL 配置。"
        "部署方面提供 Dockerfile、docker-compose.yml 和 .env.example，支持一键容器化部署。"
        "数据库升级路径为 JSON → SQLite → PostgreSQL → PostgreSQL + 向量数据库（pgvector），以适应日益增长的数据量和检索复杂度。",
        indent=True
    )

    # ================================================================
    add_heading(doc, "第12章 升级路线与优化方向", level=1)

    add_heading(doc, "12.1 8 阶段渐进式升级路线", level=2)
    add_para(doc,
        "系统遵循「基础版 MVP → 优化版 → 完整 AI Scientist 系统」的渐进式升级路线，分为 8 个 Phase 阶段：",
        indent=True
    )

    phases = [
        ("Phase 0 — 合规体检", "统一项目命名、明确 Qwen/DeepSeek 角色分工、创建 TECHNICAL_BOUNDARY.md、强化 Data Agent 校验"),
        ("Phase 1 — 数据输入升级", "接入 Moving AI 2D Benchmark、支持多格式地图解析（.map/.scen/.csv/.json/.npy）、Data Card 生成"),
        ("Phase 2 — 实验数据库", "SQLite 数据库（3 张表）、指标体系从 4 维扩展到 10 维、批量实验矩阵运行器"),
        ("Phase 3 — 文献知识库", "5 类文献收集、LiteratureAgent / FactExtractionAgent / CitationAgent / RAGAgent 四件套"),
        ("Phase 4 — 多智能体协同", "ResearchState 统一数据模型、12 智能体 Orchestrator 升级、7 种 HumanLoop 触发条件"),
        ("Phase 5 — 假设验证闭环", "HypothesisAgent 4 段结构化输出、ExperimentAgent 自动验证、ReflectionAgent 反思评估、闭环流水线"),
        ("Phase 6 — GUI 升级", "4 Tab 页面（数据输入/环境分析/推理链/研究报告）、Plotly 可视化、Markdown/PDF 导出"),
        ("Phase 7 — 后端工程化", "日志系统、FastAPI 后端（5-6 个端点）、环境变量配置、Docker 容器化"),
    ]
    for name, desc in phases:
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Cm(0.74)
        run = p.add_run(f"{name}：")
        run.bold = True
        run.font.size = Pt(12)
        run.font.name = "宋体"
        run._element.rPr.rFonts.set(qn('w:eastAsia'), "宋体")
        run = p.add_run(desc)
        run.font.size = Pt(12)
        run.font.name = "宋体"
        run._element.rPr.rFonts.set(qn('w:eastAsia'), "宋体")
        p.paragraph_format.line_spacing = 1.5

    add_heading(doc, "12.2 九大优化方向", level=2)
    optimizations = [
        ("参数自适应", "由 ParameterAgent 根据场景特征自动推荐最优算法超参数，如 ACO 的信息素蒸发率、PSO 的惯性权重等"),
        ("多维度环境特征", "从单一障碍物占比升级为聚类数、瓶颈数、熵值、通道宽度、死路数量等多维特征"),
        ("动态场景重规划", "支持动态障碍物和三级响应策略（局部修正/重新搜索/全流程选型）"),
        ("性能预测模型", "基于 RandomForest / XGBoost / Bayesian Optimization 的算法性能预测"),
        ("多目标优化（4→10 指标）", "新增 smoothness、safety_score、expanded_nodes、compute_cost、robustness、reproducibility"),
        ("假设验证闭环", "HypothesisAgent → ExperimentAgent → ReflectionAgent 三体闭环迭代"),
        ("多地图类型", "支持 3D 体素地图、拓扑地图和连续空间地图"),
        ("多机器人协同", "多机器人任务分配与协同路径规划"),
        ("增强可解释性", "六阶段推理链可视化、敏感度分析、审稿人模拟评估"),
    ]
    for name, desc in optimizations:
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Cm(0.74)
        run = p.add_run(f"{name}：")
        run.bold = True
        run.font.size = Pt(12)
        run.font.name = "宋体"
        run._element.rPr.rFonts.set(qn('w:eastAsia'), "宋体")
        run = p.add_run(desc)
        run.font.size = Pt(12)
        run.font.name = "宋体"
        run._element.rPr.rFonts.set(qn('w:eastAsia'), "宋体")
        p.paragraph_format.line_spacing = 1.5

    # ================================================================
    add_heading(doc, "第13章 总结与展望", level=1)

    add_heading(doc, "13.1 系统亮点", level=2)
    add_bullet(doc, "完整的多智能体 AI Scientist 范式：从数据输入到科学假设生成的端到端闭环")
    add_bullet(doc, "数据驱动的算法选型：算法选择由可复现实验数据和评分函数决定，Qwen 负责解释而非直接决策")
    add_bullet(doc, "渐进式架构设计：支持从基础版 MVP（35 文件、1930 行）到完整版（50+ 文件、3500+ 行）的平滑升级")
    add_bullet(doc, "10 维精细评估体系：覆盖时效、质量、安全、效率、鲁棒性的全方位算法评价")
    add_bullet(doc, "健壮的容错机制：每个智能体步骤失败不中断全流程，LLM 不可用时自动降级为规则生成")
    add_bullet(doc, "标准化输出：10 字段科学假设与研究计划报告，满足学术规范")

    add_heading(doc, "13.2 当前局限", level=2)
    add_bullet(doc, "实验数据依赖模拟环境：目前使用合成随机地图，缺乏真实物理世界数据验证")
    add_bullet(doc, "LLM 调用延迟：Qwen API 网络调用增加流程延迟（2-5 秒），离线模式丧失部分智能化能力")
    add_bullet(doc, "搜索空间局限：5 种基础算法可能无法覆盖所有路径规划场景")
    add_bullet(doc, "多机器人协同为规划阶段：尚未在实际多机器人系统上验证")

    add_heading(doc, "13.3 未来方向", level=2)
    add_bullet(doc, "接入真实机器人平台（ROS/ROS2），在物理环境中验证算法选型效果")
    add_bullet(doc, "引入更多路径规划算法（RRT*、D* Lite、Theta* 等）扩展算法库")
    add_bullet(doc, "接入持续进化的文献流（arXiv API），实现知识的自动更新")
    add_bullet(doc, "开发多轮人机对话接口，实现更深度的科学家-AI 协作")
    add_bullet(doc, "集成性能预测模型（Bayesian Optimization + AutoML），实现超参数自动调优")
    add_bullet(doc, "扩展至多机器人协同路径规划，解决多智能体在共享环境中的冲突消解")

    # ================================================================
    add_heading(doc, "参考文献", level=1)

    references = [
        "[1] 张广林, 胡小梅, 柴剑飞, 等. 路径规划算法及其应用综述[J]. 现代制造工程, 2011.",
        "[2] 朱大奇, 颜明重. 移动机器人路径规划技术综述[J]. 控制与决策, 2010, 25(7): 961-967.",
        "[3] 周子剑. 考虑力学约束的自适应RRT路径规划算法及其在机械臂中的应用[D]. 2024.",
        "[4] 罗子灿. 基于改进粒子群算法的移动机器人路径规划研究[D]. 2025.",
        "[5] 于泽. 基于强化学习的移动机器人路径规划方法研究[D]. 2025.",
        "[6] 宁致远. 基于改进蚁群算法的无人机末端配送路径规划研究[D]. 2025.",
        "[7] 朱梓轩. 基于模拟退火-改进蚁群算法的无人车路径规划[D]. 2025.",
        "[8] 李明妍. 一种高效的无人机避障路径规划混合算法策略[D]. 2025.",
        "[9] 陈刚. 复杂动态环境的移动机器人自适应MPPI路径规划[D]. 2025.",
        "[10] 王嘉琦. 基于深度强化学习的机器人路径规划算法研究[D]. 2025.",
        "[11] 梁迪. 复杂桥梁巡检中无人机安全自适应轨迹规划[D]. 2025.",
        "[12] 潘俊文. 智能车辆避障路径规划与轨迹跟踪控制方法研究[D]. 2025.",
        "[13] 沈正邦. 洪涝灾害下基于RL-ALNS算法的无人机-车辆协同配送路径优化研究[D]. 2025.",
        "[14] 任坤. 基于迁移强化学习的自主移动机器人路径规划设计[D]. 2025.",
        "[15] 阿里巴巴云计算有限公司. 基于国产开源大模型的AI科学家研发与应用比赛方案[R]. 2025.",
    ]
    for ref in references:
        add_para(doc, ref, font_size=11)

    # ================================================================
    output_path = os.path.abspath(str(OUTPUT_FILE))
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc.save(output_path)
    print(f"技术报告已生成：{output_path}")
    return output_path


if __name__ == "__main__":
    generate_report()
