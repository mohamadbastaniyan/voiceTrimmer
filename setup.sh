#!/bin/bash
# Setup script for Voice Trimmer Bot on Ubuntu

echo "🎵 Voice Trimmer Bot - Ubuntu Setup"
echo "===================================="

# Check if Python 3.8+ is installed
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Installing..."
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip python3-venv
else
    echo "✓ Python 3 is installed"
fi

# Check if FFmpeg is installed
echo "Checking FFmpeg installation..."
if ! command -v ffmpeg &> /dev/null; then
    echo "❌ FFmpeg is not installed. Installing..."
    sudo apt-get install -y ffmpeg
else
    echo "✓ FFmpeg is installed"
fi

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your TELEGRAM_BOT_TOKEN"
else
    echo "✓ .env file already exists"
fi

# Create logs directory
mkdir -p logs

echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your TELEGRAM_BOT_TOKEN"
echo "   nano .env"
echo ""
echo "2. Run the bot:"
echo "   source venv/bin/activate"
echo "   python src/bot.py"
echo ""
echo "3. For production, use systemd:"
echo "   sudo nano /etc/systemd/system/voice-trimmer-bot.service"
echo "   (See README.md for service file template)"
