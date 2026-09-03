import streamlit as st
from database import (
    init_db,
    get_applications,
    get_applications_count,
    update_application,
    delete_application,
)

PAGE_SIZE = 20

# 8 列比例：序号 | 姓名 | 手机号 | 公司 | 报告类型 | 提交时间 | 编辑 | 删除
_COLS = [0.5, 1.8, 2.2, 2.2, 4.0, 2.8, 1.1, 1.1]


# ─────────────────────────────────────────
# 页面配置
# ─────────────────────────────────────────
def set_page_config():
    st.set_page_config(
        page_title="新纪元数智 · 申请记录",
        page_icon="✦",
        layout="wide",
        initial_sidebar_state="collapsed",
    )


# ─────────────────────────────────────────
# 全局 CSS（与主站同一套设计语言）
# ─────────────────────────────────────────
def inject_global_css():
    st.markdown(
        """
        <style>
        /* ══════════════════════════════════════
           1. 隐藏 Streamlit 默认 UI
        ══════════════════════════════════════ */
        #MainMenu, footer, header,
        [data-testid="stToolbar"], [data-testid="stDecoration"],
        [data-testid="stStatusWidget"], [data-testid="collapsedControl"],
        .stDeployButton { display: none !important; }

        .main > div { padding: 0 !important; }
        .block-container {
            padding: 0 48px !important;
            max-width: 1280px !important;
            margin-left: auto !important;
            margin-right: auto !important;
        }
        @media (max-width: 768px) {
            .block-container { padding: 0 20px !important; }
        }
        section[data-testid="stSidebar"] { display: none !important; }

        [data-testid="stAppViewContainer"], [data-testid="stMain"],
        section[data-testid="stMain"], [data-testid="stMainBlockContainer"],
        [data-testid="stVerticalBlock"] { background: #fff !important; }
        [data-testid="stHorizontalBlock"] { background: transparent !important; }

        /* ══════════════════════════════════════
           2. 设计 Token
        ══════════════════════════════════════ */
        :root {
            --brand:      #1854FF;
            --brand-dk:   #1240CC;
            --brand-bg:   #EEF2FF;
            --teal:       #36CFC9;
            --teal-bg:    #E6FFFE;
            --dark:       #1D2129;
            --gray:       #6B7280;
            --gray-lt:    #9CA3AF;
            --border:     #E5E7EB;
            --bg:         #F7F8FA;
            --bg-hd:      #F1F3F9;   /* 表头用，比 --bg 深一档 */
            --danger:     #EF4444;
            --danger-lt:  #FECACA;
            --danger-bg:  #FEF2F2;
            --shadow-sm:  0 1px 3px rgba(0,0,0,.06);
        }

        /* ══════════════════════════════════════
           3. 全局基础
        ══════════════════════════════════════ */
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
        body, .stMarkdown {
            font-family: system-ui, -apple-system, "PingFang SC", "Noto Sans SC", sans-serif;
            color: var(--dark);
            background: #fff;
            -webkit-font-smoothing: antialiased;
        }

        /* ══════════════════════════════════════
           4. 导航栏
        ══════════════════════════════════════ */
        .nav {
            position: sticky; top: 0; z-index: 200;
            background: #fff; border-bottom: 1px solid var(--border);
            /* break out of block-container's 48px horizontal padding */
            margin-left: -48px;
            margin-right: -48px;
        }
        .nav-inner {
            max-width: 100%; margin: 0 auto;
            padding: 0 48px;
            display: flex; align-items: center;
            justify-content: space-between; height: 64px;
        }
        .nav-logo {
            font-size: 18px; font-weight: 700; color: var(--brand);
            letter-spacing: -0.3px; text-decoration: none;
        }
        .nav-back {
            font-size: 13px; color: var(--gray-lt);
            text-decoration: none; transition: color .15s;
            display: flex; align-items: center; gap: 5px;
            padding: 6px 12px; border-radius: 6px;
            border: 1px solid transparent;
            transition: all .15s;
        }
        .nav-back:hover {
            color: var(--brand);
            border-color: var(--brand-bg);
            background: var(--brand-bg);
        }
        @media (max-width: 768px) {
            .nav { margin-left: -20px; margin-right: -20px; }
            .nav-inner { padding: 0 20px; }
        }

        /* ══════════════════════════════════════
           5. 页面内容容器
        ══════════════════════════════════════ */
        .admin-body {
            padding: 40px 0 80px;
            width: 100%;
        }
        @media (max-width: 768px) { .admin-body { padding: 24px 0 60px; } }

        /* ══════════════════════════════════════
           6. 标题栏
        ══════════════════════════════════════ */
        .admin-header {
            display: flex; align-items: center; gap: 14px;
            margin-bottom: 20px;
        }
        .admin-title {
            font-size: clamp(20px, 2.5vw, 26px); font-weight: 700;
            color: var(--dark); letter-spacing: -0.4px;
        }
        .record-badge {
            font-size: 12px; color: var(--brand); background: var(--brand-bg);
            padding: 3px 10px; border-radius: 20px; font-weight: 500;
        }

        /* ══════════════════════════════════════
           7. 表格容器
        ══════════════════════════════════════ */
        .tbl-box {
            border: 1px solid var(--border);
            border-radius: 10px;
            overflow: hidden;
            box-shadow: var(--shadow-sm);
            margin-bottom: 20px;
        }

        /* ══════════════════════════════════════
           8. 表格头（强化背景）
        ══════════════════════════════════════ */
        .tbl-head {
            display: flex; align-items: center;
            background: var(--bg-hd);
            border-bottom: 1.5px solid var(--border);
            padding: 0 20px;
            height: 44px;
        }
        .th {
            font-size: 12px; font-weight: 600;
            color: var(--gray); letter-spacing: .3px; text-transform: uppercase;
            white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
        }
        .th:nth-child(1) { flex: 0.4;  min-width: 36px;  }
        .th:nth-child(2) { flex: 1.7;  min-width: 60px;  }
        .th:nth-child(3) { flex: 2.0;  min-width: 108px; }
        .th:nth-child(4) { flex: 2.0;  min-width: 80px;  }
        .th:nth-child(5) { flex: 3.8;  min-width: 120px; }
        .th:nth-child(6) { flex: 2.6;  min-width: 136px; }
        .th:nth-child(7) { flex: none; width: 156px; min-width: 156px; text-align: center; }

        /* ══════════════════════════════════════
           9. 行分隔线
        ══════════════════════════════════════ */
        .row-sep { height: 1px; background: var(--border); }

        /* ══════════════════════════════════════
           10. 数据行：垂直居中 + hover 高亮
        ══════════════════════════════════════ */
        [data-testid="stHorizontalBlock"]:has([data-testid="column"]:nth-child(8)) {
            align-items: center !important;
            padding: 0 20px !important;
            min-height: 52px;
            transition: background .1s;
        }
        [data-testid="stHorizontalBlock"]:has([data-testid="column"]:nth-child(8)):hover {
            background: #F5F7FF !important;
        }
        /* 编辑行：蓝色浅背景，不参与 hover */
        [data-testid="stHorizontalBlock"]:has([data-testid="column"]:nth-child(7)):not(:has([data-testid="column"]:nth-child(8))) {
            align-items: center !important;
            padding: 4px 20px !important;
            background: #F8F9FF !important;
        }

        /* ══════════════════════════════════════
           11. 单元格文本
        ══════════════════════════════════════ */
        .td-cell {
            font-size: 14px; color: var(--dark); line-height: 1.4;
            overflow: hidden; text-overflow: ellipsis;
            white-space: nowrap; display: block;
        }
        .td-id   { font-size: 12px; color: var(--gray-lt); line-height: 1.4; }
        .td-mono { font-variant-numeric: tabular-nums; letter-spacing: .4px; white-space: nowrap; }
        .td-time { font-size: 12px; color: var(--gray); white-space: nowrap; line-height: 1.4; }
        .td-warn { font-size: 13px; color: var(--danger); font-weight: 500; line-height: 1.4; }
        .td-del  { font-size: 14px; color: #C4C9D4; text-decoration: line-through; line-height: 1.4; }

        /* 删除确认行：浅红背景 */
        .row-del-bg [data-testid="stHorizontalBlock"] { background: var(--danger-bg) !important; }

        /* ══════════════════════════════════════
           12. 手机端适配（卡片式布局）
        ══════════════════════════════════════ */
        @media (max-width: 768px) {
            /* 隐藏桌面表头 */
            .tbl-head { display: none !important; }

            /* 普通数据行 & 删除确认行：改为卡片换行布局 */
            [data-testid="stHorizontalBlock"]:has([data-testid="column"]:nth-child(8)) {
                flex-wrap: wrap !important;
                padding: 10px 14px !important;
                min-height: unset !important;
                gap: 6px 0 !important;
                align-items: center !important;
            }
            /* 隐藏：序号(1)、公司(4)、报告类型(5)、提交时间(6) */
            [data-testid="stHorizontalBlock"]:has([data-testid="column"]:nth-child(8))
                [data-testid="column"]:nth-child(1),
            [data-testid="stHorizontalBlock"]:has([data-testid="column"]:nth-child(8))
                [data-testid="column"]:nth-child(4),
            [data-testid="stHorizontalBlock"]:has([data-testid="column"]:nth-child(8))
                [data-testid="column"]:nth-child(5),
            [data-testid="stHorizontalBlock"]:has([data-testid="column"]:nth-child(8))
                [data-testid="column"]:nth-child(6) {
                display: none !important;
            }
            /* 姓名(2)：左侧 55% */
            [data-testid="stHorizontalBlock"]:has([data-testid="column"]:nth-child(8))
                [data-testid="column"]:nth-child(2) {
                flex: 0 0 55% !important; width: 55% !important;
            }
            /* 手机号(3)：右侧 45% */
            [data-testid="stHorizontalBlock"]:has([data-testid="column"]:nth-child(8))
                [data-testid="column"]:nth-child(3) {
                flex: 0 0 45% !important; width: 45% !important;
            }
            /* 编辑(7)：下一行左侧 50% */
            [data-testid="stHorizontalBlock"]:has([data-testid="column"]:nth-child(8))
                [data-testid="column"]:nth-child(7) {
                flex: 0 0 50% !important; width: 50% !important;
            }
            /* 删除(8)：下一行右侧 50% */
            [data-testid="stHorizontalBlock"]:has([data-testid="column"]:nth-child(8))
                [data-testid="column"]:nth-child(8) {
                flex: 0 0 50% !important; width: 50% !important;
            }

            /* 编辑行（7列）：输入框换行卡片 */
            [data-testid="stHorizontalBlock"]:has([data-testid="column"]:nth-child(7)):not(:has([data-testid="column"]:nth-child(8))) {
                flex-wrap: wrap !important;
                padding: 8px 14px !important;
                gap: 6px 0 !important;
                align-items: center !important;
            }
            /* 隐藏编辑行序号(1) */
            [data-testid="stHorizontalBlock"]:has([data-testid="column"]:nth-child(7)):not(:has([data-testid="column"]:nth-child(8)))
                [data-testid="column"]:nth-child(1) {
                display: none !important;
            }
            /* 姓名输入(2)、手机号输入(3)：各 50% */
            [data-testid="stHorizontalBlock"]:has([data-testid="column"]:nth-child(7)):not(:has([data-testid="column"]:nth-child(8)))
                [data-testid="column"]:nth-child(2),
            [data-testid="stHorizontalBlock"]:has([data-testid="column"]:nth-child(7)):not(:has([data-testid="column"]:nth-child(8)))
                [data-testid="column"]:nth-child(3) {
                flex: 0 0 50% !important; width: 50% !important;
            }
            /* 公司输入(4)、报告类型输入(5)：各 50% */
            [data-testid="stHorizontalBlock"]:has([data-testid="column"]:nth-child(7)):not(:has([data-testid="column"]:nth-child(8)))
                [data-testid="column"]:nth-child(4),
            [data-testid="stHorizontalBlock"]:has([data-testid="column"]:nth-child(7)):not(:has([data-testid="column"]:nth-child(8)))
                [data-testid="column"]:nth-child(5) {
                flex: 0 0 50% !important; width: 50% !important;
            }
            /* 保存(6)、取消(7)：各 50% */
            [data-testid="stHorizontalBlock"]:has([data-testid="column"]:nth-child(7)):not(:has([data-testid="column"]:nth-child(8)))
                [data-testid="column"]:nth-child(6),
            [data-testid="stHorizontalBlock"]:has([data-testid="column"]:nth-child(7)):not(:has([data-testid="column"]:nth-child(8)))
                [data-testid="column"]:nth-child(7) {
                flex: 0 0 50% !important; width: 50% !important;
            }

            /* 文字样式 */
            .td-cell, .td-del { white-space: normal !important; font-size: 13px; }
            .td-mono { font-size: 13px; }
        }

        /* 手机表头（桌面隐藏） */
        .tbl-head-mobile {
            display: none;
        }
        @media (max-width: 768px) {
            .tbl-head-mobile {
                display: flex;
                align-items: center;
                background: var(--bg-hd);
                border-bottom: 1.5px solid var(--border);
                padding: 0 14px;
                height: 36px;
                font-size: 12px; font-weight: 600;
                color: var(--gray); letter-spacing: .3px;
            }
            .tbl-head-mobile .thm-name  { flex: 0 0 55%; }
            .tbl-head-mobile .thm-phone { flex: 0 0 45%; }
        }

        /* ══════════════════════════════════════
           13. 空状态
        ══════════════════════════════════════ */
        .empty-state {
            padding: 72px 0; text-align: center;
            color: var(--gray-lt); font-size: 14px;
        }

        /* ══════════════════════════════════════
           14. 分页
        ══════════════════════════════════════ */
        .page-info {
            text-align: center; font-size: 13px;
            color: var(--gray); line-height: 38px;
        }

        /* ══════════════════════════════════════
           15. 按钮系统
        ══════════════════════════════════════ */

        /* 基础：分页按钮（outlined brand） */
        [data-testid="stButton"] > button {
            background: #fff !important;
            color: var(--brand) !important;
            border: 1.5px solid var(--brand) !important;
            border-radius: 6px !important;
            font-size: 13px !important;
            font-weight: 500 !important;
            padding: 7px 18px !important;
            transition: all .15s !important;
            box-shadow: none !important;
            width: 100% !important;
        }
        [data-testid="stButton"] > button:hover {
            background: var(--brand-bg) !important;
        }

        /* 禁用态：完全灰化，禁止 hover 变色 */
        [data-testid="stButton"] > button:disabled,
        [data-testid="stButton"] > button:disabled:hover {
            opacity: 1 !important;
            cursor: not-allowed !important;
            background: var(--bg) !important;
            color: #D1D5DB !important;
            border-color: var(--border) !important;
        }

        /* 保存（primary = 实心蓝） */
        [data-testid="stButton"] > button[kind="primary"] {
            background: var(--brand) !important;
            color: #fff !important;
            border-color: var(--brand) !important;
        }
        [data-testid="stButton"] > button[kind="primary"]:hover {
            background: var(--brand-dk) !important;
        }

        /* 编辑按钮（8列行第7列）：蓝色 pill */
        [data-testid="stHorizontalBlock"]:has([data-testid="column"]:nth-child(8))
            [data-testid="column"]:nth-child(7) [data-testid="stButton"] > button {
            background: var(--brand-bg) !important;
            color: var(--brand) !important;
            border: 1px solid transparent !important;
            border-radius: 4px !important;
            font-size: 12px !important;
            font-weight: 500 !important;
            padding: 4px 10px !important;
            white-space: nowrap !important;
            line-height: 1.6 !important;
        }
        [data-testid="stHorizontalBlock"]:has([data-testid="column"]:nth-child(8))
            [data-testid="column"]:nth-child(7) [data-testid="stButton"] > button:hover {
            background: var(--brand) !important;
            color: #fff !important;
        }

        /* 删除按钮（8列行第8列）：红色风险样式 */
        [data-testid="stHorizontalBlock"]:has([data-testid="column"]:nth-child(8))
            [data-testid="column"]:nth-child(8) [data-testid="stButton"] > button {
            background: var(--danger-bg) !important;
            color: var(--danger) !important;
            border: 1px solid var(--danger-lt) !important;
            border-radius: 4px !important;
            font-size: 12px !important;
            font-weight: 500 !important;
            padding: 4px 10px !important;
            white-space: nowrap !important;
            line-height: 1.6 !important;
        }
        [data-testid="stHorizontalBlock"]:has([data-testid="column"]:nth-child(8))
            [data-testid="column"]:nth-child(8) [data-testid="stButton"] > button:hover {
            background: var(--danger) !important;
            color: #fff !important;
            border-color: var(--danger) !important;
        }

        /* 取消按钮（7列编辑行第7列）：灰色 outlined */
        [data-testid="stHorizontalBlock"]:has([data-testid="column"]:nth-child(7)):not(:has([data-testid="column"]:nth-child(8)))
            [data-testid="column"]:nth-child(7) [data-testid="stButton"] > button {
            background: #fff !important;
            color: var(--gray) !important;
            border: 1.5px solid var(--border) !important;
            font-size: 13px !important;
            padding: 6px 14px !important;
        }
        [data-testid="stHorizontalBlock"]:has([data-testid="column"]:nth-child(7)):not(:has([data-testid="column"]:nth-child(8)))
            [data-testid="column"]:nth-child(7) [data-testid="stButton"] > button:hover {
            background: var(--bg) !important;
        }

        /* ══════════════════════════════════════
           16. 编辑行输入框
        ══════════════════════════════════════ */
        [data-testid="stTextInput"] { margin-bottom: 0 !important; }
        [data-testid="stTextInput"] > div > div {
            padding-top: 5px !important; padding-bottom: 5px !important;
        }

        /* ══════════════════════════════════════
           17. 页脚
        ══════════════════════════════════════ */
        .site-footer {
            background: var(--dark); color: var(--gray-lt);
            text-align: center; padding: 32px 48px;
            font-size: 13px; line-height: 2;
        }
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
            <div class="nav-inner">
                <a class="nav-logo" href="#">✦ 新纪元数智</a>
                <a class="nav-back" href="http://119.45.38.169:8502" target="_blank">← 返回官网</a>
            </div>
        </nav>
        """,
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────
# 辅助：渲染普通行
# ─────────────────────────────────────────
def _normal_row(r, row_num):
    id_, name, phone, company, report_type, source, created_at = r

    c = st.columns(_COLS)
    with c[0]: st.markdown(f'<p class="td-id">{row_num}</p>', unsafe_allow_html=True)
    with c[1]: st.markdown(f'<p class="td-cell">{name}</p>', unsafe_allow_html=True)
    with c[2]: st.markdown(f'<p class="td-cell td-mono">{phone}</p>', unsafe_allow_html=True)
    with c[3]: st.markdown(f'<p class="td-cell">{company or "—"}</p>', unsafe_allow_html=True)
    with c[4]: st.markdown(f'<p class="td-cell">{report_type or "—"}</p>', unsafe_allow_html=True)
    with c[5]: st.markdown(f'<p class="td-time">{created_at}</p>', unsafe_allow_html=True)
    with c[6]:
        if st.button("编辑", key=f"edit_{id_}", use_container_width=True):
            st.session_state.edit_id = id_
            st.session_state.confirm_id = None
            st.rerun()
    with c[7]:
        if st.button("删除", key=f"del_{id_}", use_container_width=True):
            st.session_state.confirm_id = id_
            st.session_state.edit_id = None
            st.rerun()


# ─────────────────────────────────────────
# 辅助：渲染编辑行
# ─────────────────────────────────────────
def _edit_row(r, row_num):
    id_, name, phone, company, report_type, source, created_at = r

    st.markdown('<div class="row-edit-bg">', unsafe_allow_html=True)
    c = st.columns([0.5, 1.8, 2.0, 2.0, 4.0, 1.5, 1.5])
    with c[0]: st.markdown(f'<p class="td-id">{row_num}</p>', unsafe_allow_html=True)
    with c[1]: new_name    = st.text_input("", value=name,        key=f"n_{id_}",  label_visibility="collapsed")
    with c[2]: new_phone   = st.text_input("", value=phone,       key=f"p_{id_}",  label_visibility="collapsed")
    with c[3]: new_company = st.text_input("", value=company,     key=f"c_{id_}",  label_visibility="collapsed")
    with c[4]: new_rt      = st.text_input("", value=report_type, key=f"rt_{id_}", label_visibility="collapsed")
    with c[5]:
        if st.button("保存", key=f"save_{id_}", type="primary", use_container_width=True):
            update_application(id_, new_name.strip(), new_phone.strip(),
                               new_company.strip(), new_rt.strip())
            st.session_state.edit_id = None
            st.rerun()
    with c[6]:
        if st.button("取消", key=f"cancel_{id_}", use_container_width=True):
            st.session_state.edit_id = None
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────
# 辅助：渲染删除确认行
# ─────────────────────────────────────────
def _confirm_row(r, row_num):
    id_, name, phone, company, report_type, source, created_at = r

    st.markdown('<div class="row-del-bg">', unsafe_allow_html=True)
    c = st.columns(_COLS)
    with c[0]: st.markdown(f'<p class="td-id">{row_num}</p>',             unsafe_allow_html=True)
    with c[1]: st.markdown(f'<p class="td-del">{name}</p>',               unsafe_allow_html=True)
    with c[2]: st.markdown(f'<p class="td-del td-mono">{phone}</p>',      unsafe_allow_html=True)
    with c[3]: st.markdown(f'<p class="td-del">{company or "—"}</p>',     unsafe_allow_html=True)
    with c[4]: st.markdown(f'<p class="td-del">{report_type or "—"}</p>', unsafe_allow_html=True)
    with c[5]: st.markdown('<p class="td-warn">确认删除？</p>',            unsafe_allow_html=True)
    with c[6]:
        if st.button("确认", key=f"confirm_{id_}", use_container_width=True):
            delete_application(id_)
            st.session_state.confirm_id = None
            st.rerun()
    with c[7]:
        if st.button("取消", key=f"cncl_{id_}", use_container_width=True):
            st.session_state.confirm_id = None
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────
# 主表格（含分页）
# ─────────────────────────────────────────
def render_table():
    total = get_applications_count()
    total_pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)

    for key in ("page", "edit_id", "confirm_id"):
        if key not in st.session_state:
            st.session_state[key] = 1 if key == "page" else None

    st.session_state.page = max(1, min(st.session_state.page, total_pages))
    offset = (st.session_state.page - 1) * PAGE_SIZE
    rows   = get_applications(offset=offset, limit=PAGE_SIZE)

    st.markdown('<div class="admin-body">', unsafe_allow_html=True)

    # 标题栏
    st.markdown(
        f"""
        <div class="admin-header">
            <span class="admin-title">申请记录</span>
            <span class="record-badge">共 {total} 条</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not rows:
        st.markdown('<div class="empty-state">暂无申请记录</div>', unsafe_allow_html=True)
    else:
        # ── 表格容器开始 ──
        st.markdown('<div class="tbl-box">', unsafe_allow_html=True)

        # 表头
        st.markdown(
            """
            <div class="tbl-head">
                <span class="th">序号</span>
                <span class="th">姓名</span>
                <span class="th">手机号</span>
                <span class="th">公司</span>
                <span class="th">报告类型</span>
                <span class="th">提交时间</span>
                <span class="th">操作</span>
            </div>
            <div class="tbl-head-mobile">
                <span class="thm-name">姓名</span>
                <span class="thm-phone">手机号</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # 数据行
        edit_id    = st.session_state.edit_id
        confirm_id = st.session_state.confirm_id

        for i, r in enumerate(rows):
            if i > 0:
                st.markdown('<div class="row-sep"></div>', unsafe_allow_html=True)
            id_      = r[0]
            row_num  = i + 1   # 每页从 1 开始的本地行号
            if edit_id == id_:
                _edit_row(r, row_num)
            elif confirm_id == id_:
                _confirm_row(r, row_num)
            else:
                _normal_row(r, row_num)

        st.markdown('</div>', unsafe_allow_html=True)  # tbl-box 结束

    # 分页控件
    st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)
    c_prev, c_info, c_next = st.columns([1, 3, 1])
    with c_prev:
        if st.button("← 上一页", disabled=(st.session_state.page <= 1),
                     use_container_width=True):
            st.session_state.page -= 1
            st.rerun()
    with c_info:
        st.markdown(
            f'<div class="page-info">第 {st.session_state.page} 页 &nbsp;/&nbsp; 共 {total_pages} 页</div>',
            unsafe_allow_html=True,
        )
    with c_next:
        if st.button("下一页 →", disabled=(st.session_state.page >= total_pages),
                     use_container_width=True):
            st.session_state.page += 1
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)  # admin-body 结束


# ─────────────────────────────────────────
# 页脚
# ─────────────────────────────────────────
def render_footer():
    st.markdown(
        """
        <footer class="site-footer">
            <div>✦ 新纪元数智 &nbsp;·&nbsp; AI驱动的工程咨询报告编制系统</div>
            <div style="margin-top:4px; font-size:12px;">
                © 2026 新纪元数智. All rights reserved.
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
    render_table()
    render_footer()


if __name__ == "__main__":
    main()
