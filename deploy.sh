#!/bin/bash
# ================================================================
#  deploy.sh — 一键部署 Streamlit 应用到腾讯云 Ubuntu 服务器
#  本地执行：bash deploy.sh
#
#  ⚠️  安全提示：密码明文存于脚本，仅用于初次部署。
#  建议部署成功后改用 SSH 密钥认证并删除 REMOTE_PASS。
# ================================================================
set -euo pipefail

# ── 配置区（按需修改）────────────────────────────────────────────
REMOTE_IP="119.45.38.169"
REMOTE_USER="ubuntu"
REMOTE_PASS="Xw123456"          # ⚠️ 初次部署后建议改为密钥认证
REMOTE_DIR="/home/ubuntu/tech_inquire_web"
APP_PORT="8502"
SERVICE_NAME="streamlit-tech-inquire"
ADMIN_PORT="8503"
ADMIN_SERVICE_NAME="streamlit-tech-inquire-admin"
# ────────────────────────────────────────────────────────────────

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m'

step() { echo -e "\n${BLUE}▶ $1${NC}"; }
ok()   { echo -e "${GREEN}✓ $1${NC}"; }
warn() { echo -e "${YELLOW}⚠ $1${NC}"; }

# ssh / rsync 的公共选项（跳过首次连接的主机指纹确认）
SSH_OPTS="-o StrictHostKeyChecking=no -o LogLevel=ERROR"

# 带密码的 ssh / rsync 包装
_ssh()   { sshpass -p "$REMOTE_PASS" ssh   $SSH_OPTS "$@"; }
_rsync() { sshpass -p "$REMOTE_PASS" rsync -e "ssh $SSH_OPTS" "$@"; }

# ── Step 0：检查 sshpass（macOS 需通过 Homebrew 安装）───────────
step "检查本地依赖：sshpass"

if ! command -v sshpass &>/dev/null; then
    warn "未检测到 sshpass，正在通过 Homebrew 安装..."
    if ! command -v brew &>/dev/null; then
        echo "错误：未找到 Homebrew，请先安装：https://brew.sh" >&2
        exit 1
    fi
    brew install hudochenkov/sshpass/sshpass
fi
ok "sshpass 已就绪"

# ── Step 1：同步项目文件 ─────────────────────────────────────────
step "同步项目文件到服务器 ${REMOTE_USER}@${REMOTE_IP}:${REMOTE_DIR}"

# 确保远端目录存在
_ssh "${REMOTE_USER}@${REMOTE_IP}" "mkdir -p ${REMOTE_DIR}"

_rsync -avz --progress \
    --exclude='.git' \
    --exclude='.claude' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='*.DS_Store' \
    --exclude='venv' \
    --exclude='deploy.sh' \
    ./ "${REMOTE_USER}@${REMOTE_IP}:${REMOTE_DIR}/"

ok "文件同步完成"

# ── Step 2：远程初始化 Python 环境 ───────────────────────────────
step "初始化远程 Python 虚拟环境并安装依赖"

_ssh "${REMOTE_USER}@${REMOTE_IP}" bash <<ENVSSH
set -euo pipefail

echo "  → 安装 python3-venv..."
sudo apt-get update -qq
sudo apt-get install -y python3 python3-pip python3-venv

echo "  → 创建虚拟环境..."
cd "${REMOTE_DIR}"
[ ! -d "venv" ] && python3 -m venv venv

echo "  → 安装 Python 依赖..."
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q

echo "✓ Python 环境就绪"
ENVSSH

ok "依赖安装完成"

# ── Step 3：写入 systemd 服务并启动 ─────────────────────────────
step "配置 systemd 服务（${SERVICE_NAME}，端口 ${APP_PORT}）"

_ssh "${REMOTE_USER}@${REMOTE_IP}" bash <<SVCSSH
set -euo pipefail

sudo tee /etc/systemd/system/${SERVICE_NAME}.service > /dev/null <<UNIT
[Unit]
Description=Streamlit App - tech_inquire_web (port ${APP_PORT})
After=network.target

[Service]
Type=simple
User=${REMOTE_USER}
WorkingDirectory=${REMOTE_DIR}
ExecStart=${REMOTE_DIR}/venv/bin/streamlit run app.py \\
    --server.port ${APP_PORT} \\
    --server.address 0.0.0.0 \\
    --server.headless true \\
    --server.enableCORS false \\
    --server.enableXsrfProtection false
Restart=on-failure
RestartSec=5s
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
UNIT

sudo systemctl daemon-reload
sudo systemctl enable "${SERVICE_NAME}"
sudo systemctl restart "${SERVICE_NAME}"

sleep 2
echo ""
echo "── 服务状态 ──────────────────────────────"
systemctl status "${SERVICE_NAME}" --no-pager -l || true
SVCSSH

ok "systemd 服务已启动"

# ── Step 4：写入 Admin systemd 服务并启动 ────────────────────────
step "配置 Admin 服务（${ADMIN_SERVICE_NAME}，端口 ${ADMIN_PORT}）"

_ssh "${REMOTE_USER}@${REMOTE_IP}" bash <<ADMINSSH
set -euo pipefail

sudo tee /etc/systemd/system/${ADMIN_SERVICE_NAME}.service > /dev/null <<UNIT
[Unit]
Description=Streamlit Admin - tech_inquire_web (port ${ADMIN_PORT})
After=network.target

[Service]
Type=simple
User=${REMOTE_USER}
WorkingDirectory=${REMOTE_DIR}
ExecStart=${REMOTE_DIR}/venv/bin/streamlit run admin.py \\
    --server.port ${ADMIN_PORT} \\
    --server.address 0.0.0.0 \\
    --server.headless true \\
    --server.enableCORS false \\
    --server.enableXsrfProtection false
Restart=on-failure
RestartSec=5s
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
UNIT

sudo systemctl daemon-reload
sudo systemctl enable "${ADMIN_SERVICE_NAME}"
sudo systemctl restart "${ADMIN_SERVICE_NAME}"

sleep 2
echo ""
echo "── Admin 服务状态 ──────────────────────────"
systemctl status "${ADMIN_SERVICE_NAME}" --no-pager -l || true
ADMINSSH

ok "Admin 服务已启动"

# ── 完成提示 ────────────────────────────────────────────────────
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}  部署完成！${NC}"
echo "  官网地址：http://${REMOTE_IP}:${APP_PORT}"
echo "  管理后台：http://${REMOTE_IP}:${ADMIN_PORT}"
echo ""
echo "  常用远程命令："
echo "  查看官网日志：sshpass -p '${REMOTE_PASS}' ssh ${REMOTE_USER}@${REMOTE_IP} journalctl -u ${SERVICE_NAME} -f"
echo "  查看后台日志：sshpass -p '${REMOTE_PASS}' ssh ${REMOTE_USER}@${REMOTE_IP} journalctl -u ${ADMIN_SERVICE_NAME} -f"
echo "  重启官网服务：sshpass -p '${REMOTE_PASS}' ssh ${REMOTE_USER}@${REMOTE_IP} sudo systemctl restart ${SERVICE_NAME}"
echo "  重启后台服务：sshpass -p '${REMOTE_PASS}' ssh ${REMOTE_USER}@${REMOTE_IP} sudo systemctl restart ${ADMIN_SERVICE_NAME}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
