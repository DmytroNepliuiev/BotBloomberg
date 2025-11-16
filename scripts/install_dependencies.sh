#!/bin/bash
set -e

echo "=== Updating system ==="
sudo dnf update -y

echo "=== Installing Python 3.12 & tools ==="
sudo dnf install -y python3.12 python3.12-pip python3.12-devel git

echo "=== Creating main project folders ==="
mkdir -p /home/ec2-user/contract-app
cd /home/ec2-user/contract-app

echo "=== Creating Python venv ==="
python3.12 -m venv venv
source venv/bin/activate

echo "=== Installing project requirements ==="
if [ -f "requirements.txt" ]; then
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo "requirements.txt NOT FOUND! Upload it first."
fi

echo "=== Installation finished successfully ==="
