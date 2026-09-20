from flask import Flask, render_template, request, redirect, url_for, flash
from database import (
    init_db,
    insert_application,
    get_applications,
    get_applications_count,
    update_application,
    delete_application,
)

app = Flask(__name__)
app.secret_key = "xjy-fairy-report-2026"

PAGE_SIZE = 20

# ─────────────────────────────────────────
# 首页数据
# ─────────────────────────────────────────
ADVANTAGES = [
    ("🏗️", "行业规范深度嵌入",
     "14 种报告模板严格对标《决策评价_2024》，21 类工程专业（GBZ/T 40846-2021）、50 类鼓励产业（产业结构调整指导目录 2024）——每个章节标题与字数预算均源自国家规范，非通用套壳。"),
    ("🔍", "三源知识融合",
     "编写每章时同步融合：①项目资料库（用户上传文件向量检索）、②行业通用知识库（预置技术标准与规范）、③实时互联网搜索（最新政策数据与行业动态），引用均标注可追溯来源。"),
    ("🔒", "全文逻辑自洽",
     "跨章方案锁定：比选结论一旦确定，后续章节禁止推翻；过期章节检测：前序修改后，后续章节自动标记「上下文过期」并级联提醒——从第一页到最后一页逻辑一致。"),
    ("⚡", "效率指数级跃升",
     "传统流程需数周到数月；新纪元数智 五步向导：导入资料 → 确认大纲 → 逐章 AI 流式生成 → 人机审阅 → 一键导出 Word，数小时交付初稿，效率提升 10 倍以上。"),
]

FEATURES = [
    ("🔍", "三源知识融合",
     "编写时同步检索三类信息：项目资料库（用户上传文件，标注【源:文件名】）、行业通用知识库（技术标准与规范，标注[Z]）、实时互联网搜索（最新政策与行业数据，标注【网:标题】）。"),
    ("🔒", "跨章方案锁定",
     "工程报告独有逻辑约束：场址比选、技术路线比选等一旦在前序章节选定方案，后续所有章节禁止推翻或引入新备选——确保整本报告前后逻辑完全一致。"),
    ("📐", "精细化篇幅控制",
     "全篇上限（2万~5.5万字）→ 每章预算（核心章8000字/综述章3000字）→ 自动校正：生成后实测字数，偏少充实、偏多压缩，最多 2 轮，变化 <5% 自动刹车退出。"),
    ("🧠", "智能写作顺序",
     "AI 分析大纲章节依赖关系，编排最优写作顺序：现状分析先于方案设计，概述与结论最后写——确保 AI 写概述时手里已有完整前文数据，引用准确不编造。"),
    ("🔄", "过期章节检测",
     "前序章节被修改或新资料导入后，后续已写章节自动标记「上下文过期」，提醒重写；重写时 AI 自动读入更新后的前文全文——变更影响级联传导，不遗漏。"),
    ("📎", "结构化引用管理",
     "写作阶段：每章末尾自包含引用区块（三种来源分类标注）；导出阶段：全文统一编号[1][2][3]，编造标签自动清洗，独立输出分类参考资料清单文件。"),
]

STEPS = [
    ("项目初始化", "输入报告名称，AI 自动匹配鼓励类产业、生成主题关键词。21 类工程专业 · 50 类鼓励类产业 · AI 智能推荐。"),
    ("资料导入", "上传 Word/Excel/CSV 等项目资料，自动解析、智能切片、向量入库。支持 5 种格式 · 800字智能切片 · 100字重叠保上下文。"),
    ("确定大纲", "14 种预定义章节骨架直接使用，AI 建议最优写作顺序，核心章节先写，概述结论最后写。"),
    ("编写 & 审阅", "逐章流式生成，三阶段交互：生成提示词 → 确认/编辑 → AI 编写。实时审阅，随时修改，自动字数校验。"),
    ("合并导出", "一键导出排版规范的 Word 文档，自动生成目录与三级参考资料清单。5 级标题层级 · 原生表格 · LaTeX 公式。"),
]

