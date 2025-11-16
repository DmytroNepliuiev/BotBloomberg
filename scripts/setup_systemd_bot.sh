#!/bin/bash
set -e

SERVICE_NAME="contract-bot"
PROJECT_DIR="/home/ec2-user/contract-app"
VENV_PATH="$PROJECT_DIR/venv/bin/python"
BOT_PATH="$PROJECT_DIR/bot/bot.py"

echo "=== Creating systemd service for Discord bot ==="

sudo bash -c "cat > /etc/systemd/system/$SERVICE_NAME.service" <<EOF
[Unit]
Description=Discord Contract Bot
After=network.target

[Service]
User=ec2-user
WorkingDirectory=$PROJECT_DIR
ExecStart=$VENV_PATH $BOT_PATH
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

echo "=== Reloading systemd ==="
sudo systemctl daemon-reload

echo "=== Enabling bot service ==="
sudo systemctl enable $SERVICE_NAME

echo "=== Starting bot ==="
sudo systemctl start $SERVICE_NAME

echo "=== Bot service installed and started ==="
