from typing import Final
import mysql.connector
import os
from telegram import (Update,
                      BotCommand ,
                      BotCommandScopeChat,
                      ReplyKeyboardMarkup,
                      InlineKeyboardButton,
                      InlineKeyboardMarkup)

from telegram.ext  import (Application,
                           ContextTypes,
                           CommandHandler,
                           MessageHandler,
                           filters, CallbackQueryHandler)


TOKEN: Final = os.getenv("API_KEY")
BOT_NAME: Final = "File_Linker_bot"
SAVE_LINKS: Final = os.getenv("LINKS_KEY")
BOT_ID = os.getenv("BOT_ID")
ADMIN_ID: Final = int(os.getenv("ADMIN_ID"))
links = "http://t.me/File_Linker_bot?start="
send_messages = set()

# connect to database

DB_CONFIG = {
    "host": os.getenv("HOST"),
    "user": os.getenv("USER"),
    "password": os.getenv("PASS"),
    "database": os.getenv("DATABASE"),
    "port": int(os.getenv("PORT"))
}


# 📌 تابع اتصال به دیتابیس
def connect_db():
    return mysql.connector.connect(**DB_CONFIG)


# commands
async def start_command(update: Update, context:ContextTypes.DEFAULT_TYPE):
    print(update.message.chat.id)
    chat_id = update.effective_chat.id


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
        await context.bot.copy_message(from_chat_id=SAVE_LINKS,
                                          chat_id=chat_id,message_id=msg_id),
    else:
        buttons = [
            [InlineKeyboardButton("🇮🇷 فارسی",callback_data="fa"),
             InlineKeyboardButton("🇬🇧 English",callback_data="en")]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)

        context.user_data["lan_msg"] = await update.message.reply_text("choose your language", reply_markup=reply_markup)


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
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT chat_id FROM users")
        users = cursor.fetchall()
        conn.close()

        if users:
            chat_ids = "\n".join(str(user[0]) for user in users)
            await context.bot.send_message(chat_id=ADMIN_ID, text=f"📋 لیست چت آیدی ها:\n{chat_ids}")
        else:
            await context.bot.send_message(chat_id=ADMIN_ID, text="❌ هیچ کاربری ثبت نشده است.")


async def document_handler(update: Update, context:ContextTypes.DEFAULT_TYPE):
    file = update.message
    file_id = file.document.file_id

    chat_id = update.effective_chat.id

    if not context.user_data.get("lan"):
        conn = connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute(f"SELECT lan FROM users  WHERE chat_id={chat_id}")
            lan = cursor.fetchall()[0]
            context.user_data["lan"] = lan[0]
        except mysql.connector.Error as err:
            print(f"error caused: {err}")
        finally:
            conn.close()


    msg_id = await context.bot.forward_message(chat_id=SAVE_LINKS,
                                               message_id=file.message_id,
                                               from_chat_id=chat_id)


    if context.user_data.get("lan") == "fa":
        await update.message.reply_text(f"این هم از لینک شما😊!  \n{links}{msg_id.message_id}")
    else:
        await update.message.reply_text(f"""here is your link! 😊 \n{links}{msg_id.message_id}""")
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute(f"INSERT INTO users (chat_id) VALUE ({chat_id})")
        conn.commit()
    except mysql.connector.Error as err:
        print(f"❌ خطای MySQL: {err}")
    finally:
        conn.close()


async def pic_handler(update: Update, context:ContextTypes.DEFAULT_TYPE):
    file = update.message

    chat_id = update.effective_chat.id
    if not context.user_data.get("lan"):
        conn = connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute(f"SELECT lan FROM users  WHERE chat_id={chat_id}")
            lan = cursor.fetchall()[0]
            print(lan[0])
            context.user_data["lan"] = lan[0]
        except mysql.connector.Error as err:
            print(f"error caused: {err}")
        finally:
            conn.close()

    msg_id = await context.bot.forward_message(chat_id=SAVE_LINKS,
                                                   message_id=file.message_id,
                                                   from_chat_id=chat_id)

    if context.user_data.get("lan") == "fa":
        await update.message.reply_text(f"این هم از لینک شما😊!  \n{links}{msg_id.message_id}")
    else:
        await update.message.reply_text(f"""here is your link! 😊 \n{links}{msg_id.message_id}""")
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute(f"INSERT INTO `users` (`chat_id`, `lan`) VALUES ({chat_id},'{context.user_data.get("lan")}');", )
        conn.commit()
    except mysql.connector.Error as err:
        print(f"❌ خطای MySQL: {err}")
    finally:
        conn.close()

