import time

from telegram import Update
from telegram.ext import CallbackContext, MessageHandler, Filters, Updater

from config import PORT


def forward_test(update: Update, _: CallbackContext):
    for i in GROUPS:
        update.channel_post.forward(i)
        time.sleep(3)


GROUPS = (-1001316223163, -522695460)
TOKEN = "1841878701:AAGPtMPKrANXCR8XnhGa5pSKW4EdYMYJFz4"
CHANNEL_ID = -1001367773728

if __name__ == '__main__':
    updater = Updater(TOKEN)

    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.update.channel_post & Filters.chat(CHANNEL_ID), forward_test))
    updater.start_webhook("0.0.0.0", PORT, TOKEN, webhook_url='https://ptb-militaernews.herokuapp.com/' + TOKEN)

    #   updater.start_polling()
    updater.idle()
