from functions import *

START, SELECT_TASK = range(2)


def start(update, context, task_id):
    message = update.message
    chat_id = message.chat_id
    username = message.from_user.username


def spreadsheet(update, context, chat_id, task_data=None):
    collection_name = datetime.datetime.now().strftime("%d-%m-%Y")
    wb = openpyxl.Workbook()
    ws = wb.active
    # Write the headers
    datas = db.reference(f"task_ids/{task_data}").get() or {}
    if len(datas)<=0:
        bot.sendMessage(chat_id=chat_id,text="Task id not valid!")
        return 0
    group_id = datas['group_id']
    task_type = datas['task_type']
    task_details = db.reference(f"tasks/{group_id}/collection/{collection_name}").get() or {}
    ws.column_dimensions['A'].width = 14
    ws.column_dimensions['B'].width = 40
    ws.column_dimensions['C'].width = 18
    flex_title = "Message text" if task_type == "telegram" else "tweet link"

    ws['A1'] = 'Username'
    ws['B1'] = flex_title
    ws['C1'] = 'IST Time'

    get = "link" if task_type == "twitter" else "text"
    row = 2
    for message_id, message_data in task_details.items():
        username = message_data.get('username')
        text = message_data.get(get)
        time = message_data.get('time')
        ws.cell(row=row, column=1).value = username
        ws.cell(row=row, column=2).value = text
        ws.cell(row=row, column=3).value = time
        row += 1

    wb.save(f"{collection_name}.xlsx")
    bot.sendDocument(chat_id=chat_id, document=open(f"{collection_name}.xlsx", "rb"))
