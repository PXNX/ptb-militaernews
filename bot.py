import logging
import os

import telegram
from telegram.ext import Updater, CommandHandler

PORT = int(os.environ.get('PORT', 5000))
TOKEN = '1450084028:AAFrf_3POpIlYRBXad4ROWzbwswo9c026Dk'
GROUP = -1001374176745  # -1001327617858

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def start(update, context):
    update.message.reply_text("Hello user!")
    print("Bot was started by user.")


def message_html(update, context, text):
    return context.bot.send_message(chat_id=update.message.chat_id,
                                    text=text,
                                    parse_mode=telegram.ParseMode.HTML)


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_error_handler(error)

    updater.start_webhook(listen="0.0.0.0", port=int(PORT), url_path=TOKEN)
    updater.bot.setWebhook('https://nx2bot.ddns.net/' + TOKEN)

    print("bot")

    updater.idle()


if __name__ == '__main__':
    main()