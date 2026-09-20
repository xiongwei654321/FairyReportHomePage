# FairyReportHomePage — 项目说明

## 项目概述

**需求文档（FairyReport）** 的官网落地页，用于产品展示与试用申请收集。
这是一个 Flask 应用，对外表现为极简商务风格的产品官网，并通过 SQLite 存储访客申请信息。

产品本身（非本仓库）是一个面向中国工程咨询行业的 AI 报告编制系统，覆盖 14 种法定报告类型。

---

## 技术栈

| 层次 | 技术 |
|------|------|
| 框架 | Python + Flask >= 3.0.0 |
| 数据库 | SQLite（本地文件 `applications.db`） |
| 前端样式 | 纯 CSS（独立 .css 文件） + Jinja2 模板 |
| JS | 原生 JavaScript（汉堡菜单 + Tooltip） |
| 部署 | 腾讯云 Ubuntu，gunicorn + systemd 服务，端口 8502 |

---

## 目录结构

```
FairyReportHomePage/
├── app.py                          # Flask 应用入口 + 路由
├── database.py                     # SQLite CRUD
├── requirements.txt                # flask, gunicorn
├── deploy.sh                       # 一键部署脚本（rsync + systemd）
├── applications.db                 # 运行时生成，存储申请记录
├── static/
│   ├── css/
│   │   ├── base.css                # 公共样式：CSS 变量、reset、导航、表单、页脚
│   │   ├── home.css                # 首页专属：优势卡片、流程、对比表、FAQ
│   │   ├── trial.css               # 体验页专属：统计栏、模块卡片
│   │   └── admin.css               # 管理后台专属：表格、按钮、分页
│   └── js/
│       └── main.js                 # 汉堡菜单 + 优势卡片 tooltip
├── templates/
│   ├── base.html                   # HTML 骨架（head、block 定义）
│   ├── base_public.html            # 继承 base，加载公共导航 + 页脚 + JS
│   ├── components/
│   │   ├── nav_public.html         # 公共导航栏（参数化链接）
│   │   ├── nav_admin.html          # 管理后台导航
│   │   ├── footer_public.html      # 公共页脚
│   │   ├── footer_admin.html       # 管理后台页脚
│   │   └── contact_form.html       # 共享申请表单（参数化标题和来源）
│   ├── home.html                   # 首页（extends base_public）
│   ├── trial.html                  # 体验页（extends base_public）
│   └── admin.html                  # 管理后台（extends base）
└── 需求文档/                       # 产品参考资料（不部署）
    ├── AI驱动的工程咨询报告编制系统.md
    ├── 修改建议.md
    └── *.pdf / *.docx
```

---

## 路由

| 路由 | 方法 | 用途 |
|------|------|------|
| `/` | GET | 首页 |
| `/trial` | GET | 体验页 |
| `/submit` | POST | 表单提交（首页 + 体验页共用） |
| `/admin` | GET | 管理后台（query params: page, edit_id, confirm_id） |
| `/admin/update` | POST | 保存编辑记录 |
| `/admin/delete` | POST | 删除记录 |

---

## 页面结构

### 首页 `/`

渲染顺序（`templates/home.html`）：

1. 导航栏（带移动端汉堡菜单）
2. 首屏 Hero，主 slogan + CTA 按钮
3. 核心优势（4 列卡片，桌面/移动端悬浮 tooltip）
4. 六大特色功能（3 列卡片）
5. 五步工作流程（横向步骤 + 连接线）
6. 典型使用场景（3 列案例卡片）
7. 对比表（与通用 AI 差异化）
8. 常见问题（FAQ）
9. 申请免费试用表单（原生 HTML form → SQLite）
10. 深色页脚

### 体验页 `/trial`

渲染顺序（`templates/trial.html`）：导航栏 → Hero → 数据统计栏 → 报告模块卡片（7个）→ 申请表单 → 页脚

### 管理后台 `/admin`

渲染顺序（`templates/admin.html`）：导航栏 → 标题栏 → 数据表格（含编辑/删除行内操作）→ 分页 → 页脚

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

**设计风格**：极简留白，商务干净，无渐变、无弹窗、无复杂动效。

---

## 本地运行

```bash
pip install flask gunicorn
python app.py
```

访问 `http://localhost:8502`

---

## 部署

```bash
bash deploy.sh
```

脚本执行步骤：
1. 通过 `rsync` 同步文件到腾讯云服务器（排除 `.git`、`venv`、`deploy.sh` 等）
2. 远程创建 Python venv 并安装依赖
3. 停止旧 Streamlit 服务（如果存在）
4. 写入 gunicorn systemd 服务文件并启动

**服务信息**：
- 服务名：`flask-tech-inquire`
- 端口：`8502`
- 远程目录：`/home/ubuntu/tech_inquire_web`

> 注意：`deploy.sh` 中含明文密码，仅用于初次部署，建议部署后切换为 SSH 密钥认证。

---

## 待办改进方向（来自需求文档/修改建议.md）

- [x] 补充与通用大模型的差异化对比
- [x] 添加脱敏后的落地案例
- [x] 页面底部增加常见问题（FAQ）模块
- [ ] 为产品考虑中文品牌名称
