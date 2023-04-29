import firebase_admin
from firebase_admin import credentials, db
from google.oauth2.credentials import Credentials
from pytz import timezone
import datetime
from telegram.bot import Bot
from telegram.replykeyboardmarkup import ReplyKeyboardMarkup
from telegram.ext import ConversationHandler
import openpyxl

cred = credentials.Certificate("kit-pro-f4b0d-firebase-adminsdk-mhzrf-8a07acab1c.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://kit-pro-f4b0d-default-rtdb.firebaseio.com/"
})

bot = Bot(token="6109952194:AAEFEucsgBgQNLIfaSAvzi0n852KM8Y0NZg")


def menu_button(update,context):
    chat_id = update.message.chat_id
    text = update.message.text
    reply_keyboard = [["settings","sheet"]]
    bot.sendMessage(chat_id=chat_id,text="Use below buttons for quick access",
                    reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True),
                    reply_to_message_id=update.message.message_id)
