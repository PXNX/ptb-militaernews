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
        context.bot.send_message(chat_id=current_chat_id, text="You're not a verfied user.")


# do stuff


def start(update, context):
    update.message.reply_text("Hey :)\nIch bin noch nicht fertig!")


def new_channel_post(update: Update, context: CallbackContext):
    update.channel_post.edit_reply_markup(

        reply_markup=InlineKeyboardMarkup.from_button(InlineKeyboardButton(
            text="🔰 folge @militaernews für mehr 🔰", url="https://t.me/militaernews")))


def new_post(update: Update, context: CallbackContext):
    #  query = update.callback_query
    #  querydata = query.data

    if verify(update.message, context):
        context.user_data["step"] = 1

        context.bot.send_message(
            chat_id=update.message.chat_id,
            text="<u>🕓 New scheduled post</u>"
                 "\n\n<b>Step " + str(context.user_data["step"]) + " of 3</b>" +
                 "\nNow send the news in one message, please.",
            parse_mode=telegram.ParseMode.HTML
        )


def new_breaking(update: Update, context: CallbackContext):
    context.user_data["step"] = 1

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text="<u>‼️ New breaking news</u>"
             "\n\n<b>Step " + str(context.user_data["step"]) + " of 3</b>" +
             "\nNow send the news in one message, please.",
        parse_mode=telegram.ParseMode.HTML
    )


def incoming_text(update: Update, context: CallbackContext):
    if context.user_data["step"] == 1:
        choose_country(update, context, update.message.text)
    elif context.user_data["step"] == 2:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text="jetz sollte man Bilder etc. schicken",
            parse_mode=telegram.ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup.from_button(InlineKeyboardButton(
                text="Submit post",
                callback_data="3"
            )
            ))


def submit(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    position = int(query.data)

    if position == 3:
        buttons = InlineKeyboardMarkup.from_button(
            InlineKeyboardButton("Proceed ➡", callback_data=str(position + 1)))

    query.edit_message_text(text="hmmmm",
                            reply_markup=InlineKeyboardMarkup.from_button(
                                InlineKeyboardButton(text="Submit post", callback_data="4")),
                            parse_mode=telegram.ParseMode.HTML)
    query.answer()


def choose_country(update: Update, context: CallbackContext, text):
    context.user_data["step"] = 2

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text="<u>‼️ New breaking news</u>"
             "\n\n<b>Step " + str(context.user_data["step"]) + " of 3</b>" +
             "\nPlease list the countries - oder soll das direkt in die Nachricht eingebaut werden und dann nur die Hashtags automatisch dazu?",
        parse_mode=telegram.ParseMode.HTML
    )


def publish_post(update: Update, context: CallbackContext, text):
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Nachricht gesendet")

    context.bot.send_message(
        chat_id=CHANNEL,
        text=text + "\nFolge @militaernews",
        reply_markup=InlineKeyboardMarkup.from_button(InlineKeyboardButton(
            text="🔰 Weitere Meldungen 🔰",
            url="https://t.me/militaernews")))


def publish_breaking(update: Update, context: CallbackContext, text):
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Nachricht gesendet")

    context.bot.send_message(
        chat_id=CHANNEL,
        text="#EILMELDUNG ‼️" + text + "\nFolge @militaernews",
        reply_markup=InlineKeyboardMarkup.from_button(InlineKeyboardButton(
            text="🔰 Weitere Meldungen 🔰",
            url="https://t.me/militaernews")))


def message_button_url(update, context, text, button_text, button_url):
    return context.bot.send_message(chat_id=update.message.chat_id,
                                    text=text,
                                    parse_mode=telegram.ParseMode.HTML,
                                    reply_markup=InlineKeyboardMarkup.from_button(
                                        InlineKeyboardButton(text=button_text, url=button_url)))


def message_html(update, context, text):
    return context.bot.send_message(chat_id=update.message.chat_id,
                                    text=text,
                                    parse_mode=telegram.ParseMode.HTML)


def delay_group_button_url(update, context, text, button_text, button_url):
    # update.message.delete() # TODO REQUIRES ADMIN!!!

    if update.message.chat_id == -1001374176745:
        reply_message = message_button_url(update, context, text, button_text, button_url)

    else:
        reply_message = message_button_url(update,
                                           context,
                                           "Command can only be used in the community support group.",
                                           "Join »",
                                           "https://t.me/realme_support")

    context.job_queue.run_once(delete, 300, context=update.message.chat_id, name=str(reply_message.message_id))


def delay_group(update, context, text):
    # update.message.delete() # REQUIRES ADMIN!!!

    if update.message.chat_id == -1001374176745:
        reply_message = message_html(update, context, text)
    else:
        reply_message = message_button_url(update,
                                           context,
                                           "Command can only be used in the community support group.",
                                           "Join »",
                                           "https://t.me/realme_support")

    context.job_queue.run_once(delete, 300, context=update.message.chat_id, name=str(reply_message.message_id))


def delete(context):
    context.bot.delete_message(chat_id=context.job.context, message_id=context.job.name)


def error(update: Update, context: CallbackContext):
    logger.warning('Update "%s" caused error "%s"', update, context.error)
    context.bot.send_message(
        chat_id=-1001338514957,
        text="<b>Affected Bot</b>\n@" + context.bot.username +
             "\n\n<b>Error</b>\n<code>" + str(context.error) +
             "</code>\n\n<b>Caused by Update</b>\n<code>" + str(update) + "</code>",
        parse_mode=telegram.ParseMode.HTML)


def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))

    dp.add_handler(MessageHandler(Filters.update.channel_post, new_channel_post))

    dp.add_handler(CommandHandler("post", new_post))
    dp.add_handler(CommandHandler("breaking", new_breaking))

    dp.add_handler(MessageHandler(Filters.text, incoming_text))

    # dp.add_handler(MessageHandler(Filters.a, incoming_media))

    dp.add_handler(CallbackQueryHandler(submit))

    dp.add_error_handler(error)  # REMOVE FOR STACKTRACE!!

    updater.start_webhook(listen="0.0.0.0", port=int(PORT), url_path=TOKEN)
    updater.bot.setWebhook('https://ptb-militaernews.herokuapp.com/' + TOKEN)

    updater.idle()


if __name__ == '__main__':
    main()
