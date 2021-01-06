import logging
import os

from telegram import (
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update, ParseMode,
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton, InputMediaPhoto, InputMediaVideo, MessageId)
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

PORT = int(os.environ.get('PORT', 5000))
TOKEN = os.environ.get('TOKEN')
CHANNEL = -1001302593973
VERIFIED_USERS = [703453307, 525147382]

START_KEYBOARD = ReplyKeyboardMarkup(
    [['Breaking news ‼️', 'Scheduled post 🕓']],
    one_time_keyboard=True,
    resize_keyboard=True)  # resize for small keyboards

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)

NEWS, PHOTO, PUBLISH = range(3)


###### Replace with Filter
def verify(message: Message, context: CallbackContext) -> bool:
    current_chat_id = message.chat_id
    if current_chat_id not in set(VERIFIED_USERS):
        context.bot.send_message(chat_id=current_chat_id, text='You\'re not a verfied user ⚠')
        return False
    return True


def start(update: Update, context: CallbackContext):
    if verify(update.message, context):
        update.message.reply_text('Choose the post type.', reply_markup=START_KEYBOARD)
        update.message.reply_html("\\<<b>bold</b>")


def new_post(update: Update, context: CallbackContext) -> int:
    if verify(update.message, context):
        context.user_data['breaking'] = False
        return message_new(update, context, '<u>New scheduled post</u> 🕓')


def new_breaking(update: Update, context: CallbackContext) -> int:
    if verify(update.message, context):
        context.user_data['breaking'] = True
        return message_new(update, context, '<u>New breaking news</u> ‼️')


def message_new(update: Update, context: CallbackContext, text: str) -> int:
    update.message.reply_text(text + '\n\n<b>Step 1 of 3</b>\nSend the news in one message',
                              parse_mode=ParseMode.HTML,
                              reply_markup=ReplyKeyboardRemove())
    return NEWS


def text(update: Update, context: CallbackContext) -> int:
    if verify(update.message, context):
        context.user_data['message'] = update.message.text
        update.message.reply_text('<b>Step 2 of 3</b>\nSend photos or videos as an album',
                                  parse_mode=ParseMode.HTML,
                                  reply_markup=ReplyKeyboardMarkup([['Use placeholder 🖼️']]))
        return PHOTO


def photo(update: Update, context: CallbackContext) -> int:
    # user = update.message.from_user
    # photo_file = update.message.photo[-1].get_file()
    #  photo_file.download('user_photo.jpg')
    #  logger.info('Photo of %s: %s', user.first_name, 'user_photo.jpg')

    if update.message.media_group_id:
        file_list = []

        #  file_list.append(photo_file.file_id) # +=

        context.user_data['files'] = file_list
    else:

        # if update.message.photo:
        context.user_data['files'] = [update.message]  # [update.message.copy(update.message.chat_id)]

    # elif update.message.video:
    #    context.user_data['files'] = [update.message.video.get_file()]

    # print(photo_file.file_id)

    #  print(update.message.copy(update.message.chat_id).message_id)

    return message_preview(update, context)


def skip_photo(update: Update, context: CallbackContext) -> int:
    context.user_data['files'] = []

    # maybe something like getting the photo from a local storage
    return message_preview(update, context)


def message_preview(update: Update, context: CallbackContext) -> int:
    msg: Message = update.message
    update.message.reply_text('<b>Step 3 of 3</b>\nPreview the generated post',
                              parse_mode=ParseMode.HTML,
                              reply_markup=ReplyKeyboardMarkup([['Submit post 📣', 'Cancel 🗑']],
                                                               one_time_keyboard=True,
                                                               resize_keyboard=True))
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=context.user_data['message'] + '\nFolge @militaernews',
        # parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup.from_button(InlineKeyboardButton(
            text='🔰 Weitere Meldungen 🔰',
            url='https://t.me/militaernews')))

    if not context.user_data['files']:
        placeholder = InputMediaPhoto(open('eilmeldung.png', 'rb'))
        #   placeholder.caption = context.user_data['message'] + '\n\n🔰 Folge @militaernews für mehr 🔰'

        # context.bot.send_media_group(update.message.chat_id,
        #                              media=[placeholder],
        #                             )
        context.bot.send_photo(
            update.message.chat_id,
            photo=open('eilmeldung.png', 'rb'),
            caption=context.user_data['message'] + '\n\nFolge @militaernews',
            reply_markup=InlineKeyboardMarkup.from_button(
                InlineKeyboardButton(text='🔰 Weitere Meldungen 🔰', url='https://t.me/militaernews')))

    elif len(context.user_data['files']) == 1:

        context.bot.send_message(update.message.chat_id, text='ein Bild')

    else:

        context.bot.send_message(update.message.chat_id, text='Media Group')

        #  firstFile = context.user_data['files'][0]

        #  first_file_caption: InputMediaPhoto = context.user_data['files'][0]

        # if firstFile[1] == 0:
        #     firstFileWithCaption: InputMediaPhoto = firstFile

        #  elif firstFile[1] == 1:
        #      firstFileWithCaption: InputMediaVideo = firstFile

        #  context.user_data['files'][0].caption = context.user_data['message']

        #  context.user_data['files'][0].caption = context.user_data['message']

        #  currFile: MessageId = context.user_data['files'][0]

        #   currFile.caption = 'HAW'

        # currmsg: Message = currFile

        currmsg: Message = context.user_data['files'][0]

        ## currmsg.caption = 'HAAAA'

        currFile: InputMediaPhoto = currmsg.photo[2].get_file()

        currmsg.caption = 'rgsgg'

        currmsg.parse_mode = ParseMode.HTML

        context.bot.sendMediaGroup()
        context.bot.send_media_group(update.message.chat_id,
                                     media=[InputMediaPhoto(currmsg.photo[2].get_file().file_id)])

    return PUBLISH


