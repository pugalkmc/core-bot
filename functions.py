import firebase_admin
from firebase_admin import credentials, db
from google.oauth2.credentials import Credentials
from pytz import timezone
import datetime
from telegram.bot import Bot
from telegram.replykeyboardmarkup import ReplyKeyboardMarkup
from telegram.ext import ConversationHandler
import openpyxl

cred = credentials.Certificate("groove-mark-bot-firebase-adminsdk-z7wmh-c775561056.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://groove-mark-bot-default-rtdb.firebaseio.com/"
})

BOT_TOKEN = "6096228474:AAES2m4LdoUBfMcwYYY9bnlr5f51f55ptRQ"
bot = Bot(token=BOT_TOKEN)


def menu_button(update,context):
    chat_id = update.message.chat_id
    text = update.message.text
    reply_keyboard = [["settings","sheet"]]
    bot.sendMessage(chat_id=chat_id,text="Use below buttons for quick access",
                    reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True),
                    reply_to_message_id=update.message.message_id)

def settings(update, context):
    chat_id = update.message.chat_id
    text = update.message.text
    reply_keyboard = [["twitter", "binance", "discord"], ['main menu']]
    bot.sendMessage(chat_id=chat_id, text="Choose options",
                    reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True),
                    reply_to_message_id=update.message.message_id)
