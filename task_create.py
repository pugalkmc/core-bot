from functions import *
import telegram

TITLE, TASK_TYPE, CHAT_ID, LIMIT, MEMBERS_LIST, CONFIRM = range(6)


def create_task(update, context):
    chat_id = update.message.chat_id
    text = update.message.text
    if text == "cancel":
        bot.sendMessage(chat_id=chat_id, text="Task creation Cancelled")
        menu_button(update, context)
        return ConversationHandler.END
    reply_keyboard = [["cancel"]]
    bot.sendMessage(chat_id=chat_id, text="Send the task title",
                    reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True),
                    reply_to_message_id=update.message.message_id)
    return TITLE


def title(update, context):
    chat_id = update.message.chat_id
    text = update.message.text
    if text == "cancel":
        bot.sendMessage(chat_id=chat_id, text="Task creation Cancelled")
        menu_button(update, context)
        return ConversationHandler.END
    if len(text) >= 5:
        context.user_data["title"] = text
        reply_keyboard = [["Telegram", "twitter"], ["cancel"]]
        bot.sendMessage(chat_id=chat_id, text=f"Task title set to : {text}\n\n"
                                              f"Select the task type",
                        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True),
                        reply_to_message_id=update.message.message_id)
        return TASK_TYPE
    else:
        bot.sendMessage(chat_id=chat_id, text=f"Title too short , re-try",
                        reply_to_message_id=update.message.message_id)
        return TITLE


def task_type(update, context):
    chat_id = update.message.chat_id
    text = update.message.text
    text = text.lower()
    if text == "cancel":
        bot.sendMessage(chat_id=chat_id, text="Task creation Cancelled")
        menu_button(update, context)
        return ConversationHandler.END
    task_li = ["telegram", "twitter"]
    if text in task_li:
        context.user_data["task_type"] = text
        reply_keyboard = [["cancel"]]
        bot.sendMessage(chat_id=chat_id, text=f"Chat type set to : {text}\n\n"
                                              f"Now send the group id",
                        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True),
                        reply_to_message_id=update.message.message_id)
        return CHAT_ID
    else:
        bot.sendMessage(chat_id=chat_id, text=f"Type only can be {task_li}",
                        reply_to_message_id=update.message.message_id)
        return TASK_TYPE


def chat_id(update, context):
    chat_id = update.message.chat_id
    text = update.message.text
    if text == "cancel":
        bot.sendMessage(chat_id=chat_id, text="Task creation Cancelled")
        menu_button(update, context)
        return ConversationHandler.END

    group_type = 0
    chat_info = ""
    if not text.isnumeric():
        bot.sendMessage(chat_id=chat_id, text="Chat id must be number",
                        reply_to_message_id=update.message.message_id)
        return CHAT_ID
    try:
        # use the get_chat method to retrieve information about the chat
        chat_info = bot.get_chat(chat_id=int("-" + str(text)))
    except telegram.error.BadRequest:
        # Handle the error if the chat ID is invalid
        try:
            chat_info = bot.get_chat(chat_id=int("-100" + str(text)))
        except:
            bot.sendMessage(chat_id=chat_id, text="Invalid group id , Add me in the group and send the proper group id")
            return CHAT_ID
    if not chat_info['permissions']['can_send_messages']:
        bot.sendMessage(chat_id=chat_id, text=f"I must need admin permission in : {chat_info['title']}")
        bot.sendMessage(chat_id=chat_id, text="Task creation Cancelled")
        menu_button(update, context)
        return ConversationHandler.END
    if chat_info.type == 'group':
        group_type = "group"
    elif chat_info.type == 'supergroup':
        group_type = "supergroup"
    else:
        bot.sendMessage(chat_id=chat_id, text="It is not a group or supergroup",
                        reply_to_message_id=update.message.message_id)
        return CHAT_ID
    context.user_data["group_type"] = group_type
    context.user_data["group_id"] = chat_info['id']
    context.user_data["group_title"] = chat_info.title
    flexible_text = "limit of tweet count for each twitter" if context.user_data[
                                                                   "task_type"] == "twitter" else "message count for each member to do daily"
    bot.sendMessage(chat_id=chat_id, text=f"Id set to : {text}\n"
                                          f"Chat type: {group_type}\n"
                                          f"Now send the {flexible_text}",
                    reply_to_message_id=update.message.message_id)
    return LIMIT


def limit(update, context):
    chat_id = update.message.chat_id
    text = update.message.text
    if text == "cancel":
        bot.sendMessage(chat_id=chat_id, text="Task creation Cancelled")
        menu_button(update, context)
        return ConversationHandler.END

    if text.isdigit():
        context.user_data["limit"] = text
        flexible_text = f"Telegram message count target set to : {text}" if context.user_data[
                                                                                "task_type"] == "telegram" else f"Twitter tweet target set to {text}"
        bot.sendMessage(chat_id=chat_id, text=f"{flexible_text}\n\n"
                                              f"Now send workers telegram handle with comma separated\n"
                                              f"NOTE: Don't include @",
                        reply_to_message_id=update.message.message_id)
        return MEMBERS_LIST
    else:
        bot.sendMessage(chat_id=chat_id, text=f"Tweet limit only can be a number, re-try",
                        reply_to_message_id=update.message.message_id)
        return LIMIT


def members_list(update, context):
    chat_id = update.message.chat_id
    text = update.message.text
    if text == "cancel":
        bot.sendMessage(chat_id=chat_id, text="Task creation Cancelled")
        menu_button(update, context)
        return ConversationHandler.END
    bot.sendMessage(chat_id=chat_id, text="Got it , Now please confirm the above details once again",
                    reply_to_message_id=update.message.message_id)
    reply_keyboard = [["confirm", "cancel"]]
    bot.sendMessage(chat_id=chat_id, text=f"Title: {context.user_data['title']}\n"
                                          f"chat_id: {context.user_data['group_id']}\n"
                                          f"task type: {context.user_data['task_type']}\n"
                                          f"Limit: {context.user_data['limit']}\n"
                                          f"Members: {text}",
                    reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True),
                    reply_to_message_id=update.message.message_id)
    context.user_data["workers"] = text
    return CONFIRM


def confirm(update, context):
    chat_id = update.message.chat_id
    text = update.message.text
    text = text.lower()
    if text == "cancel":
        bot.sendMessage(chat_id=chat_id, text="Task creation Cancelled")
        menu_button(update, context)
        return ConversationHandler.END
    username = update.message.chat.username
    if text == "confirm":
        group_id = context.user_data["group_id"]
        mem_list = context.user_data["workers"].replace(" ", "").replace('@', '').split(",")
        ref_id = db.reference('last_task').get() or {}
        get_id = 1 if 'id' not in ref_id else ref_id["id"] + 1
        db.reference(f'tasks/{group_id}').set({
            'group_id': group_id,
            'title': context.user_data['title'],
            'task_id': get_id,
            'created_by': username,
            'group_title': context.user_data['group_title'],
            'group_type': context.user_data['group_type'],
            'task_type': context.user_data['task_type'],
            'workers': mem_list
        })
        db.reference(f"task_ids/{get_id}").set({
            'task_id': get_id,
            'group_id': group_id,
            'task_type': context.user_data['group_type']
        })
        db.reference('last_task').update({'id': get_id + 1})

        bot.sendMessage(chat_id=chat_id, text=f"Task created! Task ID : {get_id}")
        menu_button(update, context)
        return ConversationHandler.END
    else:
        bot.sendMessage(chat_id=chat_id, text="Please 'confirm' or 'cancel'")
        return CONFIRM
