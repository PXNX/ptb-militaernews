import logging
import os
import pprint

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

SHOW_MORE = InlineKeyboardMarkup(
    [[InlineKeyboardButton(text='🔰 Weitere Meldungen 🔰', url='https://t.me/militaernews')]])

START_KEYBOARD = ReplyKeyboardMarkup([['Breaking news ‼️', 'Scheduled post 🕓']],
                                     one_time_keyboard=True, resize_keyboard=True)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

NEWS, MEDIA, PUBLISH = range(3)


# prettyprinter for debug
def debug(debug_txt):
    p = pprint.PrettyPrinter(width=160)
    p.pprint(debug_txt)


# testhandler
# def testmyass(update: Update, context: CallbackContext):
#     debug("[DEBUG] Called function: testmyass")
#     context.bot.send_message(chat_id=CHANNEL, text='Lick my ass')


# Replace with Filter
def verify(message: Message, context: CallbackContext) -> bool:
    debug("[DEBUG] Called function: verify ")
    if message.chat_id not in VERIFIED_USERS:
        context.bot.send_message(chat_id=message.chat_id, text='You\'re not a verfied user ⚠')
        debug(f"[DEBUG] function: verify(chat_id = {message.chat_id}) returned: False ")
        return False
    debug(f"[DEBUG] function: verify(chat_id = {message.chat_id}) returned: True ")
    return True


def start(update: Update, context: CallbackContext):
    debug("[DEBUG] Called function: start ")
    if verify(update.message, context):
        debug("[DEBUG] reply_markup = START_KEYBOARD ")
        update.message.reply_text('Choose the post type.', reply_markup=START_KEYBOARD)


def new_post(update: Update, context: CallbackContext):
    debug("[DEBUG] Called function: new_post ")
    if verify(update.message, context):
        context.user_data['breaking'] = False
        debug("[DEBUG] context.user_data['breaking'] set to: False ")
        debug("[DEBUG] user_data:")
        debug(context.user_data)
        return message_new(update, context, '<u>New scheduled post</u> 🕓')


def new_breaking(update: Update, context: CallbackContext):
    debug("[DEBUG] Called function: new_breaking")
    if verify(update.message, context):
        context.user_data['breaking'] = True
        debug("[DEBUG] context.user_data['breaking'] set to: True ")
        debug("[DEBUG] user_data:")
        debug(context.user_data)
        return message_new(update, context, '<u>New breaking news</u> ‼️')


def message_new(update: Update, context: CallbackContext, text: str):
    debug(f"[DEBUG] Called function: message_new with param: text = {text}")
    update.message.reply_text(text + '\n\n<b>Step 1 of 3</b>\nSend the news in one message',
                              parse_mode=ParseMode.HTML,
                              reply_markup=ReplyKeyboardRemove())
    return NEWS


def text(update: Update, context: CallbackContext):
    debug(f"[DEBUG] Called function: text")
    context.user_data['message'] = update.message.text_markdown_v2_urled
    debug(f"[DEBUG] context.user_data['message'] set to: update.message.text_markdown_v2_urled ")
    context.user_data['remaining'] = 4
    debug(f"[DEBUG] context.user_data['remaining'] set to: 4 ")
    debug("[DEBUG] user_data:")
    debug(context.user_data)
    update.message.reply_text('<b>Step 2 of 3</b>\nSend photos or videos as an album',
                              parse_mode=ParseMode.HTML,
                              reply_markup=ReplyKeyboardMarkup([['Use placeholder 🖼️']]))
    return MEDIA


