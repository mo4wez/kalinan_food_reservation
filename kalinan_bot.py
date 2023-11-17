import os
import logging
from kalinan import Kalinan
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
    def __init__(self, kalinan_instanse: Kalinan):
        self.kalinan = kalinan_instanse
        # self.kalinan.load_cookies('cookies.pkl')
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
            entry_points=[CommandHandler("start", self.start_command)],
            states={
                self.USERNAME: [CallbackQueryHandler(self.button_callback)],
                self.PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_password)],
                self.REGISTER: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.register_user)],
            },
            fallbacks=[]
        )
        self.bot.add_handler(registeration_handler)

        reservation_handler = CallbackQueryHandler(self.button_callback)
        self.bot.add_handler(reservation_handler, group=1)

        day_data_handler = CallbackQueryHandler(self.show_day_data)
        self.bot.add_handler(day_data_handler, group=2)

        self.bot.run_polling()


    async def start_command(self, update: Update, context: CallbackContext):
        user = update.message.from_user
        chat_id = str(user.id)

        try:
            # if self.kalinan.is_logged_in():
            user: User = User.get(chat_id=chat_id)
            sent_message = await context.bot.send_message(
                chat_id=chat_id,
                text='Logging in to Kalinan...'
            )
            self.kalinan.login_to_kalinan(
                kalinan_username=user.kalinan_username,
                kalinan_password=user.kalinan_password,
            )
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=sent_message.message_id,
                text='Login successful.'
                )
            await self.show_meal_menu(update, context, chat_id)

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
        chat_id = query.message.chat_id
        print('in button_callback')

        if query.data == 'register':
            await context.bot.send_message(
            chat_id=chat_id,
            text='Ok, send your Kalinan username:'
            )
            return self.PASSWORD
        
        if query.data == 'ناهار':
            self.kalinan.go_to_reservation_page(meal=query.data)
            self.lunch_data = self.kalinan.get_meal_table_data(
                meal_table='cphMain_grdReservationLunch',
                meal=query.data
            )
            self.current_meal_data = self.lunch_data

            await self.show_days_list(update, context, chat_id, meal_data=self.lunch_data)

        elif query.data == 'شام':
            self.kalinan.go_to_reservation_page(meal=query.data)
            self.dinner_data = self.kalinan.get_meal_table_data(
                meal_table='cphMain_grdReservationDinner',
                meal=query.data
            )
            self.current_meal_data = self.dinner_data

            await self.show_days_list(update, context, chat_id, meal_data=self.dinner_data)
        
        elif query.data == 'days_menu':
            await self.show_days_list(update, context, chat_id, meal_data=self.current_meal_data)

        elif query.data == 'next_day' or query.data == 'prev_day':
            # Pass the 'prev_day' or 'next_day' action to show_day_data
            await self.show_day_data(update, context, meal_data=self.current_meal_data)

        elif query.data == 'meals_menu':
            await self.show_meal_menu(update, context, chat_id)
        
        else:
            if query.data.isdigit():
                await self.show_day_data(update, context, meal_data=self.current_meal_data)

 
    async def get_password(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        kalinan_username = update.message.text
        chat_id = update.message.from_user.id
        print('in get_password')

        context.user_data['kalinan_username'] = kalinan_username
        await context.bot.send_message(
            chat_id=chat_id,
            text='Now, send your Kalinan password:'
        )

        return self.REGISTER
    
    async def register_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.message.from_user
        chat_id = str(user.id)
        message_id = update.message.id

        kalinan_username = context.user_data.get('kalinan_username')
        context.user_data['kalinan_password'] = update.message.text
        kalinan_password = context.user_data['kalinan_password']

        new_user: User = User.create_user(chat_id, user.first_name, user.username, kalinan_username, kalinan_password)
        self.kalinan.login_to_kalinan(
            kalinan_username=new_user.kalinan_username,
            kalinan_password=new_user.kalinan_password,
        )
        await update.message.reply_text('You have been successfully registered.')
        await self.show_meal_menu(update, context)

        return ConversationHandler.END

    async def show_meal_menu(self, update: Update, context: CallbackContext, chat_id):
        query = update.callback_query
        keyboard = [[InlineKeyboardButton("Lunch", callback_data='ناهار')], [InlineKeyboardButton("Dinner", callback_data='شام')]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_message(
            chat_id=chat_id,
            text='Choose a meal:',
            reply_markup=reply_markup
        )

    async def show_days_list(self, update: Update, context: CallbackContext, chat_id, meal_data):
        query = update.callback_query
        keyboard = [
            [InlineKeyboardButton(day, callback_data=str(index))] 
            for index, (day, data_list) in enumerate(meal_data.items())
            ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.edit_text(
            text='Days:',
            reply_markup=reply_markup
        )

    async def show_day_data(self, update: Update, context: CallbackContext, meal_data):
        all_buttons = []
        query = update.callback_query

        day_index = context.user_data.get('current_day_index', 0)
        meal_data = context.user_data.get('meal_data')
        current_day_index = context.user_data.get('current_day_index', 0)

        if day_index.isdigit():
            current_day_index = int(day_index)
        elif day_index == 'next_day':
            current_day_index += 1
        elif day_index == 'prev_day':
            current_day_index -= 1

        current_day_index = max(0, min(current_day_index, len(meal_data) - 1))
        context.user_data['current_day_index'] = current_day_index

        day, data_list = list(meal_data.items())[current_day_index]
        foods = data_list[0]['foods']
        status = data_list[0]['status']

        foods_buttons = [
            [InlineKeyboardButton(food, callback_data=f'food_{index}')] 
            for index, food in enumerate(foods)
        ]

        status_button = [InlineKeyboardButton(status, callback_data='status')]

        day_buttons = [
            [InlineKeyboardButton("Days", callback_data='days_menu')],
            [InlineKeyboardButton("Meals", callback_data='meals_menu')],
            [
                InlineKeyboardButton("Previous Day", callback_data='prev_day'),
                InlineKeyboardButton("Next Day", callback_data='next_day')
            ]
        ]

        all_buttons = foods_buttons + [status_button] + day_buttons
        reply_markup = InlineKeyboardMarkup(all_buttons)

        await query.message.edit_text(
            text=day,
            reply_markup=reply_markup
        )
                