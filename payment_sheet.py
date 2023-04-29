from functions import *
import telegram
from datetime import datetime, timedelta

TASK_ID, DATE_RANGE = range(2)


def payment_start(update, context):
    message = update.message
    chat_id = message.chat_id
    username = message.from_user.username
    bot.sendMessage(chat_id=chat_id, text=f"Enter the task ID")
    return TASK_ID


def task_id(update, context):
    message = update.message
    chat_id = message.chat_id
    username = message.from_user.username
    text = message.text
    if text == "cancel":
        bot.sendMessage(chat_id=chat_id, text="Data retrive request cancelled")
        menu_button(update, context)
        return ConversationHandler.END
    get_id = db.reference(f"task_ids").get() or {}
    if text in get_id:
        context.user_data["group_id"] = get_id[text]["group_id"]
        bot.sendMessage(chat_id=chat_id, text=f"Enter the start and end date to retrive the data"
                                              f"Example: 01-01-2023 30-03-2023")
        return DATE_RANGE
    else:
        bot.sendMessage(chat_id=chat_id, text="Task id incorrect!")
        return TASK_ID


def date_range(update, context):
    message = update.message
    chat_id = message.chat_id
    username = message.from_user.username
    text = message.text
    if text == "cancel":
        bot.sendMessage(chat_id=chat_id, text="Data retrive request cancelled")
        menu_button(update, context)
        return ConversationHandler.END
    date_li = text.split(" ")
    start_date = ''
    end_date = ''
    try:
        start_date = datetime.strptime(date_li[0], "%d-%m-%Y")
    except:
        bot.sendMessage(chat_id=chat_id, text="Date format wrong")
        return DATE_RANGE
    try:
        end_date = datetime.strptime(date_li[1], "%d-%m-%Y")
    except:
        bot.sendMessage(chat_id=chat_id, text="Date format wrong")
        return DATE_RANGE
    current_date = start_date
    
    group_id = context.user_data["group_id"]
    workers = db.reference(f"tasks/{group_id}/workers").get() or {}
    dict_payment = {key: 0 for key in workers}
    while current_date <= end_date:
        current_date += timedelta(days=1)
        other_date = current_date.strftime("%d-%m-%Y")
        each_date = db.reference(f"tasks/{group_id}/collection/{other_date}").get() or {}
        for i in each_date:
            dict_payment[each_date[i]['username']] += 1
    text = f"Total counts from {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}\n\n"
    for i in dict_payment:
        text += f"{i} : {dict_payment[i]}\n"
    bot.sendMessage(chat_id=chat_id,text=text)
    return ConversationHandler.END


