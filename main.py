from datetime import timedelta
import datetime
import openpyxl
from telegram import *
from telegram.ext import *
from openpyxl import Workbook

import sheet_file
from functions import *
from task_create import *
from payment_sheet import *
from settings_con import *


def start(update, context):
    message = update.message
    chat_id = message.chat_id
    username = message.from_user.username
    current_time = datetime.now().strftime("%d-%m-%Y")
    find_people = db.reference(f'peoples/{chat_id}').get() or {}
    if username is None:
        bot.sendMessage(chat_id=chat_id, text=f"Hello @{username}\n"
                                              f"Please set your telegram username in settings!\n"
                                              f"Check out this document for guidance: Not set")
    elif find_people is None or len(find_people) == 0:
        db.reference(f'peoples/{chat_id}').set({
            'username': username,
            'chat_id': chat_id,
            'binance': None,
            'UPI': None,
            'address': None,
            'first_started': current_time
        })
        bot.sendMessage(chat_id=chat_id, text=f"Hello! welcome @{username}")
    else:
        bot.sendMessage(chat_id=chat_id, text="Hi! welcome back")
    menu_button(update, context)


def cancel(update, context):
    message = update.message
    chat_id = message.chat_id
    reply_keyboard = [["settings", "task list"]]
    bot.sendMessage(chat_id=chat_id, text="Use menu buttons for quick access",
                    reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True),
                    reply_to_message_id=update.message.message_id)


def collect_message(update, context):
    message = update.message
    chat_id = message.chat_id
    chat_type = message.chat.type
    text = message.text
    username = ''
    try:
        username = message.from_user.username
    except:
        bot.sendMessage(chat_id=1291659507, text=f"Error data:\n\n"
                                                 f"chat id: {chat_id}"
                                                 f"username: {username}"
                                                 f"Message: {text}")
    if username is None:
        bot.sendMessage(chat_id=chat_id, text=f"Hello @{username}\n"
                                              f"Please set your telegram username in settings!\n"
                                              f"Check out this document for guidance: Not set")
        return
    if text == "cancel":
        cancel(update, context)
    elif chat_type == "private":
        text = text.lower()
        username = update.message.chat.username
        username = username.lower()
        if "task list" == text:
            user_task_list = db.reference(f"tasks").get() or {}
            text = ""
            for i in user_task_list:
                each_task = db.reference(f"tasks/{i}").get() or {}
                if username in each_task["workers"]:
                    text += f"Title : {each_task['title']}\nCommand: <code>sheet {each_task['task_id']}</code>\n\n"
            if len(text) <= 1:
                bot.sendMessage(chat_id=chat_id, text="You are not assigned for any task right now!")
            else:
                bot.sendMessage(chat_id=chat_id, text=f"Task List:\n\n"
                                                      f"{text}"
                                                      f"Just click to copy the command and send it here",
                                parse_mode="html")
        elif "sheet " in text:
            task_id = text.split(" ")
            sheet_file.spreadsheet(update, context, chat_id, task_id[1])
        elif "pause " in text:
            text_li = text.split(" ")
            if text_li[1].isnumeric():
                get = db.reference(f'task_ids/{text_li[1]}').get() or {}
                db.reference(f"tasks/{get['group_id']}").update({
                    'status': 'paused'
                })
                bot.sendMessage(chat_id=chat_id, text=f"{get['title']} : Task paused!")
                bot.sendMessage(chat_id=get['group_id'], text="Task paused")
            else:
                bot.sendMessage(chat_id=chat_id, text="Task id must be a number")
        elif "active " in text:
            text_li = text.split(" ")
            if text_li[1].isnumeric():
                get = db.reference(f'task_ids/{text_li[1]}').get() or {}
                db.reference(f"tasks/{get['group_id']}").update({
                    'status': 'active'
                })
                bot.sendMessage(chat_id=chat_id, text=f"{get['title']} : Task Activated!")
                bot.sendMessage(chat_id=get['group_id'], text="Task activated")
            else:
                bot.sendMessage(chat_id=chat_id, text="Task id must be a number")

    elif chat_type == "group" or chat_type == "supergroup":
        group_id = message.chat.id
        # Only process messages from specific users in personal chat
        collection_name = datetime.now().strftime("%d-%m-%Y")
        message_id = message.message_id
        message_date_ist = datetime.now().strftime("%d-%m-%Y")
        text = message.text
        task = db.reference(f'tasks/{group_id}').get() or {}
        if len(task) <= 0 or username not in task["workers"] or task['status'] == 'paused':
            return
        inserting = "link" if task['task_type'] == "twitter" else "text"

        if task['task_type'] == 'twitter':
            if 'twitter.com' not in text or len(text) > 20:
                return
            text = text.lower()
            tweet_links_ref = db.reference(f"tasks/{task['group_id']}/collection/")
            query = tweet_links_ref.order_by_value().equal_to(text)
            if query.get():
                bot.sendMessage(chat_id=chat_id, text="Link already exits!",
                                reply_to_message_id=update.message.message_id)
                return
        # Store message data in Firebase Realtime Database
        db.reference(f"tasks/{task['group_id']}/collection/{collection_name}/{message_id}").set({
            'username': username,
            inserting: text,
            'message_id': message_id,
            'time': message_date_ist
        })


def main():
    updater = Updater(token="6109952194:AAEFEucsgBgQNLIfaSAvzi0n852KM8Y0NZg", use_context=True)
    dp = updater.dispatcher
    create = ConversationHandler(
        entry_points=[CommandHandler('create_task', create_task)],
        states={
            TITLE: [MessageHandler(Filters.text, title)],
            TASK_TYPE: [MessageHandler(Filters.text, task_type)],
            CHAT_ID: [MessageHandler(Filters.text, chat_id)],
            LIMIT: [MessageHandler(Filters.text, limit)],
            MEMBERS_LIST: [MessageHandler(Filters.text, members_list)],
            CONFIRM: [MessageHandler(Filters.text, confirm)]
        }, fallbacks=[]
    )
    payment_handler = ConversationHandler(
        entry_points=[CommandHandler('payment', payment_start)],
        states={
            TASK_ID: [MessageHandler(Filters.text, task_id)],
            DATE_RANGE: [MessageHandler(Filters.text, date_range)],
        }, fallbacks=[]
    )

    twitter_settings = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('^twitter$'), twitter_ids)],
        states={
            TWITTER_UPDATE: [MessageHandler(Filters.text, twitter_update)],
            TWITTER_UPDATE_LIST: [MessageHandler(Filters.text, twitter_update_list)],
            TWITTER_UPDATE_CONFIRM: [MessageHandler(Filters.text, twitter_update_confirm)],
        }, fallbacks=[MessageHandler(Filters.regex('^cancel$'), cancel)]
    )

    binance = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('^binance$'), binance_start)],
        states={
            BINANCE_OPTIONS: [MessageHandler(Filters.text, binance_option)],
            SET_BINANCE: [MessageHandler(Filters.text, set_binance)],
        }, fallbacks=[MessageHandler(Filters.regex('^cancel$'), cancel)]
    )
    
    dp.add_handler(binance)
    dp.add_handler(twitter_settings)
    dp.add_handler(payment_handler)
    dp.add_handler(create)
    dp.add_handler(MessageHandler(Filters.regex('^settings$'), settings))
    dp.add_handler(CommandHandler("cancel", cancel))
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text, collect_message))
    updater.start_polling()


main()