async def audio_handler(update: Update, context:ContextTypes.DEFAULT_TYPE):
    file = update.message
    file_id = file.audio.file_id

    chat_id = update.effective_chat.id
    if not context.user_data.get("lan"):
        conn = connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute(f"SELECT lan FROM users  WHERE chat_id={chat_id}")
            lan = cursor.fetchall()[0]
            print(lan[0])
            context.user_data["lan"] = lan[0]
        except mysql.connector.Error as err:
            print(f"error caused: {err}")
        finally:
            conn.close()

    msg_id = await context.bot.forward_message(chat_id=SAVE_LINKS,
                                               message_id=file.message_id,
                                               from_chat_id=chat_id)

    if context.user_data.get("lan") == "fa":
        await update.message.reply_text(f"این هم از لینک شما😊!  \n{links}{msg_id.message_id}")
    else:
        await update.message.reply_text(f"""here is your link! 😊 \n{links}{msg_id.message_id}""")
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute(f"INSERT INTO `users` (`chat_id`, `lan`) VALUES ({chat_id},'{context.user_data.get("lan")}');", )
        conn.commit()
    except mysql.connector.Error as err:
        print(f"❌ خطای MySQL: {err}")
    finally:
        conn.close()

async def video_handler(update: Update, context:ContextTypes.DEFAULT_TYPE):
    file = update.message
    file_id = file.video.file_id

    chat_id = update.effective_chat.id

    if not context.user_data.get("lan"):
        conn = connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute(f"SELECT lan FROM users  WHERE chat_id={chat_id}")
            lan = cursor.fetchall()[0]
            print(lan[0])
            context.user_data["lan"] = lan[0]
        except mysql.connector.Error as err:
            print(f"error caused: {err}")
        finally:
            conn.close()

    msg_id = await context.bot.forward_message(chat_id=SAVE_LINKS,
                                               message_id=file.message_id,
                                               from_chat_id=chat_id)

    if context.user_data.get("lan") == "fa":
        await update.message.reply_text(f"این هم از لینک شما😊!  \n{links}{msg_id.message_id}")
    else:
        await update.message.reply_text(f"""here is your link! 😊 \n{links}{msg_id.message_id}""")
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute(f"INSERT INTO `users` (`chat_id`, `lan`) VALUES ({chat_id},'{context.user_data.get("lan")}');", )
        conn.commit()
    except mysql.connector.Error as err:
        print(f"❌ خطای MySQL: {err}")
    finally:
        conn.close()

# message handler

async def message_handler(update:Update, context:ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT chat_id FROM users")
    users = cursor.fetchall()
    conn.close()

    global send_messages

    if chat_id == ADMIN_ID:
        text = update.message.text
        if text == "بازگشت":
            context.user_data["send_sms"] = False
            await context.bot.send_message(chat_id=chat_id, text="پیام همگانی لغو شد")
        elif context.user_data.get("send_sms"):
            context.user_data["send_sms"] = False
            for user in users:
                try:
                    await context.bot.send_message(chat_id=user[0],text=text)
                    if user[0] not in send_messages:
                        send_messages.add(user[0])
                except Exception as e:
                  await context.bot.send_message(chat_id=ADMIN_ID, text=f"پیام به این دلیل به {user[0]} ارسال نشد {e}")
            await check_send_messages(update,context)

# button handler

async def button_handler(update:Update, context:ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_id = update.effective_chat.id
    await context.bot.delete_message(chat_id=chat_id,message_id=context.user_data.get("lan_msg").message_id)
    data = query.data
    print(data)
    if data == "en":
        await context.bot.send_message(text="""hi welcome to this bot!
just send me the file and get the file!! 
files will send with the bot""",chat_id=chat_id)
        context.user_data["lan"] = "en"

        conn = connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute(f"INSERT INTO `users` (`chat_id`, `lan`) VALUES ({chat_id},'{"en"}');", )
            conn.commit()
        except mysql.connector.Error as err:
            print(f"error caused: {err}")
        finally:
            conn.close()

    elif data == "fa":
        await context.bot.send_message(text="""سلام! به ربات فایل لینکر خوش آمدید!
فقط کافیه فایلتون رو بفرستید تا لینک دانلود اون رو براتون ارسال کنم!
شما میتونین فایل ها رو از طریق خود ربات دانلود کنید.""", chat_id=chat_id)
        context.user_data["lan"] = "fa"

        conn = connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute(f"INSERT INTO `users` (`chat_id`, `lan`) VALUES ({chat_id},'{"fa"}');", )
            conn.commit()
        except mysql.connector.Error as err:
            print(f"error caused: {err}")
        finally:
            conn.close()



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
    app.add_handler(CallbackQueryHandler(button_handler))

    print("polling...")
    app.run_polling()

