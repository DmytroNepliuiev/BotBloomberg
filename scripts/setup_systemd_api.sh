#!/bin/bash
set -e

SERVICE_NAME="contract-api"
PROJECT_DIR="/home/ec2-user/contract-app"
VENV_PATH="$PROJECT_DIR/venv/bin/python"
UVICORN_PATH="$PROJECT_DIR/venv/bin/uvicorn"
API_PATH="backend.main:app"   # main.py → app = FastAPI()

echo "=== Creating systemd service for FastAPI ==="

sudo bash -c "cat > /etc/systemd/system/$SERVICE_NAME.service" <<EOF
[Unit]
Description=Contract API Server
After=network.target

[Service]
User=ec2-user
WorkingDirectory=$PROJECT_DIR
ExecStart=$UVICORN_PATH $API_PATH --host 0.0.0.0 --port 8000 --workers 2
Restart=always

[Install]
WantedBy=multi-user.target
EOF

echo "=== Reloading systemd ==="
sudo systemctl daemon-reload

echo "=== Enabling API service ==="
sudo systemctl enable $SERVICE_NAME

echo "=== Starting API ==="
sudo systemctl start $SERVICE_NAME

echo "=== API service installed and started ==="
