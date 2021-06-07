import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from telegram.ext import Updater, MessageHandler, Filters

from config import DATABASE_URL, TOKEN, PORT, CHANNEL_MEME
from messages import *
from postgres import PostgresPersistence
from utils import remove_message

##########################################
# this file serves as an entry point to the program.
# here all the stuff is initialized.
##########################################


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def start_session() -> scoped_session:
    engine = create_engine(DATABASE_URL, client_encoding="utf8")
    return scoped_session(sessionmaker(bind=engine, autoflush=False))


def error(update: Update, context: CallbackContext):
    logger.warning('Update "%s" caused error "%s"', update, context.error)
    context.bot.send_message(-1001338514957,
                             "<b>🤖 Affected Bot</b>\n@" + context.bot.username +
                             "\n\n<b>⚠ Error</b>\n<code>" + str(context.error) +
                             "</code>\n\n<b>Caused by Update</b>\n<code>" + str(update) + "</code>",
                             ParseMode.HTML)


if __name__ == '__main__':
    session = start_session()
    updater = Updater(TOKEN, persistence=PostgresPersistence(session), use_context=True)

    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.text(
        ["/help@CoronaVirusRobot", "/victims@CoronaVirusRobot", "/infect@CoronaVirusRobot"]), remove_message))

    dp.add_handler(MessageHandler(Filters.update.channel_post & Filters.chat(CHANNEL_MEME), forward_meme))

    #  dp.add_handler(MessageHandler(Filters.update.channel_post | Filters.update.edited_channel_post, add_button))

    #  dp.add_handler(ConversationHandler(
    #    entry_points=[MessageHandler(Filters.regex('Breaking news ‼️'), new_breaking),
    #                MessageHandler(Filters.regex('Scheduled post 🕓'), new_post)],
    #   states={
    #      NEWS: [MessageHandler(Filters.text, text)],
    #      MEDIA: [MessageHandler(Filters.photo, add_photo),
    #              MessageHandler(Filters.video, add_video),
    #              MessageHandler(Filters.regex('Use placeholder 🖼️'), skip_photo),
    #             MessageHandler(Filters.regex('Done ✅'), message_preview)],
    #      PUBLISH: [MessageHandler(Filters.regex('Submit post 📣'), publish)]},
    #   fallbacks=[MessageHandler(Filters.regex('Cancel 🗑'), cancel), CommandHandler('start', start)],
    #  ))

    dp.bot.send_message(chat_id=703453307, text='BOT ONLINE ✅')

    updater.start_webhook("0.0.0.0", PORT, TOKEN, webhook_url='https://ptb-militaernews.herokuapp.com/' + TOKEN)
    updater.idle()
