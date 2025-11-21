#!/usr/bin/env python3
"""
Telegram Voice Message Bot
Converts music files to voice messages with specific length
"""

import logging
import os
import sys
import tempfile
from pathlib import Path
from datetime import datetime

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import TELEGRAM_TOKEN, MAX_DURATION, SUPPORTED_FORMATS, LOG_DIR
from src.audio_processor import AudioProcessor

# Configure logging
log_dir = Path(LOG_DIR)
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / f"bot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class VoiceMessageBot:
    """Main bot class for handling Telegram interactions"""
    
    def __init__(self):
        self.audio_processor = AudioProcessor()
        self.application = None
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_text = (
            "Welcome to Voice Trimmer Bot! 🎵\n\n"
            "I convert music files to voice messages with specific length.\n\n"
            "Supported formats: " + ", ".join(SUPPORTED_FORMATS) + "\n"
            f"Maximum duration: {MAX_DURATION} seconds\n\n"
            "Usage:\n"
            "1. Send me a music file\n"
            "2. Specify the desired duration in seconds (optional)\n"
            "3. I'll convert it to a voice message and send it back\n\n"
            "Commands:\n"
            "/start - Show this message\n"
            "/help - Get help\n"
            "/cancel - Cancel current operation"
        )
        await update.message.reply_text(welcome_text)
        logger.info(f"User {update.effective_user.id} started the bot")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = (
            "Voice Trimmer Bot Help\n\n"
            "How to use:\n"
            "1. Send an audio file (MP3, WAV, OGG, etc.)\n"
            "2. Reply with the desired duration in seconds\n"
            "3. The bot will convert and send back as a voice message\n\n"
            "Limitations:\n"
            f"• Max file size: 20MB\n"
            f"• Max duration: {MAX_DURATION} seconds\n"
            f"• Output: Telegram voice message format (OGG)\n\n"
            "Tips:\n"
            "• Longer durations take more time to process\n"
            "• Quality depends on input file quality"
        )
        await update.message.reply_text(help_text)
        logger.info(f"User {update.effective_user.id} requested help")
    
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /cancel command"""
        if context.user_data.get('processing'):
            context.user_data['processing'] = False
            await update.message.reply_text("Operation cancelled.")
            logger.info(f"User {update.effective_user.id} cancelled operation")
        else:
            await update.message.reply_text("No operation in progress.")
    
    async def handle_audio(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle audio file uploads"""
        try:
            if context.user_data.get('processing'):
                await update.message.reply_text(
                    "I'm already processing a file. Please wait..."
                )
                return
            
            context.user_data['processing'] = True
            user_id = update.effective_user.id
            
            # Get the audio file
            audio = update.message.audio or update.message.document or update.message.voice
            
            if not audio:
                await update.message.reply_text("Please send an audio file.")
                context.user_data['processing'] = False
                return
            
            # Check file size (Telegram limit is 50MB for files)
            if audio.file_size > 50 * 1024 * 1024:
                await update.message.reply_text(
                    "File is too large. Maximum size is 50MB."
                )
                context.user_data['processing'] = False
                return
            
            logger.info(f"User {user_id} sent audio file: {audio.file_name or 'unknown'}")
            
            # Download file
            processing_msg = await update.message.reply_text("Downloading file...")
            file = await context.bot.get_file(audio.file_id)
            
            with tempfile.TemporaryDirectory() as temp_dir:
                input_path = Path(temp_dir) / (audio.file_name or f"audio_{user_id}")
                await file.download_to_drive(input_path)
                
                # Ask for duration if not provided
                if not context.user_data.get('target_duration'):
                    context.user_data['file_path'] = str(input_path)
                    await processing_msg.edit_text(
                        f"File received! Current duration: {self.audio_processor.get_duration(str(input_path))}s\n\n"
                        f"Reply with desired duration (1-{MAX_DURATION} seconds):"
                    )
                    return
                
                # Process the audio
                target_duration = context.user_data.get('target_duration', MAX_DURATION)
                
                await processing_msg.edit_text("Processing audio...")
                output_path = Path(temp_dir) / "output.ogg"
                
                success = self.audio_processor.convert_to_voice(
                    str(input_path),
                    str(output_path),
                    target_duration
                )
                
                if not success:
                    await processing_msg.edit_text(
                        "Failed to process audio. Please try again."
                    )
                    context.user_data['processing'] = False
                    return
                
                # Send as voice message
                await processing_msg.edit_text("Sending voice message...")
                
                with open(output_path, 'rb') as voice_file:
                    await update.message.reply_voice(
                        voice_file,
                        duration=target_duration,
                        caption=f"Duration: {target_duration}s"
                    )
                
                await processing_msg.edit_text("✅ Done!")
                logger.info(f"Successfully processed audio for user {user_id}")
                
                # Reset user data
                context.user_data['processing'] = False
                context.user_data['target_duration'] = None
                context.user_data['file_path'] = None
        
        except Exception as e:
            logger.error(f"Error processing audio: {str(e)}")
            await update.message.reply_text(
                f"An error occurred: {str(e)}\n\nPlease try again."
            )
            context.user_data['processing'] = False
    
    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages (duration specification)"""
        try:
            if context.user_data.get('file_path'):
                # User is specifying duration
                try:
                    duration = int(update.message.text)
                    if duration < 1 or duration > MAX_DURATION:
                        await update.message.reply_text(
                            f"Please specify a duration between 1 and {MAX_DURATION} seconds."
                        )
                        return
                    
                    context.user_data['target_duration'] = duration
                    
                    # Process the file
                    await update.message.reply_text("Processing audio...")
                    
                    input_path = context.user_data['file_path']
                    with tempfile.TemporaryDirectory() as temp_dir:
                        output_path = Path(temp_dir) / "output.ogg"
                        
                        success = self.audio_processor.convert_to_voice(
                            input_path,
                            str(output_path),
                            duration
                        )
                        
                        if not success:
                            await update.message.reply_text(
                                "Failed to process audio. Please try again."
                            )
                            return
                        
                        # Send as voice message
                        with open(output_path, 'rb') as voice_file:
                            await update.message.reply_voice(
                                voice_file,
                                duration=duration,
                                caption=f"Duration: {duration}s"
                            )
                        
                        logger.info(
                            f"User {update.effective_user.id} created voice message "
                            f"with {duration}s duration"
                        )
                        
                        # Reset user data
                        context.user_data['processing'] = False
                        context.user_data['target_duration'] = None
                        context.user_data['file_path'] = None
                
                except ValueError:
                    await update.message.reply_text(
                        f"Please send a valid number between 1 and {MAX_DURATION}."
                    )
            else:
                await update.message.reply_text(
                    "Please send an audio file first.\n"
                    "Type /help for more information."
                )
        
        except Exception as e:
            logger.error(f"Error handling text: {str(e)}")
            await update.message.reply_text("An error occurred. Please try again.")
    
    def setup_handlers(self):
        """Setup command and message handlers"""
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("cancel", self.cancel))
        
        # Handle audio files
        self.application.add_handler(MessageHandler(
            filters.AUDIO | filters.VOICE | (filters.Document() & ~filters.COMMAND),
            self.handle_audio
        ))
        
        # Handle text messages
        self.application.add_handler(MessageHandler(filters.TEXT, self.handle_text))
    
    async def run(self):
        """Start the bot"""
        self.application = Application.builder().token(TELEGRAM_TOKEN).build()
        
        self.setup_handlers()
        
        logger.info("Starting Telegram bot...")
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        logger.info("Bot is running. Press Ctrl+C to stop.")
        
        try:
            await self.application.updater.stop()
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
            await self.application.stop()
            await self.application.shutdown()


def main():
    """Main entry point"""
    bot = VoiceMessageBot()
    import asyncio
    asyncio.run(bot.run())


if __name__ == "__main__":
    main()
