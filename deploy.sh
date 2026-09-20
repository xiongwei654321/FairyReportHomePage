#!/bin/bash
# ================================================================
#  deploy.sh — 一键部署 Flask 应用到腾讯云 Ubuntu 服务器
#  本地执行：bash deploy.sh
#
#  ⚠️  安全提示：密码明文存于脚本，仅用于初次部署。
#  建议部署成功后改用 SSH 密钥认证并删除 REMOTE_PASS。
# ================================================================
set -euo pipefail

# ── 配置区（按需修改）────────────────────────────────────────────
REMOTE_IP="82.157.244.30"
REMOTE_USER="ubuntu"
REMOTE_PASS="Xw@635260316"       # ⚠️ 初次部署后建议改为密钥认证
REMOTE_DIR="/home/ubuntu/tech_inquire_web"
APP_PORT="8502"
SERVICE_NAME="flask-tech-inquire"
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

# 新装系统可能缺少 rsync（文件同步依赖它），先确保远端可用
_ssh "${REMOTE_USER}@${REMOTE_IP}" "sudo apt-get update -qq && sudo apt-get install -y rsync"

# 确保远端目录存在
_ssh "${REMOTE_USER}@${REMOTE_IP}" "mkdir -p ${REMOTE_DIR}"

_rsync -avz --progress --delete \
    --exclude='.git' \
    --exclude='.claude' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='*.DS_Store' \
    --exclude='venv' \
    --exclude='.venv' \
    --exclude='deploy.sh' \
    --exclude='applications.db' \
    --exclude='需求文档' \
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

# ── Step 3：停止旧 Streamlit 服务（如果存在）────────────────────
step "停止旧服务（如果存在）"

_ssh "${REMOTE_USER}@${REMOTE_IP}" bash <<STOPSSH
set -euo pipefail
# 停止旧 Streamlit 服务并删除 service 文件
for svc in streamlit-tech-inquire streamlit-tech-inquire-admin; do
    if systemctl is-active --quiet "\$svc" 2>/dev/null; then
        echo "  → 停止 \$svc"
        sudo systemctl stop "\$svc"
        sudo systemctl disable "\$svc"
    fi
    if [ -f "/etc/systemd/system/\${svc}.service" ]; then
        echo "  → 删除 \${svc}.service"
        sudo rm -f "/etc/systemd/system/\${svc}.service"
    fi
done
sudo systemctl daemon-reload
# 清理远端残留的旧 Streamlit 文件
rm -rf "${REMOTE_DIR}/pages" "${REMOTE_DIR}/admin.py" "${REMOTE_DIR}/.streamlit"
echo "✓ 旧服务与文件已清理"
STOPSSH

ok "旧服务已清理"

# ── Step 4：写入 systemd 服务并启动 ─────────────────────────────
step "配置 systemd 服务（${SERVICE_NAME}，端口 ${APP_PORT}）"

_ssh "${REMOTE_USER}@${REMOTE_IP}" bash <<SVCSSH
set -euo pipefail

sudo tee /etc/systemd/system/${SERVICE_NAME}.service > /dev/null <<UNIT
[Unit]
Description=Flask App - tech_inquire_web (port ${APP_PORT})
After=network.target

[Service]
Type=simple
User=${REMOTE_USER}
WorkingDirectory=${REMOTE_DIR}
ExecStart=${REMOTE_DIR}/venv/bin/gunicorn \\
    --bind 0.0.0.0:${APP_PORT} \\
    --workers 2 \\
    --timeout 120 \\
    app:app
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

# ── 完成提示 ────────────────────────────────────────────────────
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}  部署完成！${NC}"
echo "  官网地址：http://${REMOTE_IP}:${APP_PORT}"
echo "  管理后台：http://${REMOTE_IP}:${APP_PORT}/admin"
echo ""
echo "  常用远程命令："
echo "  查看日志：sshpass -p '${REMOTE_PASS}' ssh ${REMOTE_USER}@${REMOTE_IP} journalctl -u ${SERVICE_NAME} -f"
echo "  重启服务：sshpass -p '${REMOTE_PASS}' ssh ${REMOTE_USER}@${REMOTE_IP} sudo systemctl restart ${SERVICE_NAME}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
