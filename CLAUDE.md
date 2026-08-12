# FairyReportHomePage — 项目说明

## 项目概述

**需求文档（FairyReport）** 的官网落地页，用于产品展示与试用申请收集。
这是一个 Streamlit 多页应用，对外表现为极简商务风格的产品官网，并通过 SQLite 存储访客申请信息。

产品本身（非本仓库）是一个面向中国工程咨询行业的 AI 报告编制系统，覆盖 14 种法定报告类型。

---

## 技术栈

| 层次 | 技术 |
|------|------|
| 框架 | Python + Streamlit >= 1.35.0 |
| 数据库 | SQLite（本地文件 `applications.db`） |
| 前端样式 | 纯 CSS（通过 `st.markdown(unsafe_allow_html=True)` 注入） |
| 部署 | 腾讯云 Ubuntu，systemd 服务，端口 8502 |

---

## 目录结构

```
FairyReportHomePage/
├── app.py               # 首页（主入口）
├── database.py          # SQLite 数据库操作
├── requirements.txt     # 依赖：streamlit>=1.35.0
├── deploy.sh            # 一键部署脚本（rsync + systemd）
├── applications.db      # 运行时生成，存储申请记录
├── pages/
│   └── trial.py         # /trial 子页：选择报告类型 + 申请表单
└── 需求文档/             # 产品参考资料（不部署）
    ├── AI驱动的工程咨询报告编制系统.md
    ├── 修改建议.md
    └── *.pdf / *.docx
```

---

## 页面结构

### 首页 `app.py`

渲染顺序：

1. `render_nav()` — 顶部粘性导航栏（带移动端汉堡菜单）
2. `render_hero()` — 首屏 Hero，主 slogan + CTA 按钮
3. `render_advantages()` — 核心优势（4 列卡片，桌面/移动端悬浮 tooltip）
4. `render_cases()` — 六大特色功能（3 列卡片）
5. `render_process()` — 五步工作流程（横向步骤 + 连接线）
6. `render_contact()` — 申请免费试用表单（Streamlit 原生 form → SQLite）
7. `render_footer()` — 深色页脚

### 体验页 `pages/trial.py`（路由 `/trial`）

渲染顺序：导航栏 → Hero → 数据统计栏 → 报告模块卡片（7个）→ 申请表单 → 页脚

---

## 数据库

**文件**：`applications.db`（SQLite，与 `app.py` 同级目录）

**表**：`applications`

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增 |
| name | TEXT NOT NULL | 姓名 |
| phone | TEXT NOT NULL | 手机号 |
| company | TEXT | 公司（选填） |
| report_type | TEXT | 报告类型（选填） |
| source | TEXT | 来源：`homepage` 或 `trial` |
| created_at | TEXT | 提交时间，格式 `YYYY-MM-DD HH:MM:SS` |

---

## 品牌设计规范

```css
--brand:    #1854FF   /* 主品牌蓝 */
--brand-dk: #1240CC   /* 悬停深蓝 */
--brand-bg: #EEF2FF   /* 蓝色浅背景 */
--teal:     #36CFC9   /* 辅助青色 */
--dark:     #1D2129   /* 深色文字 */
--gray:     #6B7280   /* 次要文字 */
--border:   #E5E7EB   /* 边框 */
--bg:       #F7F8FA   /* 浅灰背景块 */
```

**字体**：`system-ui, -apple-system, "PingFang SC", "Noto Sans SC", sans-serif`

**设计风格**：极简留白，商务干净，无渐变、无弹窗、无复杂动效。Streamlit 默认 UI 元素（工具栏、侧边栏等）全部通过 CSS 隐藏。

---

## 本地运行

```bash
pip install streamlit>=1.35.0
streamlit run app.py
```

---

## 部署

```bash
bash deploy.sh
```

脚本执行步骤：
1. 通过 `rsync` 同步文件到腾讯云服务器（排除 `.git`、`venv`、`deploy.sh` 等）
2. 远程创建 Python venv 并安装依赖
3. 写入 systemd 服务文件并启动

**服务信息**：
- 服务名：`streamlit-tech-inquire`
- 端口：`8502`
- 远程目录：`/home/ubuntu/tech_inquire_web`

> 注意：`deploy.sh` 中含明文密码，仅用于初次部署，建议部署后切换为 SSH 密钥认证。

---

## 待办改进方向（来自需求文档/修改建议.md）

- [ ] 补充与通用大模型的差异化对比
- [ ] 添加脱敏后的落地案例
- [ ] 页面底部增加常见问题（FAQ）模块
- [ ] 为产品考虑中文品牌名称
