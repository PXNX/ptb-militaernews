import logging
import os

from telegram import (
    Update, ParseMode)
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackContext,
)

PORT = int(os.environ.get('PORT', 5000))
TOKEN = os.environ.get('TOKEN') # or something like 'anwer349wrjfw45tw4rtf34t5n54z:348wrwh45th4t'
APP_NAME = 'my-fancy-heroku-app'

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext):
    update.message.reply_text('Hello Human!')


def error(update: Update, context: CallbackContext):
    logger.warning('Update %s caused error %s', update, context.error)

    # this is just to receive a notification on TG.
    # your bot will have to be in this chat!
    context.bot.send_message(
        chat_id=-1001338514957,
        text='<b>🤖 Affected Bot</b>\n@' + context.bot.username +
             '\n\n<b>⚠ Error</b>\n<code>' + str(context.error) +
             '</code>\n\n<b>Caused by Update</b>\n<code>' + str(update) + '</code>',
        parse_mode=ParseMode.HTML)


if __name__ == '__main__':
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))

    #  dp.add_error_handler(error) # Comment out to show stacktrace

    updater.start_webhook(listen='0.0.0.0', port=PORT, url_path=TOKEN)
    updater.bot.setWebhook('https://'+APP_NAME+'.herokuapp.com/' + TOKEN)
    updater.start_polling()
    updater.idle()
