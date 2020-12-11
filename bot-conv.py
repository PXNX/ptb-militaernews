import logging
import os

from telegram import (
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update, ParseMode,
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton)
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

NEWS, PHOTO, PUBLISH = range(3)


def verify(message: Message, context: CallbackContext):
    current_chat_id = message.chat_id
    if current_chat_id in set(VERIFIED_USERS):
        return True
    else:
        context.bot.send_message(chat_id=current_chat_id, text="⚠️You're not a verfied user.")


def start(update: Update, context: CallbackContext):
    if verify(update.message, context):
        update.message.reply_text('Choose the post type.', reply_markup=START_KEYBOARD)


def new_post(update: Update, context: CallbackContext) -> int:
    if verify(update.message, context):
        context.user_data["breaking"] = False
        return message_new(update,context, "🕓 <u>New scheduled post</u>")


def new_breaking(update: Update, context: CallbackContext) -> int:
    if verify(update.message, context):
        context.user_data["breaking"] = True
        return message_new(update, context, "‼️ <u>New breaking news</u>")


def message_new(update: Update, context: CallbackContext, text) -> int:
    message_html(update, context,
                 text + "\n\n<b>Step 1 of 3</b>\nSend the news in one message.")
    return NEWS


def text(update: Update, context: CallbackContext) -> int:
    if verify(update.message, context):
        context.user_data["message"] = update.message.text
        update.message.reply_text("<b>Step 2 of 3</b>\nSend all media to be added as an album.",
                                  parse_mode=ParseMode.HTML,
                                  reply_markup=ReplyKeyboardMarkup([["Use placeholder🖼️"]]))
        return PHOTO


def photo(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()
    photo_file.download('user_photo.jpg')
    logger.info("Photo of %s: %s", user.first_name, 'user_photo.jpg')

    if context.user_data["breaking"]:
        update.message.reply_text("<b>Step 3 of 3</b>\nPreview:\n\n"+context.user_data["message"],
                                  parse_mode=ParseMode.HTML,
                                  reply_markup=ReplyKeyboardMarkup([["Submit breaking📢"]],
                                                                   one_time_keyboard=True,
                                                                   resize_keyboard=True))
    else:
        update.message.reply_text("<b>Step 3 of 3</b>\nPreview:\n\n",
                                  parse_mode=ParseMode.HTML,
                                  reply_markup=ReplyKeyboardMarkup([["Schedule post📝️"]],
                                                                   one_time_keyboard=True,
                                                                   resize_keyboard=True))

    return PUBLISH


def skip_photo(update: Update, context: CallbackContext) -> int:
    if context.user_data["breaking"]:
        update.message.reply_text("<b>Step 3 of 3</b>\nPreview:\n\n",
                                  parse_mode=ParseMode.HTML,
                                  reply_markup=ReplyKeyboardMarkup([["Submit breaking📢"]],
                                                                   one_time_keyboard=True,
                                                                   resize_keyboard=True))
    else:
        update.message.reply_text("<b>Step 3 of 3</b>\nPreview:\n\n",
                                  parse_mode=ParseMode.HTML,
                                  reply_markup=ReplyKeyboardMarkup([["Schedule post📝️"]],
                                                                   one_time_keyboard=True,
                                                                   resize_keyboard=True))

    return PUBLISH


## What about SUBMIT and CANCEL instead?


def publish_breaking(update: Update, context: CallbackContext) -> int:
    broadcast_html(
        context,
        "#EILMELDUNG ‼️\n\n" + context.user_data["message"] + "\nFolge @militaernews")

    return publish_success(update, context)


def publish_post(update: Update, context: CallbackContext) -> int:
    broadcast_html(
        context,
        "hhh" + "\nFolge @militaernews")

    return publish_success(update, context)


def publish_success(update: Update, context: CallbackContext) -> int:
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Nachricht gesendet")

    return ConversationHandler.END


def broadcast_html(context: CallbackContext, text):
    context.bot.send_message(
        chat_id=CHANNEL,
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup.from_button(InlineKeyboardButton(
            text="🔰 Weitere Meldungen 🔰",
            url="https://t.me/militaernews")))


def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        text='<b>Editing this post was canceled.</b> 🗑\n\nFeel free to create a new one.',
        parse_mode=ParseMode.HTML,
        reply_markup=START_KEYBOARD, one_time_keyboard=True, resize_keyboard=True)

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

    dp.add_handler(CommandHandler('start', start))

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('Breaking‼️'), new_breaking),
                      MessageHandler(Filters.regex('Scheduled🕓'), new_post)],
        states={
            NEWS: [MessageHandler(Filters.regex('.*'), text)],
            PHOTO: [MessageHandler(Filters.photo, photo),
                    MessageHandler(Filters.regex('Use placeholder🖼️'), skip_photo)],
            PUBLISH: [MessageHandler(Filters.regex('Submit breaking📢'), publish_breaking),
                      MessageHandler(Filters.regex('Schedule post📝'), publish_post)]},
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dp.add_handler(conv_handler)

    #  dp.add_error_handler(error)

    updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN)
    updater.bot.setWebhook('https://ptb-militaernews.herokuapp.com/' + TOKEN)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
