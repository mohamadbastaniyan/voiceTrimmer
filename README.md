# Voice Trimmer - Telegram Bot 🎵

A Telegram bot that converts music files to voice messages with a specific duration. Perfect for sharing audio clips on Telegram with precise length control.

## Features

- 🎵 Convert audio files to Telegram voice messages
- ✂️ Trim audio to specific duration
- 🔄 Support for multiple audio formats (MP3, WAV, OGG, FLAC, M4A, AAC)
- 📱 Easy-to-use Telegram interface
- 🚀 Optimized for Ubuntu/Linux servers
- 📊 Comprehensive logging

## Prerequisites

Before running the bot, ensure you have:

1. **Python 3.8+**
2. **FFmpeg** - For audio processing
   ```bash
   sudo apt-get update
   sudo apt-get install ffmpeg
   ```
3. **FFprobe** - Part of FFmpeg, for audio analysis
4. **Telegram Bot Token** - Get it from [@BotFather](https://t.me/botfather) on Telegram

## Installation

### 1. Clone the repository
```bash
git clone <repository-url>
cd voiceTrimmer
```

### 2. Create a Python virtual environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 4. Set environment variables
Create a `.env` file in the project root or export variables:

```bash
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
export MAX_DURATION=60
export LOG_DIR="./logs"
```

Or create a `.env` file:
```
TELEGRAM_BOT_TOKEN=your_bot_token_here
MAX_DURATION=60
LOG_DIR=./logs
DEBUG=False
```

## Usage

### Local Development

1. Activate virtual environment:
   ```bash
   source venv/bin/activate
   ```

2. Run the bot:
   ```bash
   python src/bot.py
   ```

### Ubuntu Server Deployment

#### Option 1: Using systemd service

1. Create a systemd service file:
   ```bash
   sudo nano /etc/systemd/system/voice-trimmer-bot.service
   ```

2. Add the following content:
   ```ini
   [Unit]
   Description=Voice Trimmer Telegram Bot
   After=network.target

   [Service]
   Type=simple
   User=<your-username>
   WorkingDirectory=/path/to/voiceTrimmer
   Environment="TELEGRAM_BOT_TOKEN=your_token_here"
   Environment="MAX_DURATION=60"
   ExecStart=/path/to/voiceTrimmer/venv/bin/python src/bot.py
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

3. Enable and start the service:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable voice-trimmer-bot
   sudo systemctl start voice-trimmer-bot
   ```

4. Check status:
   ```bash
   sudo systemctl status voice-trimmer-bot
   ```

#### Option 2: Using screen or tmux

```bash
screen -S voice-bot
source venv/bin/activate
export TELEGRAM_BOT_TOKEN="your_token_here"
python src/bot.py
```

#### Option 3: Using Docker

Create a `Dockerfile`:
```dockerfile
FROM python:3.9-slim

# Install FFmpeg
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "src/bot.py"]
```

Build and run:
```bash
docker build -t voice-trimmer-bot .
docker run -e TELEGRAM_BOT_TOKEN="your_token" voice-trimmer-bot
```

## Bot Commands

- `/start` - Show welcome message and instructions
- `/help` - Get detailed help about the bot
- `/cancel` - Cancel current operation

## How to Use the Bot

1. **Start the bot** in Telegram by finding it and clicking `/start`
2. **Send an audio file** (MP3, WAV, OGG, FLAC, M4A, or AAC)
3. **Specify the duration** in seconds (e.g., "30")
4. **Receive the voice message** trimmed to your exact duration

## Configuration

Edit `config/settings.py` to customize:

- `MAX_DURATION` - Maximum allowed duration (default: 60s)
- `SAMPLE_RATE` - Audio sample rate (default: 48000 Hz)
- `SUPPORTED_FORMATS` - List of supported audio formats
- `LOG_DIR` - Directory for log files
- `PROCESS_TIMEOUT` - Timeout for audio processing (default: 300s)

## Project Structure

```
voiceTrimmer/
├── src/
│   ├── bot.py              # Main bot logic
│   └── audio_processor.py  # Audio conversion functions
├── config/
│   └── settings.py         # Configuration settings
├── logs/                   # Log files directory
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Troubleshooting

### "FFmpeg not found"
Ensure FFmpeg is installed:
```bash
sudo apt-get install ffmpeg
```

Verify installation:
```bash
ffmpeg -version
ffprobe -version
```

### "TELEGRAM_BOT_TOKEN not set"
Make sure you've set the environment variable:
```bash
export TELEGRAM_BOT_TOKEN="your_token_here"
```

### Audio processing times out
Increase `PROCESS_TIMEOUT` in settings.py or via environment variable:
```bash
export PROCESS_TIMEOUT=600
```

### Permission issues on Ubuntu
If running as a service, ensure the user has proper permissions:
```bash
sudo chown -R username:username /path/to/voiceTrimmer
```

## System Requirements

- **CPU**: Minimum 1 core (more cores recommended for faster processing)
- **RAM**: Minimum 512MB (1GB+ recommended)
- **Storage**: At least 1GB free for temporary files
- **Network**: Stable internet connection for Telegram API
- **OS**: Ubuntu 18.04 LTS or newer (compatible with other Linux distributions)

## Performance Optimization

### For High-Load Scenarios

1. Use a more powerful server
2. Implement request queuing
3. Use multiple bot instances with load balancing
4. Cache frequently processed files

### FFmpeg Optimization

Adjust encoding parameters in `audio_processor.py`:
- `-ab 128k` - Change bitrate for quality/speed tradeoff
- `-threads` - Use multiple CPU threads for encoding

## Security Considerations

1. **Never commit tokens** - Use environment variables only
2. **Validate file inputs** - Already implemented with audio validation
3. **Rate limiting** - Consider implementing user rate limits
4. **File size limits** - Already enforced (50MB max)
5. **Temporary files** - Automatically cleaned up after processing

## Logging

Logs are saved to `logs/` directory with timestamp:
```
logs/bot_20240115_143022.log
```

View logs:
```bash
tail -f logs/bot_*.log
```

## Performance Metrics

- Average processing time: 2-10 seconds (depends on file size and server)
- Supported maximum file size: 50MB
- Maximum duration: 60 seconds (configurable)

## Future Enhancements

- [ ] Database support for user history
- [ ] Batch processing for multiple files
- [ ] Audio effects (normalization, compression)
- [ ] Custom bitrate selection
- [ ] File format conversion options
- [ ] User statistics and analytics

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open source. Please check LICENSE file for details.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review logs in the `logs/` directory
3. Open an issue on the repository

## Disclaimer

This bot is provided as-is. Make sure to comply with Telegram's Terms of Service and local regulations when using this bot.

---

**Last Updated**: November 2025
