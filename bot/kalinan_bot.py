from kalinan import Kalinan
from kalinan_config import KalinanConfig
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardRemove,
    )
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
    )
import logging


class KalinanBot:
    def __init__(self):
        self.kalinan = None
        self.config = KalinanConfig()
        self.bot = Application.builder().token(self.config.token).build()

    def run(self):
        # Configure logging
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO
        )
        
        self.bot.add_handler(
            MessageHandler(filters.TEXT, callback=self.start_command)
        )

        self.bot.run_polling()

    async def start_command(self, update: Update, context: ContextTypes):
        self.kalinan = Kalinan()
        text = "This is start message."
        await update.message.reply_text(text)


if __name__ == "__main__":
    kalinan_bot = KalinanBot()
    kalinan_bot.run()
