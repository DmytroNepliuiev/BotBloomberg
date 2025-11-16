#!/bin/bash
set -e

PROJECT_DIR="/home/ec2-user/contract-app"

echo "=== Pulling latest code ==="
cd $PROJECT_DIR
git pull

echo "=== Activating venv ==="
source venv/bin/activate

if [ -f "requirements.txt" ]; then
  echo "=== Updating Python packages ==="
  pip install -r requirements.txt
fi

echo "=== Restarting systemd services ==="
sudo systemctl restart contract-api
sudo systemctl restart contract-bot

echo "=== Update finished successfully ==="
