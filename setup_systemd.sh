#!/bin/bash
# Setup script for Lotto Max Prediction as Systemd Service

set -e

SCRIPT_DIR="/home/eva/workspace/My_lotto_project"
SERVICE_NAME="lotto-predictor"
SERVICE_FILE="${SCRIPT_DIR}/lotto-predictor.service"
SYSTEMD_DIR="/etc/systemd/system"

echo "=================================="
echo "Lotto Max Systemd Service Setup"
echo "=================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ This script must be run with sudo privileges"
    echo "Run: sudo bash setup_systemd.sh"
    exit 1
fi

# Check if service file exists
if [ ! -f "$SERVICE_FILE" ]; then
    echo "❌ Service file not found: $SERVICE_FILE"
    exit 1
fi

echo ""
echo "📋 Step 1: Installing service file..."
cp "$SERVICE_FILE" "$SYSTEMD_DIR/"
echo "✓ Service file copied to $SYSTEMD_DIR"

echo ""
echo "📋 Step 2: Reloading systemd daemon..."
systemctl daemon-reload
echo "✓ Systemd daemon reloaded"

echo ""
echo "📋 Step 3: Enabling service to start on boot..."
systemctl enable "$SERVICE_NAME"
echo "✓ Service enabled (will start on boot)"

echo ""
echo "📋 Step 4: Starting service..."
systemctl start "$SERVICE_NAME"
echo "✓ Service started"

echo ""
echo "=================================="
echo "✅ Setup Complete!"
echo "=================================="
echo ""
echo "📊 Service Status:"
systemctl status "$SERVICE_NAME" --no-pager

echo ""
echo "📝 Useful Commands:"
echo "  • View logs:        sudo journalctl -u $SERVICE_NAME -f"
echo "  • Check status:     sudo systemctl status $SERVICE_NAME"
echo "  • Stop service:     sudo systemctl stop $SERVICE_NAME"
echo "  • Start service:    sudo systemctl start $SERVICE_NAME"
echo "  • Restart service:  sudo systemctl restart $SERVICE_NAME"
echo "  • Disable on boot:  sudo systemctl disable $SERVICE_NAME"
echo ""