SCENARIOS = [
    ("可行性研究报告",
     "省级能源基础设施项目",
     "编制团队 2 人，传统流程需 3～4 周反复修改，版本管理混乱，跨章数据不一致。",
     "使用 新纪元数智 2 天完成全文初稿，三源引用自动标注，跨章方案锁定确保前后一致，工程师审阅后顺利提交评审。",
     "交付周期缩短约 80%"),
    ("资金申请报告",
     "县级公共基础设施项目",
     "政策依据检索耗时长，申报规范更新频繁，人工对照规范效率低，易遗漏关键章节。",
     "系统自动融合最新政策与行业知识库，章节骨架严格对标申报规范，一次性完成全文结构，大幅减少返工次数。",
     "规范符合率显著提升"),
    ("产业园区发展规划",
     "地方政府产业园区项目",
     "需覆盖宏观政策、产业现状、竞争格局多维度内容，人工搜集整理周期长，大体量报告篇幅难以把控。",
     "实时互联网搜索融合行业数据，智能写作顺序确保现状分析先于战略规划，篇幅自动校验控制全文字数在预算范围内。",
     "信息整合效率提升 5 倍以上"),
]

COMPARISONS = [
    ("行业规范内置",
     "无，依赖提示词临时补充",
     "严格对标《决策评价_2024》<br>14 种报告预定义骨架与字数预算"),
    ("知识来源可追溯",
     "训练数据，无法追溯出处",
     "三源融合，每处引用标注来源<br>（文件名 / 技术标准 / 网页标题）"),
    ("跨章逻辑一致性",
     "自行管理，章节间易矛盾",
     "跨章方案锁定 + 过期章节检测<br>前后逻辑强制一致"),
    ("篇幅管控",
     "手动控制，字数难保证",
     "自动字数校验 + 最多 2 轮修正<br>全篇 2 万～5.5 万字精准达标"),
    ("数据安全",
     "数据上传至第三方服务器",
     "支持私有化本地部署<br>数据不出内网，适配涉密项目"),
    ("行业适配深度",
     "通用场景，非行业专用",
     "21 类工程专业深度适配<br>50 类鼓励类产业自动匹配"),
]

FAQS = [
    ("生成的报告能直接提交评审吗？",
     "新纪元数智 定位是 AI 辅助编制工具，生成内容为专业初稿，需由具备资质的工程师审阅、核实数据并修改完善后，方可用于正式评审提交。我们不承诺评审通过结果，成果质量最终取决于工程师的专业判断。"),
    ("项目资料上传后数据是否安全？",
     "我们支持私有化本地部署，数据完全不出内网，适配涉密项目需求。云端版本采用加密传输，项目文件仅用于本次报告编制，不用于模型训练或其他用途。"),
    ("目前支持哪些报告类型？",
     "当前已开放：可行性研究报告、初步可行性研究报告、项目建议书、资金申请报告、项目评估报告、产业/企业/园区发展规划报告，共 6 种。后评价报告、社会评价报告等共 14 种类型持续开放中。"),
    ("需要安装软件或配置环境吗？",
     "不需要。云端版本直接通过浏览器访问，无需安装任何软件，开箱即用。如需私有化部署，我们提供完整的部署支持与技术文档。"),
    ("和直接使用 ChatGPT 等通用 AI 有什么区别？",
     "通用大模型不了解工程咨询行业规范，无法保证章节结构合规、字数达标，且知识来源无法追溯。新纪元数智 内置《决策评价_2024》等行业标准，三源知识引用均标注来源，跨章逻辑强制一致，专为工程报告编制场景设计。"),
    ("如何申请试用？",
     "填写页面下方的申请表单，留下姓名和联系方式，我们将在 1 个工作日内与您联系，安排产品演示与试用账号。"),
]

