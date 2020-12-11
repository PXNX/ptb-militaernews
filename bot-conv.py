import logging
import os

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, ParseMode, Message
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

PORT = int(os.environ.get('PORT', 5000))
TOKEN = '1317941240:AAHxIBg8Oq0g2dfVgTBK9PfNxa0JCNGXDXk'
CHANNEL = -1001302593973
VERIFIED_USERS = [703453307, 525147382]

START_KEYBOARD = ReplyKeyboardMarkup(
    [['Breaking‼️', 'Scheduled🕓']],
    one_time_keyboard=True,
    resize_keyboard=True)  # resize for small keyboards

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)

TEXT, PHOTO, LOCATION, BIO = range(4)


def verify(message: Message, context: CallbackContext):
    current_chat_id = message.chat_id
    if current_chat_id in set(VERIFIED_USERS):
        return True
    else:
        context.bot.send_message(chat_id=current_chat_id, text="⚠️You're not a verfied user.")


def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Choose the post type.', reply_markup=START_KEYBOARD)

    return TEXT


def new_post(update: Update, context: CallbackContext):
    if verify(update.message, context):
        message_html(update,
                     context,
                     "<u>🕓 New scheduled post</u>\n\n<b>Step 1 of 3</b>\nNow send the news in one message, please.")


def new_breaking(update: Update, context: CallbackContext):
    if verify(update.message, context):
        message_html(update,
                     context,
                     "<u>‼️ New breaking news</u>\n\n<b>Step 1 of 3</b>\nNow send the news in one message, please.")


def gender(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("Gender of %s: %s", user.first_name, update.message.text)
    update.message.reply_text(
        'I see! Please send me a photo of yourself, '
        'so I know what you look like, or send /skip if you don\'t want to.',
        reply_markup=ReplyKeyboardRemove(),
    )

    return PHOTO


def photo(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()
    photo_file.download('user_photo.jpg')
    logger.info("Photo of %s: %s", user.first_name, 'user_photo.jpg')
    update.message.reply_text(
        'Gorgeous! Now, send me your location please, ' 'or send /skip if you don\'t want to.'
    )

    return LOCATION


def skip_photo(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s did not send a photo.", user.first_name)
    update.message.reply_text(
        'I bet you look great! Now, send me your location please, ' 'or send /skip.'
    )

    return LOCATION


def location(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    user_location = update.message.location
    logger.info(
        "Location of %s: %f / %f", user.first_name, user_location.latitude, user_location.longitude
    )
    update.message.reply_text(
        'Maybe I can visit you sometime! ' 'At last, tell me something about yourself.'
    )

    return BIO


def skip_location(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s did not send a location.", user.first_name)
    update.message.reply_text(
        'You seem a bit paranoid! ' 'At last, tell me something about yourself.'
    )

    return BIO


def bio(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("Bio of %s: %s", user.first_name, update.message.text)
    update.message.reply_text('Thank you! I hope we can talk again some day.')

    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Editing this post was canceled. 🗑', reply_markup=START_KEYBOARD)

    return ConversationHandler.END


def message_html(update, context, text):
    return context.bot.send_message(chat_id=update.message.chat_id,
                                    text=text,
                                    parse_mode=ParseMode.HTML)


def error(update: Update, context: CallbackContext):
    logger.warning('Update "%s" caused error "%s"', update, context.error)
    context.bot.send_message(
        chat_id=-1001338514957,
        text="<b>🤖 Affected Bot</b>\n@" + context.bot.username +
             "\n\n<b>⚠ Error</b>\n<code>" + str(context.error) +
             "</code>\n\n<b>Caused by Update</b>\n<code>" + str(update) + "</code>",
        parse_mode=ParseMode.HTML)


def main() -> None:
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary

    updater = Updater(TOKEN)
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],  ## cancel == entrypoint, too?
        states={
            TEXT: [MessageHandler(Filters.regex('Breaking‼️'), new_breaking),
                   MessageHandler(Filters.regex('Scheduled🕓'), new_post)],
            PHOTO: [MessageHandler(Filters.photo, photo), CommandHandler('skip', skip_photo)],
            LOCATION: [
                MessageHandler(Filters.location, location),
                CommandHandler('skip', skip_location),
            ],
            BIO: [MessageHandler(Filters.text & ~Filters.command, bio)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dp.add_handler(conv_handler)

    dp.add_error_handler(error)

    updater.start_webhook(listen="0.0.0.0", port=int(PORT), url_path=TOKEN)
    updater.bot.setWebhook('https://ptb-militaernews.herokuapp.com/' + TOKEN)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
