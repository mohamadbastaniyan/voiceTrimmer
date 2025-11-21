#!/bin/bash
# Deploy script for Voice Trimmer Bot to Ubuntu Server

set -e

echo "🚀 Voice Trimmer Bot - Deployment Script"
echo "========================================"
echo ""

# Variables (customize these)
BOT_USER="ubuntu"
BOT_HOME="/home/$BOT_USER/voiceTrimmer"
BOT_TOKEN="${TELEGRAM_BOT_TOKEN}"
SERVICE_NAME="voice-trimmer-bot"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ This script must be run as root (use sudo)"
    exit 1
fi

echo "📝 Deployment Configuration:"
echo "   User: $BOT_USER"
echo "   Home: $BOT_HOME"
echo "   Service: $SERVICE_NAME"
echo ""

# Update system
echo "1️⃣  Updating system packages..."
apt-get update
apt-get upgrade -y

# Install dependencies
echo "2️⃣  Installing dependencies..."
apt-get install -y python3 python3-pip python3-venv ffmpeg git

# Create bot directory
echo "3️⃣  Setting up bot directory..."
if [ ! -d "$BOT_HOME" ]; then
    mkdir -p "$BOT_HOME"
    git clone <repository-url> "$BOT_HOME" || echo "Manual setup required"
fi

chown -R "$BOT_USER:$BOT_USER" "$BOT_HOME"

# Setup Python environment
echo "4️⃣  Setting up Python virtual environment..."
cd "$BOT_HOME"
sudo -u "$BOT_USER" python3 -m venv venv
sudo -u "$BOT_USER" venv/bin/pip install --upgrade pip setuptools wheel
sudo -u "$BOT_USER" venv/bin/pip install -r requirements.txt

# Create .env file
echo "5️⃣  Configuring environment..."
if [ ! -f "$BOT_HOME/.env" ]; then
    cp "$BOT_HOME/.env.example" "$BOT_HOME/.env"
fi

if [ -n "$BOT_TOKEN" ]; then
    sed -i "s/your_bot_token_here/$BOT_TOKEN/" "$BOT_HOME/.env"
    echo "✓ Bot token configured"
else
    echo "⚠️  Bot token not provided. Please edit .env manually."
fi

# Create logs directory
mkdir -p "$BOT_HOME/logs"
chown -R "$BOT_USER:$BOT_USER" "$BOT_HOME/logs"

# Setup systemd service
echo "6️⃣  Installing systemd service..."
cp "$BOT_HOME/voice-trimmer-bot.service" "/etc/systemd/system/$SERVICE_NAME.service"

# Update paths in service file
sed -i "s|/home/ubuntu/voiceTrimmer|$BOT_HOME|g" "/etc/systemd/system/$SERVICE_NAME.service"
sed -i "s|User=ubuntu|User=$BOT_USER|g" "/etc/systemd/system/$SERVICE_NAME.service"

# Reload systemd daemon
systemctl daemon-reload

# Enable and start service
echo "7️⃣  Enabling and starting service..."
systemctl enable "$SERVICE_NAME"
systemctl start "$SERVICE_NAME"

# Check status
sleep 2
echo ""
echo "✅ Deployment completed!"
echo ""
echo "📊 Service Status:"
systemctl status "$SERVICE_NAME" --no-pager

echo ""
echo "📝 Next steps:"
echo "   View logs: journalctl -u $SERVICE_NAME -f"
echo "   Stop bot: sudo systemctl stop $SERVICE_NAME"
echo "   Edit config: nano $BOT_HOME/.env"
echo "   Restart: sudo systemctl restart $SERVICE_NAME"