# ─────────────────────────────────────────
# 体验页数据
# ─────────────────────────────────────────
MODULES = [
    {
        "tag": "核心", "tag_class": "free",
        "title": "可行性研究报告",
        "desc": "全面分析项目市场、技术、财务与各类风险，科学测算投入产出与盈利水平，研判建设可行性。严格对标《决策评价_2024》规范，预定义完整章节骨架与字数预算。",
        "users": "核心报告类型",
    },
    {
        "tag": "核心", "tag_class": "free",
        "title": "初步可行性研究报告",
        "desc": "在全面可研前进行初步论证，快速评估项目基本可行性，为深入研究提供依据，降低前期决策风险。",
        "users": "核心报告类型",
    },
    {
        "tag": "可用", "tag_class": "free",
        "title": "项目建议书",
        "desc": "快速构建包含项目背景、建设方案、投资估算与效益预测的立项初稿，完成项目早期论证，加速审批进程。",
        "users": "立项阶段首选",
    },
    {
        "tag": "可用", "tag_class": "free",
        "title": "资金申请报告",
        "desc": "自动匹配政策依据，生成符合专项资金申报规范的完整材料，统筹资金规划方案，对标评审标准提升申报通过率。",
        "users": "资金申报专用",
    },
    {
        "tag": "可用", "tag_class": "free",
        "title": "项目评估报告",
        "desc": "对拟建或在建项目进行全面评估，核查可行性报告结论，分析项目实施方案及风险，为投资决策提供独立意见。",
        "users": "评审决策必备",
    },
    {
        "tag": "可用", "tag_class": "free",
        "title": "产业 / 企业 / 园区发展规划",
        "desc": "覆盖宏观趋势、政策风向、竞争格局，结合区域资源与产业特色，输出具备实操价值的中长期发展规划报告。",
        "users": "规划类报告",
    },
    {
        "tag": "即将上线", "tag_class": "soon",
        "title": "更多报告类型",
        "desc": "后评价报告、社会评价报告、专题研究报告、投资机会研究报告、PPP特许经营方案等共 14 种，持续开放中。",
        "users": "敬请期待",
    },
]


# ─────────────────────────────────────────
# 路由
# ─────────────────────────────────────────

@app.route("/")
def home():
    return render_template(
        "home.html",
        page="home",
        advantages=ADVANTAGES,
        features=FEATURES,
        steps=STEPS,
        scenarios=SCENARIOS,
        comparisons=COMPARISONS,
        faqs=FAQS,
    )


@app.route("/trial")
def trial():
    return render_template(
        "trial.html",
        page="trial",
        modules=MODULES,
    )


@app.route("/submit", methods=["POST"])
def submit():
    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()
    company = request.form.get("company", "").strip()
    report_type = request.form.get("report_type", "").strip()
    source = request.form.get("source", "homepage")

    if not name or not phone:
        flash("请填写姓名和手机号", "error")
    else:
        insert_application(name, phone, company, report_type, source=source)
        flash("已提交，感谢您的申请！我们将在 1 个工作日内与您联系。", "success")

    redirect_url = "/" if source == "homepage" else "/trial"
    return redirect(redirect_url + "#contact")


@app.route("/admin")
def admin():
    page = request.args.get("page", 1, type=int)
    edit_id = request.args.get("edit_id", None, type=int)
    confirm_id = request.args.get("confirm_id", None, type=int)

    total = get_applications_count()
    total_pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    page = max(1, min(page, total_pages))
    offset = (page - 1) * PAGE_SIZE
    rows = get_applications(offset=offset, limit=PAGE_SIZE)

    return render_template(
        "admin.html",
        page=page,
        total=total,
        total_pages=total_pages,
        rows=rows,
        edit_id=edit_id,
        confirm_id=confirm_id,
    )


@app.route("/admin/update", methods=["POST"])
def admin_update():
    id_ = request.form.get("id", type=int)
    page = request.form.get("page", 1, type=int)
    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()
    company = request.form.get("company", "").strip()
    report_type = request.form.get("report_type", "").strip()

    if id_:
        update_application(id_, name, phone, company, report_type)

    return redirect(url_for("admin", page=page))


@app.route("/admin/delete", methods=["POST"])
def admin_delete():
    id_ = request.form.get("id", type=int)
    page = request.form.get("page", 1, type=int)

    if id_:
        delete_application(id_)

    return redirect(url_for("admin", page=page))


# ─────────────────────────────────────────
# 启动
# ─────────────────────────────────────────
if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=8502, debug=True)
