#!/usr/bin/env python3
"""
Audio processing module for converting audio files to voice messages
"""

import logging
import subprocess
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class AudioProcessor:
    """Handles audio file processing and conversion"""
    
    # Supported input formats
    SUPPORTED_FORMATS = {
        'mp3': 'libmp3lame',
        'wav': 'pcm_s16le',
        'ogg': 'libvorbis',
        'flac': 'flac',
        'm4a': 'aac',
        'aac': 'aac',
    }
    
    def __init__(self):
        """Initialize audio processor"""
        self.logger = logging.getLogger(__name__)
    
    def get_duration(self, file_path: str) -> Optional[float]:
        """
        Get duration of audio file in seconds
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Duration in seconds or None if failed
        """
        try:
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1:noescapes=1',
                file_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                duration = float(result.stdout.strip())
                self.logger.info(f"Audio duration: {duration}s")
                return duration
            else:
                self.logger.error(f"ffprobe error: {result.stderr}")
                return None
        
        except subprocess.TimeoutExpired:
            self.logger.error("ffprobe timeout")
            return None
        except (ValueError, AttributeError) as e:
            self.logger.error(f"Error parsing duration: {str(e)}")
            return None
    
    def convert_to_voice(
        self,
        input_path: str,
        output_path: str,
        target_duration: int = 60,
        sample_rate: int = 48000,
        channels: int = 1
    ) -> bool:
        """
        Convert audio file to Telegram voice message format (OGG/OPUS)
        
        Args:
            input_path: Path to input audio file
            output_path: Path to output OGG file
            target_duration: Target duration in seconds
            sample_rate: Output sample rate (default 48000 for Telegram)
            channels: Number of channels (1 for mono)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # First, get the actual duration
            actual_duration = self.get_duration(input_path)
            if actual_duration is None:
                self.logger.error("Failed to get audio duration")
                return False
            
            # Determine if we need to trim or pad
            trim_end = min(target_duration, actual_duration)
            
            # FFmpeg command to convert to OGG/OPUS
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-t', str(trim_end),  # Trim to target duration
                '-acodec', 'libopus',  # Use Opus codec (Telegram voice format)
                '-ab', '128k',  # Bitrate
                '-ar', str(sample_rate),  # Sample rate
                '-ac', str(channels),  # Channels (mono)
                '-vn',  # No video
                '-y',  # Overwrite output
                output_path
            ]
            
            self.logger.info(f"Converting audio: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode != 0:
                self.logger.error(f"FFmpeg error: {result.stderr}")
                return False
            
            # Verify output file exists and has content
            output_file = Path(output_path)
            if not output_file.exists() or output_file.stat().st_size == 0:
                self.logger.error("Output file is empty or doesn't exist")
                return False
            
            self.logger.info(
                f"Successfully converted audio to {output_path} "
                f"({output_file.stat().st_size} bytes)"
            )
            return True
        
        except subprocess.TimeoutExpired:
            self.logger.error("FFmpeg timeout - file processing took too long")
            return False
        except Exception as e:
            self.logger.error(f"Error during audio conversion: {str(e)}")
            return False
    
    def validate_audio_file(self, file_path: str) -> bool:
        """
        Validate if file is a valid audio file
        
        Args:
            file_path: Path to file to validate
            
        Returns:
            True if valid audio file, False otherwise
        """
        try:
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-select_streams', 'a:0',
                '-show_entries', 'stream=codec_type',
                '-of', 'csv=p=0',
                file_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            is_valid = result.returncode == 0 and 'audio' in result.stdout
            
            if is_valid:
                self.logger.info(f"Audio file validated: {file_path}")
            else:
                self.logger.warning(f"Invalid audio file: {file_path}")
            
            return is_valid
        
        except Exception as e:
            self.logger.error(f"Error validating audio file: {str(e)}")
            return False
    
    def get_file_format(self, file_path: str) -> Optional[str]:
        """
        Detect audio file format
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Format string or None if detection failed
        """
        try:
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-select_streams', 'a:0',
                '-show_entries', 'stream=codec_name',
                '-of', 'default=noprint_wrappers=1:nokey=1:noescapes=1',
                file_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                format_str = result.stdout.strip()
                self.logger.info(f"Detected format: {format_str}")
                return format_str
            return None
        
        except Exception as e:
            self.logger.error(f"Error detecting format: {str(e)}")
            return None