## What about SUBMIT and CANCEL instead?


def publish(update: Update, context: CallbackContext) -> int:
    if context.user_data['breaking']:
        broadcast_html(
            context,
            '#EILMELDUNG ‼️\n\n' + context.user_data['message'] + '\nFolge @militaernews')
    else:
        context.bot.send_message(
            chat_id=CHANNEL,
            text=context.user_data['message'] + '\nFolge @militaernews',
            parse_mode=ParseMode.HTML,

            reply_markup=InlineKeyboardMarkup.from_button(InlineKeyboardButton(
                text='🔰 Weitere Meldungen 🔰',
                url='https://t.me/militaernews')))

    return publish_success(update, context)


def publish_post(update: Update, context: CallbackContext) -> int:
    broadcast_html(
        context,
        'hhh' + '\nFolge @militaernews')

    return publish_success(update, context)


def broadcast_html(context: CallbackContext, text):
    context.bot.send_message(
        chat_id=CHANNEL,
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup.from_button(InlineKeyboardButton(
            text='🔰 Weitere Meldungen 🔰',
            url='https://t.me/militaernews')))


def publish_success(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('<b>Message sent</b> ✅\nCompose a new one?',
                              parse_mode=ParseMode.HTML,
                              reply_markup=START_KEYBOARD)
    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        text='<b>Editing this post was cancelled</b> 🗑\nFeel free to create a new one',
        parse_mode=ParseMode.HTML,
        reply_markup=START_KEYBOARD)
    return ConversationHandler.END


def message_html(update, context, text):
    return context.bot.send_message(chat_id=update.message.chat_id,
                                    text=text,
                                    parse_mode=ParseMode.HTML)


def error(update: Update, context: CallbackContext):
    logger.warning('Update %s caused error %s', update, context.error)
    context.bot.send_message(
        chat_id=-1001338514957,
        text='<b>🤖 Affected Bot</b>\n@' + context.bot.username +
             '\n\n<b>⚠ Error</b>\n<code>' + str(context.error) +
             '</code>\n\n<b>Caused by Update</b>\n<code>' + str(update) + '</code>',
        parse_mode=ParseMode.HTML)


def main() -> None:
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary

    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start, filters=Filters.chat(chat_id=VERIFIED_USERS)))

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('Breaking news ‼️'), new_breaking),
                      MessageHandler(Filters.regex('Scheduled post 🕓'), new_post)],
        states={
            NEWS: [MessageHandler(Filters.regex('.*'), text)],
            PHOTO: [MessageHandler(Filters.photo, photo),
                    MessageHandler(Filters.regex('Use placeholder 🖼️'), skip_photo)],  # skip placeholder?
            PUBLISH: [MessageHandler(Filters.regex('Submit post 📣'), publish)]},
        fallbacks=[MessageHandler(Filters.regex('Cancel 🗑'), cancel), CommandHandler('start', start)],
    )

    dp.add_handler(conv_handler)

    #  dp.add_error_handler(error)

    updater.start_webhook(listen='0.0.0.0', port=PORT, url_path=TOKEN)
    updater.bot.setWebhook('https://ptb-militaernews.herokuapp.com/' + TOKEN)

    updater.start_polling()##
    updater.idle()


if __name__ == '__main__':
    main()