def add_photo(update: Update, context: CallbackContext):
    debug(f"[DEBUG] Called function: add_photo")
    debug("[DEBUG] user_data:")
    debug(context.user_data)
    if context.user_data['remaining'] == 4:
        debug("[DEBUG] function add_photo: context.user_data['remaining'] == 4")
        context.user_data['files'] = list([str(update.message.photo[2].file_id)])
        debug(f"[DEBUG] add_photo: context.user_data['files'] set to: {list([str(update.message.photo[2].file_id)])}")
        context.user_data['photo'] = list([True])
        debug("[DEBUG] add_photo: context.user_data['photo'] set to: [True]")
        debug("[DEBUG] user_data:")
        debug(context.user_data)
    else:
        debug("[DEBUG] function add_photo: context.user_data['remaining'] != 4")
        context.user_data['files'].append(str(update.message.photo[2].file_id))
        debug(f"[DEBUG] add_photo: context.user_data['files'] appended: {str(update.message.photo[2].file_id)}")
        context.user_data['photo'].append(True)
        debug("[DEBUG] add_photo: context.user_data['photo'] appended: True")
        debug("[DEBUG] user_data:")
        debug(context.user_data)
    return media_sent(update, context)


def add_video(update: Update, context: CallbackContext):
    debug("[DEBUG] Called function: add_video")
    debug("[DEBUG] user_data:")
    debug(context.user_data)
    if not context.user_data['files']:
        debug("[DEBUG] function add_video: context.user_data['files'] == None")
        context.user_data['files'] = [update.message.video.file_id]
        debug(f"[DEBUG] add_video: context.user_data['files'] set to: {[update.message.video.file_id]}")
        context.user_data['photo'] = [False]
        debug(f"[DEBUG] add_video: context.user_data['photo'] set to: {[False]}")
        debug("[DEBUG] user_data:")
        debug(context.user_data)
    else:
        debug("[DEBUG] function add_video: context.user_data['files'] != None")
        context.user_data['files'] += [update.message.video.get_file().file_id]
        debug(f"[DEBUG] add_video: context.user_data['files'] added (+=): {[update.message.video.get_file().file_id]}")
        context.user_data['photo'][5 - context.user_data['remaining']] = False
        debug(f"[DEBUG] add_video: context.user_data['photo'][5 - context.user_data['remaining']] (= {5 - context.user_data['remaining']}) set to: False")
        debug("[DEBUG] user_data:")
        debug(context.user_data)
    return media_sent(update, context)


def skip_photo(update: Update, context: CallbackContext):
    debug("[DEBUG] Called function: skip_photo")
    context.user_data['files'] = None
    debug("[DEBUG] skip_photo: context.user_data['files'] set to: None")
    debug("[DEBUG] user_data:")
    debug(context.user_data)
    return message_preview(update, context)


def media_sent(update: Update, context: CallbackContext):
    debug("[DEBUG] Called function: media_sent")
    remaining = context.user_data['remaining']
    debug(f"[DEBUG] media_sent: var remaining set to: {context.user_data['remaining']}")
    
    if remaining is 0:
        debug("[DEBUG] media_sent: var remaining == 0, return message_preview")
        return message_preview(update, context)
    
    update.message.reply_text(text="You have " + str(remaining) + " photos/videos remaining.",
                              reply_markup=ReplyKeyboardMarkup([['Done ✅']]))
    context.user_data['remaining'] -= 1
    debug(f"[DEBUG] media_sent: context.user_data['remaining'] decremented (-= 1): {context.user_data['remaining']}")


