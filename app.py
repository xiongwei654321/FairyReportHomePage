import time
import streamlit as st
import streamlit.components.v1 as components
from database import init_db, insert_application


# ─────────────────────────────────────────
# 页面配置
# ─────────────────────────────────────────
def set_page_config():
    st.set_page_config(
        page_title="新纪元数智 · AI驱动的工程咨询报告编制系统",
        page_icon="✦",
        layout="wide",
        initial_sidebar_state="collapsed",
    )


# ─────────────────────────────────────────
# 全局 CSS：品牌色 + 隐藏 Streamlit 默认控件 + 各模块样式
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

        /* ══ 消除 Streamlit 容器默认边距 ══ */
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

        /* ══ CSS 变量：品牌色统一管理 ══ */
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

        /* ══ 全局基础 ══ */
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
        body, .stMarkdown {
            font-family: system-ui, -apple-system, "PingFang SC", "Noto Sans SC", sans-serif;
            color: var(--dark);
            background: #fff;
            -webkit-font-smoothing: antialiased;
        }

        /* ══ 导航栏 ══ */
        .nav {
            position: sticky;
            top: 0;
            z-index: 200;
            background: #fff;
            border-bottom: 1px solid var(--border);
            padding: 0 5%;
            display: flex;
            align-items: center;
            justify-content: space-between;
            height: 64px;
        }
        .nav-logo {
            font-size: 18px;
            font-weight: 700;
            color: var(--brand);
            letter-spacing: -0.3px;
            text-decoration: none;
        }
        .nav-links { display: flex; gap: 32px; align-items: center; }
        .nav-links a {
            font-size: 14px;
            color: var(--gray);
            text-decoration: none;
            transition: color .15s;
        }
        .nav-links a:hover { color: var(--brand); }
        .nav-cta {
            background: var(--brand) !important;
            color: #fff !important;
            padding: 8px 20px !important;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 500;
            text-decoration: none;
            transition: background .15s;
        }
        .nav-cta:hover { background: var(--brand-dk) !important; }

        /* ══ 汉堡菜单（移动端） ══ */
        .nav-burger {
            display: none;
            cursor: pointer;
            flex-direction: column;
            gap: 5px;
            padding: 4px;
        }
        .nav-burger span {
            display: block;
            width: 22px;
            height: 2px;
            background: var(--dark);
            border-radius: 2px;
        }
        .nav-mobile {
            display: none;
            flex-direction: column;
            background: #fff;
            padding: 12px 5% 16px;
            border-bottom: 1px solid var(--border);
        }
        .nav-mobile a {
            padding: 11px 0;
            font-size: 15px;
            color: var(--dark);
            text-decoration: none;
            border-bottom: 1px solid #F3F4F6;
        }
        .nav-mobile a:last-child { border-bottom: none; }
        .nav-mobile.open { display: flex; }

        @media (max-width: 768px) {
            .nav-links { display: none; }
            .nav-burger { display: flex; }
        }

        /* ══ Hero 首屏 ══ */
        .hero {
            background: var(--bg);
            padding: 96px 5% 88px;
            text-align: center;
        }
        .hero-tag {
            display: inline-block;
            font-size: 13px;
            color: var(--brand);
            background: var(--brand-bg);
            padding: 4px 14px;
            border-radius: 20px;
            margin-bottom: 24px;
            letter-spacing: .5px;
        }
        .hero h1 {
            font-size: clamp(30px, 5vw, 52px);
            font-weight: 700;
            color: var(--dark);
            line-height: 1.22;
            letter-spacing: -1px;
            margin-bottom: 20px;
        }
        .hero h1 em { font-style: normal; color: var(--brand); }
        .hero p {
            font-size: 17px;
            color: var(--gray);
            max-width: 560px;
            margin: 0 auto 40px;
            line-height: 1.75;
        }
        .hero-btns { display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; }
        .btn-primary {
            background: var(--brand);
            color: #fff;
            padding: 12px 28px;
            border-radius: 6px;
            font-size: 15px;
            font-weight: 500;
            text-decoration: none;
            transition: background .15s;
            display: inline-block;
        }
        .btn-primary:hover { background: var(--brand-dk); color: #fff; }
        .btn-outline {
            background: transparent;
            color: var(--brand);
            padding: 12px 28px;
            border-radius: 6px;
            font-size: 15px;
            font-weight: 500;
            text-decoration: none;
            border: 1.5px solid var(--brand);
            transition: background .15s;
            display: inline-block;
        }
        .btn-outline:hover { background: var(--brand-bg); }

        /* ══ Section 通用 ══ */
        .section    { padding: 80px 5%; }
        .sec-white  { background: #fff; }
        .sec-gray   { background: var(--bg); }
        .sec-title {
            font-size: clamp(22px, 3vw, 32px);
            font-weight: 700;
            color: var(--dark);
            text-align: center;
            margin-bottom: 12px;
            letter-spacing: -0.5px;
        }
        .sec-sub {
            font-size: 15px;
            color: var(--gray);
            text-align: center;
            margin-bottom: 52px;
            line-height: 1.7;
        }

        /* ══ 产品优势卡片 ══ */
        .adv-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            max-width: 1100px;
            margin: 0 auto;
        }
        .adv-card {
            background: #fff;
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 32px 24px;
            text-align: left;
        }
        .adv-icon {
            width: 42px;
            height: 42px;
            background: var(--brand-bg);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            margin-bottom: 20px;
        }
        .adv-card h3 {
            font-size: 16px;
            font-weight: 600;
            color: var(--dark);
            margin-bottom: 10px;
        }
        .adv-card p { font-size: 14px; color: var(--gray); line-height: 1.7; }

        @media (max-width: 900px) { .adv-grid { grid-template-columns: repeat(2, 1fr); } }
        @media (max-width: 520px) { .adv-grid { grid-template-columns: 1fr; } }

        /* ══ 3 列网格（用于 6 卡片特色功能）══ */
        .adv-grid-3 {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            max-width: 1100px;
            margin: 0 auto;
        }
        @media (max-width: 900px) { .adv-grid-3 { grid-template-columns: repeat(2, 1fr); } }
        @media (max-width: 520px) { .adv-grid-3 { grid-template-columns: 1fr; } }

        /* ══ 客户案例卡片 ══ */
        .case-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            max-width: 1100px;
            margin: 0 auto;
        }
        .case-card {
            background: #fff;
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 28px 24px;
        }
        .case-tag {
            display: inline-block;
            font-size: 12px;
            color: var(--teal);
            background: var(--teal-bg);
            padding: 3px 10px;
            border-radius: 4px;
            margin-bottom: 14px;
            font-weight: 500;
        }
        .case-card h3 {
            font-size: 15px;
            font-weight: 600;
            color: var(--dark);
            margin-bottom: 10px;
            line-height: 1.5;
        }
        .case-card p { font-size: 13px; color: var(--gray); line-height: 1.75; }
        .case-result {
            margin-top: 16px;
            font-size: 13px;
            color: var(--brand);
            font-weight: 500;
        }

        @media (max-width: 900px) { .case-grid { grid-template-columns: repeat(2, 1fr); } }
        @media (max-width: 540px) { .case-grid { grid-template-columns: 1fr; } }

        /* ══ 合作流程 ══ */
        .process-wrap {
            display: flex;
            align-items: flex-start;
            justify-content: center;
            max-width: 1000px;
            margin: 0 auto;
        }
        .process-item {
            flex: 1;
            text-align: center;
            padding: 0 10px;
            position: relative;
        }
        /* 步骤之间的连接线 */
        .process-item::after {
            content: '';
            position: absolute;
            top: 19px;
            left: calc(50% + 22px);
            right: calc(0% - 50% + 22px);
            width: calc(100% - 44px);
            height: 1px;
            background: var(--border);
        }
        .process-item:last-child::after { display: none; }
        .process-num {
            width: 40px;
            height: 40px;
            background: var(--brand);
            color: #fff;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 15px;
            font-weight: 700;
            margin: 0 auto 16px;
            position: relative;
            z-index: 1;
        }
        .process-item h4 {
            font-size: 14px;
            font-weight: 600;
            color: var(--dark);
            margin-bottom: 8px;
        }
        .process-item p { font-size: 13px; color: var(--gray); line-height: 1.65; }

        @media (max-width: 768px) {
            .process-wrap { flex-direction: column; gap: 24px; align-items: center; }
            .process-item::after { display: none; }
            .process-item { width: 100%; max-width: 300px; }
        }

        /* ══ 咨询表单 ══ */
        .contact-wrap {
            max-width: 560px;
            margin: 0 auto;
            background: #fff;
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 40px;
        }
        .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
        .form-group { margin-bottom: 18px; }
        .form-label {
            display: block;
            font-size: 13px;
            color: var(--gray);
            margin-bottom: 6px;
            font-weight: 500;
        }
        .form-input {
            width: 100%;
            padding: 10px 14px;
            font-size: 14px;
            border: 1.5px solid var(--border);
            border-radius: 6px;
            outline: none;
            color: var(--dark);
            background: #FAFAFA;
            transition: border-color .15s, background .15s;
            font-family: inherit;
        }
        .form-input:focus { border-color: var(--brand); background: #fff; }
        .form-textarea { min-height: 96px; resize: vertical; }
        .form-submit {
            width: 100%;
            background: var(--brand);
            color: #fff;
            padding: 13px;
            border: none;
            border-radius: 6px;
            font-size: 15px;
            font-weight: 500;
            cursor: pointer;
            transition: background .15s;
            margin-top: 6px;
            font-family: inherit;
        }
        .form-submit:hover:not(:disabled) { background: var(--brand-dk); }
        .form-submit:disabled { background: var(--teal); cursor: default; }

        @media (max-width: 600px) {
            .contact-wrap { padding: 28px 20px; }
            .form-row { grid-template-columns: 1fr; }
        }

        /* ══ 页脚 ══ */
        .site-footer {
            background: var(--dark);
            color: #9CA3AF;
            text-align: center;
            padding: 36px 5%;
            font-size: 13px;
            line-height: 2;
        }
        .site-footer a {
            color: #9CA3AF;
            text-decoration: none;
            margin: 0 8px;
            transition: color .15s;
        }
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
        /* 全局覆盖 baseweb select / 下拉框为浅色 */
        div[data-baseweb="select"],
        div[data-baseweb="select"] > div,
        div[data-baseweb="select"] > div > div,
        div[data-baseweb="select"] > div > div > div,
        div[data-baseweb="select"] > div > div > div > div,
        div[data-baseweb="select"] input,
        div[data-baseweb="select"] [role="combobox"],
        div[data-baseweb="select"] [aria-haspopup="listbox"] {
            background: #FAFBFC !important;
            background-color: #FAFBFC !important;
            color: #111827 !important;
            border-color: #EAECF0 !important;
            border-radius: 6px !important;
            font-size: 14px !important;
            -webkit-text-fill-color: #111827 !important;
        }
        /* placeholder 与未选中状态 */
        div[data-baseweb="select"] input::placeholder,
        div[data-baseweb="select"] [aria-selected="false"] {
            color: #9CA3AF !important;
            -webkit-text-fill-color: #9CA3AF !important;
        }
        /* 下拉箭头 */
        div[data-baseweb="select"] svg {
            color: #6B7280 !important;
        }
        /* 下拉菜单面板：白色（portal 可能挂在 body 下） */
        body div[data-baseweb="popover"],
        body div[data-baseweb="popover"] > div,
        body div[data-baseweb="popover"] > div > div,
        body div[data-baseweb="popover"] > div > div > div,
        body div[data-baseweb="menu"],
        body div[data-baseweb="menu"] ul,
        body div[data-baseweb="menu"] li,
        body div[data-baseweb="menu"] div {
            background: #fff !important;
            background-color: #fff !important;
            color: #111827 !important;
            border-color: #E5E7EB !important;
            font-size: 14px !important;
            -webkit-text-fill-color: #111827 !important;
        }
        /* 选项 hover / 选中 */
        body div[data-baseweb="menu"] li:hover,
        body div[data-baseweb="menu"] li[aria-selected="true"],
        body div[data-baseweb="menu"] li:hover > div,
        body div[data-baseweb="menu"] li[aria-selected="true"] > div {
            background: #EEF2FF !important;
            background-color: #EEF2FF !important;
            color: #1854FF !important;
            -webkit-text-fill-color: #1854FF !important;
        }

        /* ══ Hero 信任标签 ══ */
        .hero-trust {
            margin-top: 36px;
            padding-top: 20px;
            border-top: 1px solid var(--border);
            display: inline-block;
            font-size: 13px;
            color: var(--gray);
            letter-spacing: 0.2px;
        }

        /* ══ 对比表 ══ */
        /* 外层卡片：border-radius + overflow:hidden 裁剪表格四角 */
        .cmp-wrap {
            max-width: 960px;
            margin: 0 auto;
            border: 1px solid var(--border);
            border-radius: 10px;
            overflow: hidden;
        }
        /* 横向滚动层：只控制移动端滚动，不影响外层圆角 */
        .cmp-scroll {
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
        }
        .cmp-table {
            width: 100%;
            border-collapse: collapse;
            min-width: 560px;
        }
        .cmp-table thead th {
            padding: 16px 20px;
            text-align: center;
            font-size: 13px;
            font-weight: 600;
            color: var(--dark);
            background: var(--bg);
            border-bottom: 1px solid var(--border);
            white-space: nowrap;
        }
        .cmp-table thead th:first-child {
            text-align: left;
            border-right: 1px solid var(--border);
        }
        .cmp-table thead th.cmp-hl {
            color: var(--brand);
            background: var(--brand-bg);
        }
        .cmp-table tbody td {
            padding: 16px 20px;
            text-align: center;
            border-bottom: 1px solid var(--border);
            color: var(--gray);
            line-height: 1.7;
            vertical-align: top;
            font-size: 13px;
        }
        .cmp-table tbody tr:last-child td { border-bottom: none; }
        .cmp-table tbody td:first-child {
            text-align: left;
            font-weight: 500;
            color: var(--dark);
            background: var(--bg);
            border-right: 1px solid var(--border);
            white-space: nowrap;
        }
        .cmp-table tbody td.cmp-hl {
            background: #FAFBFF;
            color: var(--dark);
        }

        /* ══ 对比表移动端：table → 卡片堆叠 ══ */
        @media (max-width: 640px) {
            .cmp-wrap { border-radius: 0; border-left: none; border-right: none; }
            .cmp-scroll { overflow-x: visible; }
            .cmp-table, .cmp-table tbody { display: block; min-width: unset; width: 100%; }
            .cmp-table thead { display: none; }
            .cmp-table tbody tr {
                display: grid;
                grid-template-columns: 1fr 1fr;
                border-bottom: 1px solid var(--border);
            }
            .cmp-table tbody tr:last-child { border-bottom: none; }
            .cmp-table tbody td {
                display: block;
                text-align: left;
                border: none;
                padding: 12px 16px;
                font-size: 13px;
                line-height: 1.65;
                white-space: normal;
            }
            /* 维度名：独占一行 */
            .cmp-table tbody td:first-child {
                grid-column: 1 / -1;
                background: var(--bg);
                border-bottom: 1px solid var(--border);
                border-right: none;
                font-weight: 600;
                font-size: 13px;
                padding: 10px 16px;
            }
            /* 通用大模型 列：加小标签 */
            .cmp-table tbody td:nth-child(2)::before {
                content: "通用大模型";
                display: block;
                font-size: 11px;
                font-weight: 500;
                color: var(--gray);
                margin-bottom: 5px;
                letter-spacing: 0.3px;
            }
            .cmp-table tbody td:nth-child(2) {
                border-right: 1px solid var(--border);
            }
            /* 新纪元数智 列：加小标签 */
            .cmp-table tbody td.cmp-hl::before {
                content: "✦ 新纪元数智";
                display: block;
                font-size: 11px;
                font-weight: 600;
                color: var(--brand);
                margin-bottom: 5px;
                letter-spacing: 0.3px;
            }
        }

        /* ══ FAQ ══ */
        .faq-wrap { max-width: 760px; margin: 0 auto; }
        .faq-item { border-bottom: 1px solid var(--border); padding: 28px 0; }
        .faq-item:first-child { border-top: 1px solid var(--border); }
        .faq-q { font-size: 15px; font-weight: 600; color: var(--dark); margin-bottom: 12px; line-height: 1.5; }
        .faq-a { font-size: 14px; color: var(--gray); line-height: 1.85; }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────
# 导航栏
# ─────────────────────────────────────────
def render_nav():
    st.markdown(
        """
        <nav class="nav">
            <a class="nav-logo" href="#">✦ 新纪元数智</a>
            <div class="nav-links">
                <a href="#advantages">核心优势</a>
                <a href="#cases">特色功能</a>
                <a href="#process">工作流程</a>
                <a href="#contact">联系我们</a>
                <a class="nav-cta" href="/trial">立即体验</a>
            </div>
            <div class="nav-burger"
                 onclick="document.getElementById('navMobile').classList.toggle('open')"
                 aria-label="展开菜单">
                <span></span><span></span><span></span>
            </div>
        </nav>
        <div class="nav-mobile" id="navMobile">
            <a href="#advantages">核心优势</a>
            <a href="#cases">特色功能</a>
            <a href="#process">工作流程</a>
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
            <span class="hero-tag">工程咨询行业首款 AI 报告编制平台 · 14 种法定报告类型</span>
            <h1>从<em>数周</em>到<em>数小时</em><br>工程咨询报告的智能革命</h1>
            <p>
                新纪元数智 专为中国工程咨询行业打造，融合项目资料库、行业知识库与实时互联网三源信息，
                覆盖 14 种法定报告类型，AI 逐章编写、自动校验篇幅、保障全文逻辑自洽。
            </p>
            <div class="hero-btns">
                <a class="btn-primary" href="/trial">立即体验</a>
                <a class="btn-outline" href="#cases">了解六大特色功能</a>
            </div>
            <p class="hero-trust">🔒 支持私有化本地部署 &nbsp;·&nbsp; 数据不出内网 &nbsp;·&nbsp; 适配涉密项目</p>
        </section>
        """,
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────
# 产品优势（4 列卡片）
# ─────────────────────────────────────────
def render_advantages():
    advantages = [
        ("🏗️", "行业规范深度嵌入",
         "14 种报告模板严格对标《决策评价_2024》，21 类工程专业（GBZ/T 40846-2021）、50 类鼓励产业（产业结构调整指导目录 2024）——每个章节标题与字数预算均源自国家规范，非通用套壳。"),
        ("🔍", "三源知识融合",
         "编写每章时同步融合：①项目资料库（用户上传文件向量检索）、②行业通用知识库（预置技术标准与规范）、③实时互联网搜索（最新政策数据与行业动态），引用均标注可追溯来源。"),
        ("🔒", "全文逻辑自洽",
         "跨章方案锁定：比选结论一旦确定，后续章节禁止推翻；过期章节检测：前序修改后，后续章节自动标记「上下文过期」并级联提醒——从第一页到最后一页逻辑一致。"),
        ("⚡", "效率指数级跃升",
         "传统流程需数周到数月；新纪元数智 五步向导：导入资料 → 确认大纲 → 逐章 AI 流式生成 → 人机审阅 → 一键导出 Word，数小时交付初稿，效率提升 10 倍以上。"),
    ]
    cards_html = "".join(
        f'<div class="adv-card adv-card-has-tip" data-tip-icon="{icon}" data-tip-title="{title}" data-tip="{desc}">'
        f'<div class="adv-icon">{icon}</div>'
        f'<h3>{title}</h3>'
        f'<p>{desc}</p>'
        f'</div>'
        for icon, title, desc in advantages
    )
    st.markdown(
        f"""
        <style>
        .adv-card-has-tip {{
            transition: transform 0.2s cubic-bezier(0.34,1.2,0.64,1),
                        box-shadow 0.2s ease,
                        border-color 0.2s ease;
        }}
        .adv-card-has-tip:hover {{
            transform: translateY(4px);
            box-shadow: 0 8px 20px rgba(24,84,255,0.08);
            border-color: rgba(24,84,255,0.3);
        }}
        @media (hover: none) {{
            .adv-card-has-tip:active {{
                transform: translateY(4px);
                box-shadow: 0 8px 20px rgba(24,84,255,0.08);
                border-color: rgba(24,84,255,0.3);
            }}
        }}
        </style>
        <section class="section sec-white" id="advantages">
            <div class="sec-title">核心优势</div>
            <div class="sec-sub">不是通用 AI 套壳，而是深度垂直于工程咨询行业的专业系统</div>
            <div class="adv-grid">{cards_html}</div>
        </section>
        """,
        unsafe_allow_html=True,
    )
    # Script runs inside an iframe (height=0); window.parent accesses the main page
    components.html(
        """
        <script>
        (function () {
            var doc = window.parent.document;
            var showTimer = null;
            var hideTimer = null;

            function ensureTip() {
                var el = doc.getElementById('__adv_float_tip__');
                if (el) return el;
                el = doc.createElement('div');
                el.id = '__adv_float_tip__';
                el.style.cssText = [
                    'position:fixed',
                    'z-index:99999',
                    'background:#1c2128',
                    'color:#cdd9e5',
                    'border-radius:10px',
                    'padding:16px 18px',
                    'width:300px',
                    'max-width:calc(100vw - 32px)',
                    'box-shadow:0 8px 32px rgba(0,0,0,0.4),0 0 0 1px rgba(255,255,255,0.07)',
                    'font-size:13px',
                    'line-height:1.7',
                    'pointer-events:none',
                    'font-family:system-ui,-apple-system,sans-serif',
                    'opacity:0',
                    'transform:translateY(-6px)',
                    'transition:opacity 0.16s ease,transform 0.16s ease'
                ].join(';');
                doc.body.appendChild(el);
                return el;
            }

            function positionTip(el, card) {
                var rect = card.getBoundingClientRect();
                var pw = window.parent.innerWidth;
                var ph = window.parent.innerHeight;
                var w = 300;
                var left = rect.left + rect.width / 2 - w / 2;
                var top  = rect.bottom + 10;
                if (left + w > pw - 16) left = pw - w - 16;
                if (left < 16) left = 16;
                var h = el.offsetHeight;
                if (top + h > ph - 16) top = rect.top - h - 10;
                el.style.left = left + 'px';
                el.style.top  = top  + 'px';
            }

            function showTip(card) {
                clearTimeout(hideTimer);
                showTimer = setTimeout(function () {
                    var el = ensureTip();
                    var icon    = card.getAttribute('data-tip-icon') || '';
                    var title   = card.getAttribute('data-tip-title') || '';
                    var content = card.getAttribute('data-tip') || '';
                    el.innerHTML =
                        '<div style="display:flex;align-items:center;gap:8px;margin-bottom:10px">' +
                          '<span style="font-size:15px;line-height:1">' + icon + '</span>' +
                          '<span style="font-size:13px;font-weight:600;color:#e6edf3">' + title + '</span>' +
                        '</div>' +
                        '<div style="height:1px;background:rgba(255,255,255,0.07);margin-bottom:10px"></div>' +
                        '<div style="color:#8b949e;line-height:1.75">' + content + '</div>';
                    positionTip(el, card);
                    requestAnimationFrame(function () {
                        el.style.opacity = '1';
                        el.style.transform = 'translateY(0)';
                    });
                }, 120);
            }

            function hideTip() {
                clearTimeout(showTimer);
                hideTimer = setTimeout(function () {
                    var el = doc.getElementById('__adv_float_tip__');
                    if (el) {
                        el.style.opacity = '0';
                        el.style.transform = 'translateY(-6px)';
                    }
                }, 0);
            }

            var activeCard = null;
            var touchStartX = 0;
            var touchStartY = 0;
            var touchMoved  = false;
            var pendingCard = null;

            function hideTipImmediate() {
                clearTimeout(showTimer);
                clearTimeout(hideTimer);
                var el = doc.getElementById('__adv_float_tip__');
                if (el) {
                    el.style.opacity = '0';
                    el.style.transform = 'translateY(-6px)';
                }
                activeCard = null;
            }

            function attach() {
                doc.querySelectorAll('.adv-card-has-tip').forEach(function (card) {
                    if (card._advTipAttached) return;
                    card._advTipAttached = true;

                    // 桌面端：鼠标悬停
                    card.addEventListener('mouseenter', function () { showTip(card); });
                    card.addEventListener('mouseleave', hideTip);

                    // 移动端：记录按下位置，不阻止滚动
                    card.addEventListener('touchstart', function (e) {
                        touchStartX = e.touches[0].clientX;
                        touchStartY = e.touches[0].clientY;
                        touchMoved  = false;
                        pendingCard = card;
                    }, { passive: true });

                    // 手指移动超过阈值视为滚动，取消点击并关闭提示
                    card.addEventListener('touchmove', function (e) {
                        var dx = e.touches[0].clientX - touchStartX;
                        var dy = e.touches[0].clientY - touchStartY;
                        if (Math.abs(dx) > 8 || Math.abs(dy) > 8) {
                            touchMoved = true;
                            hideTipImmediate();
                        }
                    }, { passive: true });

                    // 抬起手指且未滑动 → 切换提示框
                    card.addEventListener('touchend', function () {
                        if (!touchMoved && pendingCard === card) {
                            if (activeCard === card) {
                                hideTipImmediate();
                            } else {
                                hideTipImmediate();
                                activeCard = card;
                                showTip(card);
                            }
                        }
                        pendingCard = null;
                    });
                });

                // 页面滚动时立即关闭提示
                if (!doc._advScrollAttached) {
                    doc._advScrollAttached = true;
                    window.parent.addEventListener('scroll', hideTipImmediate, { passive: true });
                }

                // 点击页面其他区域关闭提示
                if (!doc._advOutsideAttached) {
                    doc._advOutsideAttached = true;
                    doc.addEventListener('touchstart', function (e) {
                        if (activeCard && !activeCard.contains(e.target)) {
                            hideTipImmediate();
                        }
                    }, { passive: true });
                }
            }

            attach();
            setTimeout(attach, 500);
            setTimeout(attach, 1500);
        })();
        </script>
        """,
        height=0,
        scrolling=False,
    )


# ─────────────────────────────────────────
# 应用场景（4 列卡片）
# ─────────────────────────────────────────
def render_cases():
    scenarios = [
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
    cards_html = "".join(
        f"""
        <div class="adv-card">
            <div class="adv-icon">{icon}</div>
            <h3>{title}</h3>
            <p>{desc}</p>
        </div>
        """
        for icon, title, desc in scenarios
    )
    st.markdown(
        f"""
        <section class="section sec-gray" id="cases">
            <div class="sec-title">六大特色功能</div>
            <div class="sec-sub">针对工程咨询报告的独特需求设计的六项专有机制——确保报告引用真实、逻辑自洽、篇幅精准</div>
            <div class="adv-grid-3">{cards_html}</div>
        </section>
        """,
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────
# 操作流程（横向步骤 + 连接线）
# ─────────────────────────────────────────
def render_process():
    steps = [
        ("项目初始化", "输入报告名称，AI 自动匹配鼓励类产业、生成主题关键词。21 类工程专业 · 50 类鼓励类产业 · AI 智能推荐。"),
        ("资料导入", "上传 Word/Excel/CSV 等项目资料，自动解析、智能切片、向量入库。支持 5 种格式 · 800字智能切片 · 100字重叠保上下文。"),
        ("确定大纲", "14 种预定义章节骨架直接使用，AI 建议最优写作顺序，核心章节先写，概述结论最后写。"),
        ("编写 & 审阅", "逐章流式生成，三阶段交互：生成提示词 → 确认/编辑 → AI 编写。实时审阅，随时修改，自动字数校验。"),
        ("合并导出", "一键导出排版规范的 Word 文档，自动生成目录与三级参考资料清单。5 级标题层级 · 原生表格 · LaTeX 公式。"),
    ]
    items_html = "".join(
        f"""
        <div class="process-item">
            <div class="process-num">{i}</div>
            <h4>{title}</h4>
            <p>{desc}</p>
        </div>
        """
        for i, (title, desc) in enumerate(steps, 1)
    )
    st.markdown(
        f"""
        <section class="section sec-white" id="process">
            <div class="sec-title">五步工作流程</div>
            <div class="sec-sub">无需学习复杂操作，五步向导式工作流，从资料到成稿，全程向导化</div>
            <div class="process-wrap">{items_html}</div>
        </section>
        """,
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────
# 对比区块：为什么不直接用通用 AI？
# ─────────────────────────────────────────
def render_comparison():
    rows = [
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
    rows_html = "".join(
        f"""<tr>
            <td>{dim}</td>
            <td>{col1}</td>
            <td class="cmp-hl">{col2}</td>
        </tr>"""
        for dim, col1, col2 in rows
    )
    st.markdown(
        f"""
        <section class="section sec-white" id="comparison">
            <div class="sec-title">为什么不直接用通用 AI？</div>
            <div class="sec-sub">通用大模型解决不了工程咨询报告的核心问题——行业规范合规、引用可追溯、全文逻辑自洽</div>
            <div class="cmp-wrap">
                <div class="cmp-scroll">
                    <table class="cmp-table">
                        <thead>
                            <tr>
                                <th>对比维度</th>
                                <th>通用大模型</th>
                                <th class="cmp-hl">✦ 新纪元数智
                                    <br><span style="font-size:12px;font-weight:400;">专为工程咨询设计</span>
                                </th>
                            </tr>
                        </thead>
                        <tbody>{rows_html}</tbody>
                    </table>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────
# 典型使用场景（占位，待替换为真实案例）
# ─────────────────────────────────────────
def render_scenarios():
    scenarios = [
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
    cards_html = "".join(
        f"""
        <div class="case-card">
            <span class="case-tag">{rtype}</span>
            <h3>{title}</h3>
            <p><strong style="color:var(--dark);font-size:13px;">痛点：</strong>{pain}</p>
            <p style="margin-top:10px;">{solution}</p>
            <div class="case-result">→ {result}</div>
        </div>
        """
        for rtype, title, pain, solution, result in scenarios
    )
    st.markdown(
        f"""
        <section class="section sec-gray" id="scenarios">
            <div class="sec-title">典型使用场景</div>
            <div class="sec-sub">以下为典型业务场景示意，实际效果因项目复杂度与工程师专业判断而有所不同</div>
            <div class="case-grid">{cards_html}</div>
        </section>
        """,
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────
# 常见问题（FAQ）
# ─────────────────────────────────────────
def render_faq():
    faqs = [
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
    items_html = "".join(
        f"""<div class="faq-item">
            <div class="faq-q">Q：{q}</div>
            <div class="faq-a">{a}</div>
        </div>"""
        for q, a in faqs
    )
    st.markdown(
        f"""
        <section class="section sec-gray" id="faq">
            <div class="sec-title">常见问题</div>
            <div class="sec-sub">如有其他疑问，欢迎通过申请表单联系我们</div>
            <div class="faq-wrap">{items_html}</div>
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
        <div style="height:36px;background:linear-gradient(to bottom, var(--bg), #fff);"></div>
        <section id="contact" style="background:#fff; padding: 40px 5% 28px; text-align:center;">
            <div class="sec-title">申请免费试用</div>
            <div class="sec-sub" style="margin-bottom: 0;">
                无需安装，浏览器即可使用 · 支持私有化部署 · 数据安全可控<br>
                留下联系方式，我们将在 1 个工作日内与您联系
            </div>
        </section>
        <div style="height:28px;background:#fff;"></div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("apply_form", clear_on_submit=True):
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
                source="homepage",
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
                <a href="#advantages">核心优势</a>·
                <a href="#cases">特色功能</a>·
                <a href="#process">工作流程</a>·
                <a href="#contact">联系我们</a>
            </div>
            <div>✦ 新纪元数智 &nbsp;·&nbsp; AI驱动的工程咨询报告编制系统</div>
            <div style="margin-top:4px; font-size:12px;">
                © 2026 新纪元数智. All rights reserved. &nbsp;·&nbsp; 无需安装，浏览器即可使用 · 支持私有化部署
            </div>
            <div style="margin-top:6px; font-size:12px;">
                <a href="https://beian.miit.gov.cn/" target="_blank" rel="noopener noreferrer">京ICP备2026057726号</a>
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
    render_advantages()
    render_cases()
    render_process()
    render_scenarios()
    render_comparison()
    render_faq()
    render_contact()
    render_footer()


if __name__ == "__main__":
    main()
