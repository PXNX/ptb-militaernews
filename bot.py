import logging
import os
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters, CallbackQueryHandler

PORT = int(os.environ.get('PORT', 5000))
TOKEN = '1317941240:AAHxIBg8Oq0g2dfVgTBK9PfNxa0JCNGXDXk'
CHANNEL = -1001302593973
join_usernames = []

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def start(update, context):
    update.message.reply_text("Hey :)\nIch bin noch nicht fertig!")


def new_channel_post(update: Update, context: CallbackContext):
    update.channel_post.edit_reply_markup(

        reply_markup=InlineKeyboardMarkup.from_button(InlineKeyboardButton(
            text="🔰 folge @militaernews für mehr 🔰", url="https://t.me/militaernews")))


def new_post(update: Update, context: CallbackContext, text):
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Nachricht gesendet")

    context.bot.send_message(
        chat_id=CHANNEL,
        text=text+"\nFolge @militaernews",
        reply_markup=InlineKeyboardMarkup.from_button(InlineKeyboardButton(
            text="🔰 Weitere Meldungen 🔰",
            url="https://t.me/militaernews")))


def new_member_join(update: Update, context: CallbackContext):
    update.message.delete()

    global join_usernames

    for join_user in update.message.new_chat_members:

        if join_user.name is not None:
            join_user_name = join_user.name
        else:
            join_user_name = join_user.full_name

        join_usernames.append(join_user_name)

    if len(join_usernames) >= 15:
        update.message.reply_text(
            text="Hi {} 🤖\nWelcome to the group.\n\n"
                 "<u>Group's rules</u>"
                 "\n\n<b>1. Language</b>"
                 "\nPlease use English or Hindi as an alternative."
                 "\n\n<b>2. Links</b>"
                 "\nSending links is not permitted."
                 "\n\n<b>3. Forwarding</b>"
                 "\nForwarding messages from other channels is not permitted"
                 "\n\n<b>4. Respect</b>"
                 "\nWe're all one big community. Don't be rude."
                 "\n\n<b>5. Spam</b>"
                 "\nAvoid sending stuff multiple times. Flooding the chat won't give you more attention."
                 "\n\n<b>6. Files</b>"
                 "\nAvoid sending files over 50Mb, if not ultimately needed."
                 "\n\n<b>7. Advertisements</b>"
                 "\nSelf-promotion is not permitted."
                 "\n\n<b>8. Content</b>"
                 "\nGore, porn and anything alike is absolutely prohibited.".format(', '.join(join_usernames)),
            parse_mode=telegram.ParseMode.HTML)
        join_usernames = []


# def post(update: Update, context: CallbackContext):


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
        chat_id= -466851941,
        text="Error @"+context.bot.username+"\n\nCaused by Update <code>"+str(update)+"</code>\n\nError: <code>"+str(context.error)+"</code>",
        parse_mode=telegram.ParseMode.HTML)


def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))

    dp.add_handler(MessageHandler(Filters.update.channel_post, new_channel_post))

    dp.add_handler(CommandHandler("post", new_post))

    dp.add_error_handler(error)  # REMOVE FOR STACKTRACE!!

    updater.start_webhook(listen="0.0.0.0", port=int(PORT), url_path=TOKEN)
    updater.bot.setWebhook('https://ptb-militaernews.herokuapp.com/' + TOKEN)

    updater.idle()


if __name__ == '__main__':
    main()