def message_preview(update: Update, context: CallbackContext):
    debug("[DEBUG] Called function: message_preview, with user_data:")
    debug(context.user_data)
    update.message.reply_text('<b>Step 3 of 3</b>\nPreview the generated post',
                              parse_mode=ParseMode.HTML,
                              reply_markup=ReplyKeyboardMarkup([['Submit post 📣', 'Cancel 🗑']],
                                                               one_time_keyboard=True, resize_keyboard=True))
    
    if context.user_data['breaking']:
        txt = '\#EILMELDUNG ‼️\n\n' + context.user_data['message'] + '\n\nFolge @militaernews'
        debug(f"[DEBUG] message_preview: var txt set to: EILMELDUNG + context.user_data['message'] ({context.user_data['message']}) + Folge Milnews")
    else:
        txt = context.user_data['message'] + '\nFolge @militaernews'
        debug(f"[DEBUG] message_preview: var txt set to: context.user_data['message'] ({context.user_data['message']}) + Folge Milnews")
    
    if not context.user_data['files']:
        debug(f"[DEBUG] message_preview: if not context.user_data['files']")
        msg = context.bot.send_photo(update.message.chat_id,
                                     photo=open('eilmeldung.png', 'rb'),
                                     caption=txt,
                                     parse_mode=ParseMode.MARKDOWN_V2,
                                     reply_markup=SHOW_MORE)
    
    elif len(context.user_data['files']) == 1:
        debug(f"[DEBUG] message_preview: elif len(context.user_data['files']) == 1 ({len(context.user_data['files'])})")
        if context.user_data['photo'][0]:
            debug(f"[DEBUG] message_preview: if context.user_data['photo'][0] ({context.user_data['photo'][0]})")
            msg = context.bot.send_photo(chat_id=update.message.chat_id,
                                         photo=context.user_data['files'][0],
                                         caption=txt,
                                         parse_mode=ParseMode.MARKDOWN_V2,
                                         reply_markup=SHOW_MORE)
        else:
            debug(f"[DEBUG] message_preview: if not context.user_data['photo'][0]")
            msg = context.bot.send_video(chat_id=update.message.chat_id,
                                         video=context.user_data['files'][0],
                                         caption=txt,
                                         parse_mode=ParseMode.MARKDOWN_V2,
                                         reply_markup=SHOW_MORE)
    
    else:
        debug(f"[DEBUG] message_preview: len(context.user_data['files']) != 1 ({len(context.user_data['files'])})")
        context.bot.send_message(update.message.chat_id, text='Media Group:')
        
        if context.user_data['photo'][0]:
            debug(f"[DEBUG] message_preview: if context.user_data['photo'][0] ({context.user_data['photo'][0]})")
            files = [
                InputMediaPhoto(media=context.user_data['files'][0], caption=txt, parse_mode=ParseMode.MARKDOWN_V2)]
            debug(f"[DEBUG] message_preview: list files changed to: {files}")
        else:
            debug(f"[DEBUG] message_preview: if not context.user_data['photo'][0] ({context.user_data['photo'][0]})")
            files = [
                InputMediaVideo(media=context.user_data['files'][0], caption=txt, parse_mode=ParseMode.MARKDOWN_V2)]
            debug(f"[DEBUG] message_preview: list files changed to: {files}")

        debug(f"[DEBUG] message_preview: for loop: range(1, len(context.user_data['files']) (0, {len(context.user_data['files'])})")
        for i in range(1, len(context.user_data['files'])):
            debug(f"[DEBUG] message_preview: for loop: i == {i}")
            if context.user_data['photo'][i]:
                debug(f"[DEBUG] message_preview: context.user_data['photo'][i] ({context.user_data['photo'][i]})")
                debug(context.user_data['files'][i])
                files.append(InputMediaPhoto(media=context.user_data['files'][i]))
                debug(f"[DEBUG] message_preview: list files added (+=): InputMediaPhoto(media=context.user_data['files'][i]) ({context.user_data['files'][i]})")
            else:
                files.append(InputMediaVideo(media=context.user_data['files'][i]))
                debug(f"[DEBUG] message_preview: list files added (+=): InputMediaVideo(media=context.user_data['files'][i]) ({context.user_data['files'][i]})")
        debug(f"[DEBUG] message_preview: list files:")
        debug(files)
        debug("[DEBUG] user_data:")
        debug(context.user_data)
        
        # how to copy it?
        msg = context.bot.send_media_group(chat_id=update.message.chat_id, media=files)
        debug("[DEBUG] message_preview: var msg changed to: context.bot.send_media_group(chat_id=update.message.chat_id, media=files, reply_markup=SHOW_MORE)")
    
    context.user_data['post'] = msg
    debug("[DEBUG] message_preview: context.user_data['post'] changed to: msg")
    debug("[DEBUG] user_data:")
    debug(context.user_data)

    return PUBLISH


