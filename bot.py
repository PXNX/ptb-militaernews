import logging
import os
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters, CallbackQueryHandler

PORT = int(os.environ.get('PORT', 5000))
TOKEN = '1317941240:AAHxIBg8Oq0g2dfVgTBK9PfNxa0JCNGXDXk'
CHANNEL = -1001302593973
VERIFIED_USERS = [703453307, 525147382]

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def verify(message: telegram.Message, context: CallbackContext):
    current_chat_id = message.chat_id
    if current_chat_id in set(VERIFIED_USERS):
        return True
    else:
        context.bot.send_message(chat_id=current_chat_id, text="⚠️You're not a verfied user.")


def start(update, context):
    if verify(update.message, context):
        message_html(update,
                     context,
                     "Welcome human 🤖\nI'm here to ease the process of publishing for "
                     "@militaernews.\n\n/post\nSchedule a post 🕓\n\n/breaking\nPublish breaking "
                     "news ‼\n\n/cancel\nCancel current editing session 🗑️")


def new_post(update: Update, context: CallbackContext):
    if verify(update.message, context):
        context.user_data["step"] = 1
        context.user_data["breaking"] = False

        message_html(update,
                     context,
                     "<u>🕓 New scheduled post</u>\n\n<b>Step " + str(context.user_data["step"]) +
                     " of 3</b>\nNow send the news in one message, please.")


def new_breaking(update: Update, context: CallbackContext):
    if verify(update.message, context):
        context.user_data["step"] = 1
        context.user_data["breaking"] = True

        message_html(update,
                     context,
                     "<u>‼️ New breaking news</u>\n\n<b>Step " + str(context.user_data["step"]) +
                     " of 3</b>\nNow send the news in one message, please.")


def incoming_text(update: Update, context: CallbackContext):
    current_step = context.user_data["step"]
    if current_step == 0:
        message_html(update,
                     context,
                     "Please start a new editing session first.\n\n/post\nSchedule a post 🕓\n\n/breaking\nPublish "
                     "breaking news ‼")  ##replace with buttons??

    elif current_step == 1:
        context.user_data["message"] = update.message.text
        choose_country(update, context, update.message.text)

    elif current_step == 2:
        message_html(update,
                     context,
                     "<b>Step " + str(context.user_data["step"]) +
                     " of 3</b>\nNow send media as one album, please.")

        context.user_data["step"] = 3  ## remove that^^ increase after album received.

    elif current_step == 3:  ##Sending media album on step 3 actually^^
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Please check for spelling mistakes and make sure everything is properly formatted before proceeding.",
            parse_mode=telegram.ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup.from_button(InlineKeyboardButton(
                text="Submit post 📝",
                callback_data="1"
            )
            ))


def submit(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    position = int(query.data)

    if position == 1:

        text = context.user_data["message"] ###add country or so here??

        if context.user_data["breaking"]:
            publish_breaking(update, context, text)
        else:
            publish_post(update, context, "Pizza ist toll!")
            # todo make this method handle to full publishing process
            # - maybe not smart as one will be sent directly and the other scheduled :)
        update.message.edit_text(
            "HUUU")  ###########TODO find out what's the correct message to get rid of that button :)

    query.answer()


def choose_country(update: Update, context: CallbackContext, text):
    context.user_data["step"] = 2

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text="<u>‼️ New breaking news</u>"
             "\n\n<b>Step " + str(context.user_data["step"]) + " of 3</b>" +
             "\nPlease list the countries - oder soll das direkt in die Nachricht eingebaut werden und dann nur die "
             "Hashtags automatisch dazu?",
        parse_mode=telegram.ParseMode.HTML
    )


def publish_post(update: Update, context: CallbackContext, text):
    broadcast_html(
        context,
        text + "\nFolge @militaernews")

    context.user_data["step"] = 0

    update.message.edit_text(
        "Nachricht gesendet")  ###########TODO find out what's the correct message to get rid of that button :)

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Nachricht gesendet")


def publish_breaking(update: Update, context: CallbackContext, text):
    broadcast_html(
        context,
        "#EILMELDUNG ‼️\n\n" + text + "\nFolge @militaernews")

    context.user_data["step"] = 0

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Nachricht gesendet")


# Maybe add button to choose between new post and new breaking :)


def cancel_editing(update: Update, context: CallbackContext):
    if verify(update.message, context):
        context.user_data["step"] = 0
        context.user_data["message"] = ""

        message_html(
            update,
            context,
            "Editing this post was canceled. 🗑")


def broadcast_html(context: CallbackContext, text):
    context.bot.send_message(
        chat_id=CHANNEL,
        text=text,
        parse_mode=telegram.ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup.from_button(InlineKeyboardButton(
            text="🔰 Weitere Meldungen 🔰",
            url="https://t.me/militaernews")))


def message_html(update, context, text):
    return context.bot.send_message(chat_id=update.message.chat_id,
                                    text=text,
                                    parse_mode=telegram.ParseMode.HTML)


def error(update: Update, context: CallbackContext):
    logger.warning('Update "%s" caused error "%s"', update, context.error)
    context.bot.send_message(
        chat_id=-1001338514957,
        text="<b>🤖 Affected Bot</b>\n@" + context.bot.username +
             "\n\n<b>⚠ Error</b>\n<code>" + str(context.error) +
             "</code>\n\n<b>Caused by Update</b>\n<code>" + str(update) + "</code>",
        parse_mode=telegram.ParseMode.HTML)


def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))

    dp.add_handler(CommandHandler("post", new_post))
    dp.add_handler(CommandHandler("breaking", new_breaking))
    dp.add_handler(CommandHandler("cancel", cancel_editing))

    dp.add_handler(MessageHandler(Filters.text, incoming_text))

    # dp.add_handler(MessageHandler(Filters.a, incoming_media))

    dp.add_handler(CallbackQueryHandler(submit))

    #   dp.add_error_handler(error)  # REMOVE FOR STACKTRACE!!

    updater.start_webhook(listen="0.0.0.0", port=int(PORT), url_path=TOKEN)
    updater.bot.setWebhook('https://ptb-militaernews.herokuapp.com/' + TOKEN)

    updater.idle()


if __name__ == '__main__':
    main()
