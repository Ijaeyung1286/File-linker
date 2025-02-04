from typing import Final
import os
from telegram import Update
from telegram.ext  import (Application,
                           ContextTypes,
                           CommandHandler,
                           MessageHandler,
                           filters)


TOKEN: Final = os.getenv("API_KEY")
BOT_NAME: Final = "File_Linker_bot"
SAVE_LINKS: Final = -1002431540662
BOT_ID = 7660097928
links = "http://t.me/File_Linker_bot?start="

# commands
async def start_command(update: Update, context:ContextTypes.DEFAULT_TYPE):

    if context.args:
        msg_id = context.args[0]
        chat_id = update.message.chat_id
        await context.bot.forward_message(from_chat_id=SAVE_LINKS,
                                          chat_id=chat_id,message_id=msg_id),
    else:
        await update.message.reply_text("""hi welcome to this bot!
just send me the file and get the download link""")

async def document_handler(update: Update, context:ContextTypes.DEFAULT_TYPE):
    file = update.message
    file_id = file.document.file_id
    try:
        file_url = await context.bot.getFile(file_id)
        await update.message.reply_text(f"there is your link!\n{str(file_url.file_path)}")
    except Exception:
        chat_id = update.message.chat.id
        msg_id = await context.bot.forward_message(chat_id=SAVE_LINKS,
                                          message_id=file.message_id,
                                          from_chat_id=chat_id)

        await update.message.reply_text(f"""file is too big!
bot with this link you can download it with the bot from this link below!   😊
{links}{msg_id.message_id}""")

async def pic_handler(update: Update, context:ContextTypes.DEFAULT_TYPE):
    file = update.message
    file_id = file.photo
    try:
        file_url = await context.bot.get_file(file_id[-1].file_id)
        await update.message.reply_text(f"there is your link!\n{str(file_url.file_path)}")
    except Exception:
        chat_id = update.message.chat.id
        msg_id = await context.bot.forward_message(chat_id=SAVE_LINKS,
                                                   message_id=file.message_id,
                                                   from_chat_id=chat_id)

        await update.message.reply_text(f"""file is too big!
        bot with this link you can download it with the bot from this link below!   😊
        {links}{msg_id.message_id}""")

async def audio_handler(update: Update, context:ContextTypes.DEFAULT_TYPE):
    file = update.message
    file_id = file.audio.file_id
    try:
        file_url = await context.bot.get_file(file_id)
        await update.message.reply_text(f"there is your link!\n{str(file_url.file_path)}")
    except Exception:
        chat_id = update.message.chat.id
        msg_id = await context.bot.forward_message(chat_id=SAVE_LINKS,
                                                   message_id=file.message_id,
                                                   from_chat_id=chat_id)

        await update.message.reply_text(f"""file is too big!
        bot with this link you can download it with the bot from this link below!   😊
        {links}{msg_id.message_id}""")

async def video_handler(update: Update, context:ContextTypes.DEFAULT_TYPE):
    file = update.message
    file_id = file.video.file_id
    try:
        file_url = await context.bot.get_file(file_id)
        #play video url = https://ijaeyung1286.github.io/video-player/?video=
        play_url = f"https://ijaeyung1286.github.io/video-player?video={file_url.file_path}"
        await update.message.reply_text(f"Here is your links!\ndownload link:\n{str(file_url.file_path)}\nplay video link:\n{play_url}")
    except Exception:
        chat_id = update.message.chat.id
        msg_id = await context.bot.forward_message(chat_id=SAVE_LINKS,
                                                   message_id=file.message_id,
                                                   from_chat_id=chat_id)

        await update.message.reply_text(f"""file is too big!
        bot with this link you can download it with the bot from this link below!   😊
        {links}{msg_id.message_id}""")


if __name__ == "__main__":
    print("starting ...")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.Document.ALL, document_handler))
    app.add_handler(MessageHandler(filters.PHOTO, pic_handler))
    app.add_handler(MessageHandler(filters.AUDIO, audio_handler))
    app.add_handler(MessageHandler(filters.VIDEO, video_handler))
    print("polling...")
    app.run_polling()