# What about SUBMIT and CANCEL instead?
def publish(update: Update, context: CallbackContext):
    debug("[DEBUG] Called function: publish")
    if context.user_data['breaking']:
        broadcast_html(
            context,
            '\#EILMELDUNG ‼️\n\n' + context.user_data['message'] + '\nFolge @militaernews')
    else:
        context.bot.send_message(
            chat_id=CHANNEL,
            text=context.user_data['message'] + '\nFolge @militaernews',
            parse_mode=ParseMode.HTML,
            
            reply_markup=InlineKeyboardMarkup.from_button(InlineKeyboardButton(
                text='🔰 Weitere Meldungen 🔰',
                url='https://t.me/militaernews')))
    
    return publish_success(update, context)


def publish_post(update: Update, context: CallbackContext):
    debug("[DEBUG] Called function: publish_post")
    broadcast_html(
        context,
        'hhh' + '\nFolge @militaernews')
    
    return publish_success(update, context)


def broadcast_html(context: CallbackContext, text: str):
    debug("[DEBUG] Called function: broadcast_html")
    context.bot.send_message(
        chat_id=CHANNEL,
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup.from_button(InlineKeyboardButton(
            text='🔰 Weitere Meldungen 🔰',
            url='https://t.me/militaernews')))


def add_button(update: Update, context: CallbackContext):
    debug("[DEBUG] Called function: add_button")
    try:
        update.effective_message.edit_reply_markup(reply_markup=SHOW_MORE)
    except:
        return


def publish_success(update: Update, context: CallbackContext):
    debug("[DEBUG] Called function: publish_success")
    update.message.reply_text('<b>Message sent</b> ✅\nCompose a new one?',
                              parse_mode=ParseMode.HTML,
                              reply_markup=START_KEYBOARD)
    debug("[DEBUG] publish_success: returning ConversationHandler.END")
    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext):
    debug("[DEBUG] Called function: cancel")
    update.message.reply_text(
        text='<b>Editing this post was cancelled</b> 🗑\nFeel free to create a new one',
        parse_mode=ParseMode.HTML,
        reply_markup=START_KEYBOARD)
    debug("[DEBUG] cancel: returning ConversationHandler.END")
    return ConversationHandler.END


def message_html(update: Update, context: CallbackContext, text: str):
    debug("[DEBUG] Called function: message_html")
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


if __name__ == '__main__':
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    
    #  dp.add_error_handler(error)
    
    # dp.add_handler(CommandHandler('ass', testmyass))
    
    dp.add_handler(CommandHandler('start', start, filters=Filters.chat(chat_id=VERIFIED_USERS)))
    
    dp.add_handler(MessageHandler(Filters.update.channel_post | Filters.update.edited_channel_post, add_button))
    
    dp.add_handler(ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('Breaking news ‼️'), new_breaking),
                      MessageHandler(Filters.regex('Scheduled post 🕓'), new_post)],
        states={
            NEWS: [MessageHandler(Filters.regex('.*'), text)],
            MEDIA: [MessageHandler(Filters.photo, add_photo),
                    MessageHandler(Filters.video, add_video),
                    MessageHandler(Filters.regex('Use placeholder 🖼️'), skip_photo),
                    MessageHandler(Filters.regex('Done ✅'), message_preview)],
            PUBLISH: [MessageHandler(Filters.regex('Submit post 📣'), publish)]},
        fallbacks=[MessageHandler(Filters.regex('Cancel 🗑'), cancel), CommandHandler('start', start)],
    ))
    
    updater.start_webhook(listen='0.0.0.0', port=PORT, url_path=TOKEN)
    updater.bot.setWebhook('https://ptb-militaernews.herokuapp.com/' + TOKEN)
    updater.start_polling()
    updater.idle()
