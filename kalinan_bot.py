import logging
import re
from config.kalinan_config import KalinanConfig
from peewee import DoesNotExist
from models.user_model import User
from models.user_model import db
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardRemove
    )
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackQueryHandler,
    ContextTypes,
    CallbackContext,
    filters
    )


class KalinanBot:
    def __init__(self):
        self.config = KalinanConfig()
        self.bot = Application.builder().token(self.config.token).build()
        self.USERNAME, self.PASSWORD, self.REGISTER = range(3)

    def run(self):
        # Configure logging
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO
        )

        registeration_handler = ConversationHandler(
            entry_points = [CommandHandler("start", self.start_command)],
            states = {
                self.USERNAME: [CallbackQueryHandler(self.button_callback)],
                self.PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_password)],
                self.REGISTER: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.register_user)],
            },
            fallbacks = []
        )
        self.bot.add_handler(registeration_handler)


        self.bot.run_polling()


    async def start_command(self, update: Update, context: CallbackContext):
        user = update.message.from_user
        chat_id = str(user.id)

        try:
            existing_user = User.get(User.chat_id == chat_id)
            await context.bot.send_message(
                chat_id=chat_id,
                text='You already registered.'
            )
        except DoesNotExist:
            await update.message.reply_text("You are not registered. Let's start the registration process.")
            keyboard = [[InlineKeyboardButton("Register", callback_data='register')]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await context.bot.send_message(
                chat_id=chat_id,
                text='Click the button below to start the registration process:',
                reply_markup = reply_markup,
            )

        return self.USERNAME

    async def button_callback(self, update: Update, context: CallbackContext):
        query = update.callback_query
        print('in button_callback')

        if query.data == 'register':
            chat_id = query.message.chat_id
            await context.bot.send_message(
            chat_id=chat_id,
            text='Ok, send your Kalinan username:'
            )

            return self.PASSWORD

    
    async def get_password(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        kalinan_username = update.message.text
        chat_id = update.message.from_user.id
        print('in get_password')

        context.user_data['kalinan_username'] = kalinan_username
        await context.bot.send_message(
            chat_id=chat_id,
            text='Ok, send your Kalinan password:'
        )

        return self.REGISTER
    
    async def register_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.message.from_user
        chat_id = str(user.id)

        kalinan_username = context.user_data.get('kalinan_username')
        kalinan_password = update.message.text

        new_user = User.create_user(chat_id, user.first_name, user.username, kalinan_username, kalinan_password)
        await update.message.reply_text('You have been successfully registered.')

        return ConversationHandler.END


if __name__ == '__main__':
    bot = KalinanBot()
    bot.run()
