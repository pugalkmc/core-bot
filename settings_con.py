from functions import *

TWITTER_UPDATE, TWITTER_UPDATE_LIST, TWITTER_UPDATE_CONFIRM = range(3)


def twitter_ids(update, context):
    message = update.message
    chat_id = message.chat_id
    username = message.from_user.username
    text = message.text
    reply_keyboard = [["Update ID's", "My id's"], ['main menu']]
    bot.sendMessage(chat_id=chat_id, text="Twitter settings",
                    reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                     one_time_keyboard=True),
                    reply_to_message_id=update.message.message_id)
    return TWITTER_UPDATE


def twitter_update(update, context):
    message = update.message
    chat_id = message.chat_id
    username = message.from_user.username
    text = message.text
    text = text.lower()
    if "update id's" == text:
        reply_keyboard = [['cancel']]
        bot.sendMessage(chat_id=chat_id, text="Now send the all twitter usernames comma(,) separated including "
                                              "previously added id's\n"
                                              "Example: @pugalkmc , @sarankmc",
                        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                         one_time_keyboard=True),
                        reply_to_message_id=update.message.message_id)
        return TWITTER_UPDATE_LIST
    elif "my id's" == text:
        get_ids = db.reference(f"peoples/{chat_id}").get() or {}
        if 'twitter' in get_ids:
            form_text = "Twitter id's list:\n"
            for i in get_ids['twitter']:
                form_text += f"@{i} "
            bot.sendMessage(chat_id=chat_id, text=form_text)
        else:
            bot.sendMessage(chat_id=chat_id, text="No twitter id's found!")
        return twitter_ids(update, context)
    elif "main menu" == text:
        menu_button(update, context)
        return ConversationHandler.END


def twitter_update_list(update, context):
    message = update.message
    chat_id = message.chat_id
    username = message.from_user.username
    text = message.text
    if "cancel" == text:
        return twitter_ids(update, context)
    ids = text.replace("@", "").replace(" ", "").split(",")
    context.user_data['twitter_ids'] = ids
    reply_keyboard = [["confirm", "cancel"]]
    bot.sendMessage(chat_id=chat_id, text=f"Twitter ID:\n"
                                          f"@{ids}\n\n"
                                          f"Please click confirm or cancel the process",
                    reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                     one_time_keyboard=True)
                    )
    return TWITTER_UPDATE_CONFIRM


def twitter_update_confirm(update, context):
    message = update.message
    chat_id = message.chat_id
    username = message.from_user.username
    text = message.text
    text = text.lower()
    if "confirm" == text:
        db.reference(f"peoples/{chat_id}").update({
            'twitter': context.user_data["twitter_ids"]
        })
        bot.sendMessage(chat_id=chat_id, text="Your twitter id's are updated")
        return twitter_ids(update, context)
    elif "cancel" == text:
        return twitter_ids(update, context)
    else:
        bot.sendMessage(chat_id=chat_id, text="Pleas correct option 'confirm' or 'cancel'")
        return TWITTER_UPDATE_CONFIRM


BINANCE_OPTIONS, SET_BINANCE = range(2)


def binance_start(update, context):
    message = update.message
    chat_id = message.chat_id
    username = message.from_user.username
    text = message.text
    text = text.lower()
    get_data = db.reference(f"peoples/{chat_id}").get() or {}
    if 'binance' in get_data:
        reply_keyboard = [["change binance", "settings"]]
        bot.sendMessage(chat_id=chat_id, text=f"Your binance ID : {get_data['binance']}",
                        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                         one_time_keyboard=True)
                        )
        context.user_data['status'] = 'not set'
    else:
        reply_keyboard = [["change binance", "settings"]]
        bot.sendMessage(chat_id=chat_id, text=f"Your binance not set",
                        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                         one_time_keyboard=True)
                        )
        context.user_data['status'] = 'set'
    return BINANCE_OPTIONS


def binance_option(update, context):
    message = update.message
    chat_id = message.chat_id
    username = message.from_user.username
    text = message.text
    text = text.lower()
    if context.user_data['status'] == 'set':
        option_1 = "change binance"
    else:
        option_1 = "set binance"

    if option_1 == text:
        reply_keyboard = [["cancel"]]
        bot.sendMessage(chat_id=chat_id, text=f"Now send the binance ID to set",
                        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                         one_time_keyboard=True)
                        )
        bot.send_photo(chat_id=chat_id, photo=open('binance_1.jpg', 'rb'))
        bot.send_photo(chat_id=chat_id, photo=open('binance_2.jpg', 'rb'))
        return SET_BINANCE
    elif "settings":
        settings(update, context)
        return ConversationHandler.END


def set_binance(update, context):
    message = update.message
    chat_id = message.chat_id
    username = message.from_user.username
    text = message.text
    text = text.lower()
    if "cancel" == text:
        menu_button(update, context)
        return ConversationHandler.END
    if text.ismuneric():
        db.reference(f"peoples/{chat_id}").update({
            'binance': text
        })
        return binance_start(update, context)
    else:
        bot.sendMessage(chat_id=chat_id, text="Binance ID must be a number")
        return SET_BINANCE
