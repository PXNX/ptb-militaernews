from telegram.ext import BaseFilter


class AlbumFilter(BaseFilter):
    def filter(self, message):
        return message.media_group_id


album_filter = AlbumFilter()


def get_report(update, context):
    # since albums aren't displayed as unique update we will wait 5 seconds
    # before passing the update to media_hanlder to be sure that bot will list all media of the album
    context.job_queue.run_once(media_handler, when=2, context=update)


def get_media_album(update, context):
    if update.effective_message.media_group_id not in context.bot_data:
        media_album = context.bot_data[update.effective_message.media_group_id] = []
    else:
        media_album = context.bot_data[update.effective_message.media_group_id]
    if update.effective_message.photo:
        media_album.append(["photo", update.effective_message.photo[-1].file_id])
    elif update.effective_message.video:
        media_album.append(["video", update.effective_message.video.file_id])


def media_handler(context):
    update = context.job.context
    if update.effective_message.media_group_id:
        media = "album"
        media_file = context.bot_data[custom_update.effective_message.media_group_id]

    elif update.effective_message.photo:
        media = "photo"
        media_file = custom_update.effective_message.photo[-1].file_id

    elif update.effective_message.video:
        media = "video"
        media_file = custom_update.effective_message.video.file_id

    else:
        media = None
        media_file = None

    context.bot_data[something][something] = {"media_type": media, "media_file": media_file}


def send_report_description(update, context):
    if context.bot_data[something]["media_type"] is not None:
        if context.bot_data[something]["media_type"] == "photo":
            context.bot.send_photo(chat_id=update.effective_chat.id,
                                   caption=f'Description: {report_info["description"]}\n\nOriginal Message: {report_info["message_info"]["link"]}',
                                   photo=report_info["media_file"])
        elif context.bot_data[something]["media_type"] == "video":
            context.bot.send_video(chat_id=update.effective_chat.id,
                                   caption=f'Description: {report_id["description"]}\n\nOriginal Message: {report_info["message_info"]["link"]}',
                                   video=report_info["media_file"])
        elif context.bot_data[something]["media_type"] == "album":
            album = []
            for media_file in context.bot_data[something]["media_file"]:
                caption = f'Description: '
                something
                ' if context.bot_data[something]["media_file"].index(media_file) == 0 else None
                if media_file[0] == "photo":
                    album.append(InputMediaPhoto(media=media_file[1], caption=caption))
                elif media_file[0] == "video":
                    album.append(InputMediaVideo(media=media_file[1], caption=caption))
            context.bot.send_media_group(chat_id=update.effective_chat.id, media=album)


def main():
    updater = Updater(token='token')
    dispatcher = updater.dispatcher

    dispatcher.add_handler(MessageHandler(album_filter, get_media_album), group=0)
    dispatcher.add_handler(MessageHandler(something, get_report), group=1)


if __name__ == '__main__':
    main()