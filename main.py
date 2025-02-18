from typing import Final
import json
import os
from telegram import Update, BotCommand , BotCommandScopeChat, ReplyKeyboardMarkup
from telegram.ext  import (Application,
                           ContextTypes,
                           CommandHandler,
                           MessageHandler,
                           filters)


TOKEN: Final = os.getenv("API_KEY")
BOT_NAME: Final = "File_Linker_bot"
SAVE_LINKS: Final = os.getenv("LINKS_KEY")
BOT_ID = os.getenv("BOT_ID")
ADMIN_ID: Final = int(os.getenv("ADMIN_ID"))
links = "http://t.me/File_Linker_bot?start="
send_messages = set()

# connect to database

def add_chat_id(new_id):
    try:
        # خواندن اطلاعات قبلی از فایل
        with open("users.json", "r", encoding="utf-8") as file:
            data = json.load(file)

        # بررسی اگر ID قبلاً ذخیره نشده باشد، آن را اضافه کن
        if new_id not in data["chat_id"]:
            data["chat_id"].append(new_id)

            # ذخیره تغییرات در فایل
            with open("users.json", "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)



    except FileNotFoundError:
        print("فایل JSON پیدا نشد، ایجاد یک فایل جدید...")
        data = {"chat_id": [new_id]}
        with open("users.json", "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        print(f"ID {new_id} اضافه شد.")


# commands
async def start_command(update: Update, context:ContextTypes.DEFAULT_TYPE):
    print(update.message.chat.id)
    chat_id = update.effective_chat.id

    add_chat_id(chat_id)

    if update.message.chat.id == ADMIN_ID:
        command = [BotCommand("admin", "فرستادن پیام همگانی"),
                   BotCommand("check", "برسی تعداد ارسال"),
                   BotCommand("users","لیست کاربران")]
        scope = BotCommandScopeChat(chat_id=ADMIN_ID)
        await app.bot.set_my_commands(command,scope=scope)

        pass
    if context.args:
        msg_id = context.args[0]
        chat_id = update.message.chat_id
        await context.bot.forward_message(from_chat_id=SAVE_LINKS,
                                          chat_id=chat_id,message_id=msg_id),
    else:
        await update.message.reply_text("""hi welcome to this bot!
just send me the file and get the file!! 
files will send with the bot""")

async def admin_command(update:Update, context:ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if update.message.chat.id == ADMIN_ID:
        button = [["بازگشت"]]
        reply_markup = ReplyKeyboardMarkup(button,resize_keyboard=True)
        await context.bot.send_message(chat_id=chat_id,text="پیام همگانی خود را ارسال کنید.", reply_markup=reply_markup)
        context.user_data["send_sms"] = True

async def check_send_messages(update:Update, context:ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    global send_messages
    if chat_id == ADMIN_ID:
        await context.bot.send_message(chat_id=ADMIN_ID,text=f"پیام شما به {len(send_messages)} نفر ارسال شد")
        print(send_messages)
        send_messages = set()
        print(send_messages)

async def check_users(update:Update, context:ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id == ADMIN_ID:
        with open("users.json", "r") as file:
            data = json.load(file)
        users = data["chat_id"]

        if users:
            chat_ids = "\n".join(str(user) for user in users)
            await context.bot.send_message(chat_id=ADMIN_ID, text=f"📋 لیست چت آیدی ها:\n{chat_ids}")
        else:
            await context.bot.send_message(chat_id=ADMIN_ID, text="❌ هیچ کاربری ثبت نشده است.")


async def document_handler(update: Update, context:ContextTypes.DEFAULT_TYPE):
    file = update.message

    chat_id = update.effective_chat.id

    add_chat_id(chat_id)

    msg_id = await context.bot.forward_message(chat_id=SAVE_LINKS,
                                               message_id=file.message_id,
                                               from_chat_id=chat_id)

    await update.message.reply_text(f"""here is your link! 😊 \n{links}{msg_id.message_id}""")

async def pic_handler(update: Update, context:ContextTypes.DEFAULT_TYPE):
    file = update.message
    file_id = file.photo

    chat_id = update.effective_chat.id

    add_chat_id(chat_id)

    msg_id = await context.bot.forward_message(chat_id=SAVE_LINKS,
                                                   message_id=file.message_id,
                                                   from_chat_id=chat_id)

    await update.message.reply_text(f"""here is your link! 😊 \n{links}{msg_id.message_id}""")

async def audio_handler(update: Update, context:ContextTypes.DEFAULT_TYPE):
    file = update.message
    file_id = file.audio.file_id

    chat_id = update.effective_chat.id

    add_chat_id(chat_id)

    msg_id = await context.bot.forward_message(chat_id=SAVE_LINKS,
                                               message_id=file.message_id,
                                               from_chat_id=chat_id)

    await update.message.reply_text(f"""here is your link! 😊 \n{links}{msg_id.message_id}""")

async def video_handler(update: Update, context:ContextTypes.DEFAULT_TYPE):
    file = update.message

    chat_id = update.effective_chat.id

    add_chat_id(chat_id)
    msg_id = await context.bot.forward_message(chat_id=SAVE_LINKS,
                                               message_id=file.message_id,
                                               from_chat_id=chat_id)

    await update.message.reply_text(f"""here is your link! 😊 \n{links}{msg_id.message_id}""")

# message handler

async def message_handler(update:Update, context:ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    add_chat_id(chat_id)
    with open("users.json", "r") as file:
        data = json.load(file)
    print(data["chat_id"])
    users = data["chat_id"]

    global send_messages

    if chat_id == ADMIN_ID:
        text = update.message.text
        if text == "بازگشت":
            context.user_data["send_sms"] = False
            await context.bot.send_message(chat_id=chat_id, text="پیام همگانی لغو شد")
        elif context.user_data.get("send_sms"):
            context.user_data["send_sms"] = False
            for user in users:
                await context.bot.send_message(chat_id=user,text=text)
                if user not in send_messages:
                    send_messages.add(user)
            await check_send_messages(update,context)


if __name__ == "__main__":
    print("starting ...")
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("admin", admin_command))
    app.add_handler(CommandHandler("check", check_send_messages))
    app.add_handler(CommandHandler("users", check_users))

    app.add_handler(MessageHandler(filters.Document.ALL, document_handler))
    app.add_handler(MessageHandler(filters.PHOTO, pic_handler))
    app.add_handler(MessageHandler(filters.AUDIO, audio_handler))
    app.add_handler(MessageHandler(filters.VIDEO, video_handler))
    app.add_handler(MessageHandler(filters.TEXT, message_handler))

    print("polling...")
    app.run_polling()
