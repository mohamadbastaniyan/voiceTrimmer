#!/usr/bin/env python3
"""
Configuration settings for Voice Trimmer Bot
"""

import os
from pathlib import Path

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Telegram Bot Token (set via environment variable)
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_TELEGRAM_BOT_TOKEN_HERE')

# Audio settings
MAX_DURATION = int(os.getenv('MAX_DURATION', '60'))  # Maximum voice message duration in seconds
MIN_DURATION = 1  # Minimum duration in seconds
SAMPLE_RATE = 48000  # Sample rate for Telegram voice messages
CHANNELS = 1  # Mono audio

# Supported audio formats
SUPPORTED_FORMATS = ['mp3', 'wav', 'ogg', 'flac', 'm4a', 'aac']

# File size limits
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB (Telegram limit)

# Logging
LOG_DIR = os.getenv('LOG_DIR', str(PROJECT_ROOT / 'logs'))
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# FFmpeg settings
FFMPEG_PATH = os.getenv('FFMPEG_PATH', 'ffmpeg')
FFPROBE_PATH = os.getenv('FFPROBE_PATH', 'ffprobe')

# Processing
TEMP_DIR = os.getenv('TEMP_DIR', '/tmp/voice_trimmer')  # Temporary directory for processing
PROCESS_TIMEOUT = int(os.getenv('PROCESS_TIMEOUT', '300'))  # 5 minutes

# Bot behavior
REQUEST_KWARGS = {
    'connect_timeout': 10,
    'read_timeout': 10,
}

# Database (optional, for future use)
DATABASE_URL = os.getenv('DATABASE_URL', None)

# Development
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Validate token
if TELEGRAM_TOKEN == 'YOUR_TELEGRAM_BOT_TOKEN_HERE':
    raise ValueError(
        "TELEGRAM_BOT_TOKEN environment variable is not set. "
        "Please set it before running the bot."
    )
