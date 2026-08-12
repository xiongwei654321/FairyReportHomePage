import time
import streamlit as st
from database import init_db, insert_application


# ─────────────────────────────────────────
# 页面配置
# ─────────────────────────────────────────
def set_page_config():
    st.set_page_config(
        page_title="需求文档 · 选择报告类型，立即体验",
        page_icon="✦",
        layout="wide",
        initial_sidebar_state="collapsed",
    )


# ─────────────────────────────────────────
# 全局 CSS（与 home 同一套设计语言）
# ─────────────────────────────────────────
def inject_global_css():
    st.markdown(
        """
        <style>
        /* ══ 隐藏 Streamlit 默认元素 ══ */
        #MainMenu, footer, header,
        [data-testid="stToolbar"],
        [data-testid="stDecoration"],
        [data-testid="stStatusWidget"],
        [data-testid="collapsedControl"],
        .stDeployButton { display: none !important; visibility: hidden !important; }

        .main > div { padding: 0 !important; }
        .block-container { padding: 0 !important; max-width: 100% !important; }
        section[data-testid="stSidebar"] { display: none !important; }

        /* ══ 全屏纯白底色 ══ */
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"],
        section[data-testid="stMain"],
        [data-testid="stMainBlockContainer"],
        [data-testid="stVerticalBlock"],
        [data-testid="stHorizontalBlock"] {
            background: #fff !important;
        }

        /* ══ CSS 变量 ══ */
        :root {
            --brand:    #1854FF;
            --brand-dk: #1240CC;
            --brand-bg: #EEF2FF;
            --teal:     #36CFC9;
            --teal-bg:  #E6FFFE;
            --dark:     #1D2129;
            --gray:     #6B7280;
            --border:   #E5E7EB;
            --bg:       #F7F8FA;
        }

        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
        body, .stMarkdown {
            font-family: system-ui, -apple-system, "PingFang SC", "Noto Sans SC", sans-serif;
            color: var(--dark);
            background: #fff;
            -webkit-font-smoothing: antialiased;
        }

        /* ══ 导航栏 ══ */
        .nav {
            position: sticky; top: 0; z-index: 200;
            background: #fff; border-bottom: 1px solid var(--border);
            padding: 0 5%; display: flex; align-items: center;
            justify-content: space-between; height: 64px;
        }
        .nav-logo { font-size: 18px; font-weight: 700; color: var(--brand); letter-spacing: -0.3px; text-decoration: none; }
        .nav-links { display: flex; gap: 32px; align-items: center; }
        .nav-links a { font-size: 14px; color: var(--gray); text-decoration: none; transition: color .15s; }
        .nav-links a:hover { color: var(--brand); }
        .nav-cta {
            background: var(--brand) !important; color: #fff !important;
            padding: 8px 20px !important; border-radius: 6px;
            font-size: 14px; font-weight: 500; text-decoration: none; transition: background .15s;
        }
        .nav-cta:hover { background: var(--brand-dk) !important; }
        .nav-burger { display: none; cursor: pointer; flex-direction: column; gap: 5px; padding: 4px; }
        .nav-burger span { display: block; width: 22px; height: 2px; background: var(--dark); border-radius: 2px; }
        .nav-mobile {
            display: none; flex-direction: column; background: #fff;
            padding: 12px 5% 16px; border-bottom: 1px solid var(--border);
        }
        .nav-mobile a { padding: 11px 0; font-size: 15px; color: var(--dark); text-decoration: none; border-bottom: 1px solid #F3F4F6; }
        .nav-mobile a:last-child { border-bottom: none; }
        .nav-mobile.open { display: flex; }
        @media (max-width: 768px) { .nav-links { display: none; } .nav-burger { display: flex; } }

        /* ══ Hero ══ */
        .hero {
            background: var(--bg);
            padding: 80px 5% 72px;
            text-align: center;
        }
        .hero-tag {
            display: inline-block; font-size: 13px; color: var(--brand);
            background: var(--brand-bg); padding: 4px 14px; border-radius: 20px;
            margin-bottom: 24px; letter-spacing: .5px;
        }
        .hero h1 {
            font-size: clamp(28px, 4.5vw, 46px); font-weight: 700; color: var(--dark);
            line-height: 1.22; letter-spacing: -1px; margin-bottom: 18px;
        }
        .hero h1 em { font-style: normal; color: var(--brand); }
        .hero p { font-size: 16px; color: var(--gray); max-width: 560px; margin: 0 auto; line-height: 1.75; }

        /* ══ 数据统计栏 ══ */
        .stat-bar {
            display: flex; justify-content: center;
            background: #fff; border-bottom: 1px solid var(--border);
        }
        .stat-item {
            text-align: center; padding: 32px 52px;
            border-right: 1px solid var(--border);
        }
        .stat-item:last-child { border-right: none; }
        .stat-num { font-size: 34px; font-weight: 700; color: var(--brand); letter-spacing: -1px; }
        .stat-label { font-size: 13px; color: var(--gray); margin-top: 6px; }
        @media (max-width: 640px) {
            .stat-bar { flex-wrap: wrap; }
            .stat-item { padding: 20px 24px; border-right: none; border-bottom: 1px solid var(--border); width: 50%; }
            .stat-item:nth-child(odd) { border-right: 1px solid var(--border); }
            .stat-item:last-child { border-bottom: none; }
        }

        /* ══ Section 通用 ══ */
        .section    { padding: 80px 5%; }
        .sec-white  { background: #fff; }
        .sec-gray   { background: var(--bg); }
        .sec-title {
            font-size: clamp(22px, 3vw, 32px); font-weight: 700; color: var(--dark);
            text-align: center; margin-bottom: 12px; letter-spacing: -0.5px;
        }
        .sec-sub {
            font-size: 15px; color: var(--gray);
            text-align: center; margin-bottom: 48px; line-height: 1.7;
        }

        /* ══ 报告模块卡片（3 列） ══ */
        .module-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            max-width: 1100px;
            margin: 0 auto;
        }
        .module-card {
            background: #fff;
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 28px 24px;
            display: flex;
            flex-direction: column;
            gap: 12px;
            transition: box-shadow .15s;
        }
        .module-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,.06); }
        .module-card.coming { opacity: .5; pointer-events: none; }
        .module-tag {
            display: inline-block; font-size: 12px; font-weight: 500;
            padding: 3px 10px; border-radius: 4px;
        }
        .module-tag.free { color: var(--brand); background: var(--brand-bg); }
        .module-tag.soon { color: var(--gray); background: #F3F4F6; }
        .module-card h3 { font-size: 16px; font-weight: 600; color: var(--dark); line-height: 1.4; }
        .module-card p  { font-size: 13px; color: var(--gray); line-height: 1.7; flex: 1; }
        .module-meta {
            display: flex; align-items: center; justify-content: space-between;
            padding-top: 14px; border-top: 1px solid #F3F4F6;
        }
        .module-users { font-size: 12px; color: var(--gray); }
        .module-btn {
            font-size: 13px; font-weight: 500; color: var(--brand);
            text-decoration: none; padding: 6px 16px;
            border: 1.5px solid var(--brand); border-radius: 5px;
            transition: background .15s;
        }
        .module-btn:hover { background: var(--brand-bg); }
        @media (max-width: 900px) { .module-grid { grid-template-columns: repeat(2, 1fr); } }
        @media (max-width: 540px)  { .module-grid { grid-template-columns: 1fr; } }

        /* ══ 咨询表单 ══ */
        .contact-wrap {
            max-width: 560px; margin: 0 auto; background: #fff;
            border: 1px solid var(--border); border-radius: 12px; padding: 40px;
        }
        .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
        .form-group { margin-bottom: 18px; }
        .form-label { display: block; font-size: 13px; color: var(--gray); margin-bottom: 6px; font-weight: 500; }
        .form-input {
            width: 100%; padding: 10px 14px; font-size: 14px;
            border: 1.5px solid var(--border); border-radius: 6px; outline: none;
            color: var(--dark); background: #FAFAFA;
            transition: border-color .15s, background .15s; font-family: inherit;
        }
        .form-input:focus { border-color: var(--brand); background: #fff; }
        .form-submit {
            width: 100%; background: var(--brand); color: #fff; padding: 13px; border: none;
            border-radius: 6px; font-size: 15px; font-weight: 500; cursor: pointer;
            transition: background .15s; margin-top: 6px; font-family: inherit;
        }
        .form-submit:hover:not(:disabled) { background: var(--brand-dk); }
        .form-submit:disabled { background: var(--teal); cursor: default; }
        @media (max-width: 600px) { .contact-wrap { padding: 28px 20px; } .form-row { grid-template-columns: 1fr; } }

        /* ══ 页脚 ══ */
        .site-footer {
            background: var(--dark); color: #9CA3AF;
            text-align: center; padding: 36px 5%; font-size: 13px; line-height: 2;
        }
        .site-footer a { color: #9CA3AF; text-decoration: none; margin: 0 8px; transition: color .15s; }
        .site-footer a:hover { color: #fff; }
        .footer-links { margin-bottom: 6px; }

        /* ══ Streamlit 原生表单样式适配 ══ */
        [data-testid="stForm"] {
            background: #fff !important;
            border: 1px solid #EAECF0 !important;
            border-radius: 8px !important;
            padding: 36px 40px !important;
            box-shadow: none !important;
            max-width: 560px;
            margin: 0 auto;
        }
        div[data-testid="stTextInput"] label,
        div[data-testid="stTextInput"] label p,
        div[data-testid="stTextInput"] [data-testid="stWidgetLabel"],
        div[data-testid="stTextInput"] [data-testid="stWidgetLabel"] p,
        div[data-testid="stTextInput"] [data-testid="stWidgetLabel"] span {
            font-size: 13px !important;
            color: var(--gray) !important;
            font-weight: 500 !important;
        }
        div[data-testid="stTextInput"] input {
            border: 1px solid #EAECF0 !important;
            border-radius: 6px !important;
            background: #FAFBFC !important;
            font-size: 14px !important;
            color: var(--dark) !important;
            padding: 10px 14px !important;
            transition: border-color .15s, background .15s !important;
        }
        div[data-testid="stTextInput"] input:focus {
            border-color: var(--brand) !important;
            background: #fff !important;
            box-shadow: 0 0 0 2px rgba(24,84,255,.08) !important;
        }
        div[data-testid="stTextInput"] input::placeholder {
            color: #C8CACD !important;
            font-size: 14px !important;
        }
        [data-testid="stFormSubmitButton"] {
            margin-top: 8px !important;
        }
        [data-testid="stFormSubmitButton"] > button {
            background: var(--brand) !important;
            color: #fff !important;
            border: none !important;
            border-radius: 6px !important;
            font-size: 15px !important;
            font-weight: 500 !important;
            width: 100% !important;
            padding: 0.75rem 1rem !important;
            transition: background .15s !important;
            letter-spacing: 0.3px !important;
        }
        [data-testid="stFormSubmitButton"] > button:hover {
            background: var(--brand-dk) !important;
            color: #fff !important;
        }
        [data-testid="stFormSubmitButton"] > button:focus:not(:active) {
            border: none !important;
            box-shadow: none !important;
        }
        div[data-testid="stSelectbox"] label,
        div[data-testid="stSelectbox"] label p,
        div[data-testid="stSelectbox"] [data-testid="stWidgetLabel"],
        div[data-testid="stSelectbox"] [data-testid="stWidgetLabel"] p,
        div[data-testid="stSelectbox"] [data-testid="stWidgetLabel"] span {
            font-size: 13px !important;
            color: var(--gray) !important;
            font-weight: 500 !important;
        }
        div[data-testid="stSelectbox"] > div > div[data-baseweb="select"] > div {
            border: 1px solid #EAECF0 !important;
            border-radius: 6px !important;
            background: #FAFBFC !important;
            font-size: 14px !important;
            color: #9CA3AF !important;
        }
        div[data-testid="stSelectbox"] > div > div[data-baseweb="select"] > div > div > div {
            color: #9CA3AF !important;
        }
        div[data-testid="stSelectbox"] > div > div[data-baseweb="select"] > div:focus-within {
            border-color: var(--brand) !important;
            background: #fff !important;
            box-shadow: 0 0 0 2px rgba(24,84,255,.08) !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────
# 导航栏（带返回首页入口）
# ─────────────────────────────────────────
def render_nav():
    st.markdown(
        """
        <nav class="nav">
            <a class="nav-logo" href="/">✦ 需求文档</a>
            <div class="nav-links">
                <a href="/">首页</a>
                <a href="/#advantages">核心优势</a>
                <a href="/#cases">特色功能</a>
                <a href="#contact">联系我们</a>
                <a class="nav-cta" href="#contact">申请试用</a>
            </div>
            <div class="nav-burger"
                 onclick="document.getElementById('navMobile').classList.toggle('open')"
                 aria-label="展开菜单">
                <span></span><span></span><span></span>
            </div>
        </nav>
        <div class="nav-mobile" id="navMobile">
            <a href="/">首页</a>
            <a href="/#advantages">核心优势</a>
            <a href="/#cases">特色功能</a>
            <a href="#contact">联系我们</a>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────
# 首屏 Hero
# ─────────────────────────────────────────
def render_hero():
    st.markdown(
        """
        <section class="hero">
            <span class="hero-tag">14 种法定报告类型 · 21 类工程专业 · 严格对标行业规范</span>
            <h1>选择报告类型，<em>立即开始</em>生成</h1>
            <p>
                严格对标《决策评价_2024》行业规范，每种报告都有预定义的章节骨架与字数预算，
                覆盖可行性研究、项目评估、发展规划等工程咨询全场景。
            </p>
        </section>
        """,
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────
# 数据统计栏
# ─────────────────────────────────────────
def render_stats():
    st.markdown(
        """
        <div class="stat-bar">
            <div class="stat-item">
                <div class="stat-num">14</div>
                <div class="stat-label">报告类型</div>
            </div>
            <div class="stat-item">
                <div class="stat-num">21</div>
                <div class="stat-label">工程专业</div>
            </div>
            <div class="stat-item">
                <div class="stat-num">50</div>
                <div class="stat-label">鼓励类产业</div>
            </div>
            <div class="stat-item">
                <div class="stat-num">10x</div>
                <div class="stat-label">效率提升</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────
# 报告模块卡片（7 个）
# ─────────────────────────────────────────
def render_modules():
    modules = [
        {
            "tag": "核心", "tag_class": "free",
            "title": "可行性研究报告",
            "desc": "全面分析项目市场、技术、财务与各类风险，科学测算投入产出与盈利水平，研判建设可行性。严格对标《决策评价_2024》规范，预定义完整章节骨架与字数预算。",
            "users": "核心报告类型",
            "link": "#contact",
        },
        {
            "tag": "核心", "tag_class": "free",
            "title": "初步可行性研究报告",
            "desc": "在全面可研前进行初步论证，快速评估项目基本可行性，为深入研究提供依据，降低前期决策风险。",
            "users": "核心报告类型",
            "link": "#contact",
        },
        {
            "tag": "可用", "tag_class": "free",
            "title": "项目建议书",
            "desc": "快速构建包含项目背景、建设方案、投资估算与效益预测的立项初稿，完成项目早期论证，加速审批进程。",
            "users": "立项阶段首选",
            "link": "#contact",
        },
        {
            "tag": "可用", "tag_class": "free",
            "title": "资金申请报告",
            "desc": "自动匹配政策依据，生成符合专项资金申报规范的完整材料，统筹资金规划方案，对标评审标准提升申报通过率。",
            "users": "资金申报专用",
            "link": "#contact",
        },
        {
            "tag": "可用", "tag_class": "free",
            "title": "项目评估报告",
            "desc": "对拟建或在建项目进行全面评估，核查可行性报告结论，分析项目实施方案及风险，为投资决策提供独立意见。",
            "users": "评审决策必备",
            "link": "#contact",
        },
        {
            "tag": "可用", "tag_class": "free",
            "title": "产业 / 企业 / 园区发展规划",
            "desc": "覆盖宏观趋势、政策风向、竞争格局，结合区域资源与产业特色，输出具备实操价值的中长期发展规划报告。",
            "users": "规划类报告",
            "link": "#contact",
        },
        {
            "tag": "即将上线", "tag_class": "soon",
            "title": "更多报告类型",
            "desc": "后评价报告、社会评价报告、专题研究报告、投资机会研究报告、PPP特许经营方案等共 14 种，持续开放中。",
            "users": "敬请期待",
            "link": None,
        },
    ]

    cards_html = ""
    for m in modules:
        coming_class = " coming" if m["tag_class"] == "soon" else ""
        cards_html += f"""
        <div class="module-card{coming_class}">
            <span class="module-tag {m['tag_class']}">{m['tag']}</span>
            <h3>{m['title']}</h3>
            <p>{m['desc']}</p>
            <div class="module-meta">
                <span class="module-users">{m['users']}</span>
            </div>
        </div>
        """

    st.markdown(
        f"""
        <section class="section sec-gray" id="modules">
            <div class="sec-title">选择报告类型</div>
            <div class="sec-sub">覆盖 14 种法定报告类型，严格对标国家规范，每种报告预定义章节骨架与字数预算</div>
            <div class="module-grid">{cards_html}</div>
        </section>
        """,
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────
# 申请表单（Streamlit 原生 + SQLite 写入）
# ─────────────────────────────────────────
def render_contact():
    st.markdown(
        """
        <section id="contact" style="background:#fff; padding: 56px 5% 32px; text-align:center;">
            <div class="sec-title">申请体验 需求文档</div>
            <div class="sec-sub" style="margin-bottom: 0;">
                无需安装，浏览器即可使用 · 支持私有化部署 · 数据安全可控<br>
                留下联系方式，我们将在 1 个工作日内与您联系
            </div>
        </section>
        <div style="height:28px;background:#fff;"></div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("apply_form_trial", clear_on_submit=True):
        c1, c2 = st.columns(2)
        name  = c1.text_input("您的姓名 *", placeholder="请输入姓名")
        phone = c2.text_input("联系手机 *", placeholder="请输入手机号")
        company = st.text_input("公司名称（选填）", placeholder="请输入公司名称")
        report_type = st.selectbox(
            "报告类型（选填）",
            options=[
                "请选择报告类型",
                "可行性研究报告",
                "初步可行性研究报告",
                "项目建议书",
                "资金申请报告",
                "项目评估报告",
                "产业 / 企业 / 园区发展规划报告",
            ],
        )
        submitted = st.form_submit_button("提交申请", use_container_width=True)

    if submitted:
        if not name.strip() or not phone.strip():
            st.error("请填写姓名和手机号")
        else:
            selected_type = "" if report_type.startswith("请选择") else report_type
            insert_application(
                name.strip(), phone.strip(),
                company.strip(), selected_type,
                source="trial",
            )
            msg = st.empty()
            msg.success("✓ 已提交，感谢您的申请！我们将在 1 个工作日内与您联系。")
            time.sleep(3)
            msg.empty()

    st.markdown('<div style="height:72px;background:#fff;"></div>', unsafe_allow_html=True)


# ─────────────────────────────────────────
# 页脚
# ─────────────────────────────────────────
def render_footer():
    st.markdown(
        """
        <footer class="site-footer">
            <div class="footer-links">
                <a href="/">首页</a>·
                <a href="/#advantages">核心优势</a>·
                <a href="/#cases">特色功能</a>·
                <a href="#contact">联系我们</a>
            </div>
            <div>✦ 需求文档 &nbsp;·&nbsp; AI驱动的工程咨询报告编制系统</div>
            <div style="margin-top:4px; font-size:12px;">
                © 2026 需求文档. All rights reserved. &nbsp;·&nbsp; 无需安装，浏览器即可使用 · 支持私有化部署
            </div>
        </footer>
        """,
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────
# 主入口
# ─────────────────────────────────────────
def main():
    init_db()
    set_page_config()
    inject_global_css()
    render_nav()
    render_hero()
    render_stats()
    render_modules()
    render_contact()
    render_footer()


if __name__ == "__main__":
    main()
