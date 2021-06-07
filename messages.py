import time

from telegram import Update, ParseMode
from telegram.ext import CallbackContext

from config import GROUP_SHITPOST, GROUP_MAIN
from utils import delay_group, delay_group_button_url, now, delay_group_preview, message_button_url


##########################################
# this file contains the actions that will happen once a command is called
# just replicate below schemes :)
##########################################

def forward_meme(update: Update, _: CallbackContext):
    for i in (GROUP_MAIN, GROUP_SHITPOST):
        update.message.forward(i)
        time.sleep(3)


def admins(update: Update, context: CallbackContext):
    delay_group(update, context,
                "<u>Group's staff</u>"
                "\n\n<b>Organization</b>"
                "\n@aakaah00001"
                "\n@Prashant_Choudhary"
                "\n@PacificPC"
                "\n\n<b>Moderators</b>"
                "\n@dark_phoenix6969"
                "\n@blue_bettle")


def polls(update: Update, context: CallbackContext):  # GROUP

    current_time = now()
    previous_timestamp = context.bot_data.get("previous_timestamp", 1000)

    if update.message.from_user.id in ADMINS and int(previous_timestamp) + 3628800000 <= current_time:
        update.message.delete()
        print("--- sending new poll")

        current_link = context.bot.send_message(GROUP,
                                                "Hey Realme Fans!"
                                                "\n\n<b>It's once again time for Poll-Five 🖐️</b> "
                                                "\n\nThis idea came up in @realme_offtopic a few days ago and I "
                                                "immediately implemented it. It could just be interesting to see what "
                                                "the community thinks about certain topics. "
                                                "\n\nCredits go to all the ones who brought up the following "
                                                "questions. "
                                                "\n\nHope you enjoy it!", ParseMode.HTML).link

        context.bot_data['previous_link'] = current_link
        context.bot_data['previous_timestamp'] = current_time

        question_0 = "How old are you? 🎂"
        answers_0 = ["below 15", "15-18", "19-21", "22-26", "27-32",
                     "33-37", "38-45", "46-53", "54-62", "older than 63"]

        question_1 = "How old is your current phone? 📱"
        answers_1 = ["3 months", "6 months", "9 months", "1 year", "1.5 years",
                     "2 years", "2.5 years", "3 years", "3.5 years", "4 years or older"]

        question_2 = "How much money would you spend on a good value phone? 💰"
        answers_2 = ["80-120$", "121-150$", "151-200$", "201-250$", "251-300$",
                     "301-350$", "351-420$", "421-500$", "501-650$", "more than 650$"]

        question_3 = "How many different phones have you owned over the last 5 years? 🎁"
        answers_3 = ["1", "2", "3", "4", "more than 4"]

        question_4 = "What's the most important thing when buying a brandnew phone? 🔥"
        answers_4 = ["Camera", "Display", "Audio", "Haptics/Design", "Storage space",
                     "Connectivity", "Multitasking capability/Ram", "Processing power", "Battery/Endurance",
                     "Durability/Protection"]

        questions = [question_0, question_1, question_2, question_3]
        answers = [answers_0, answers_1, answers_2, answers_3]

        for i in range(4):
            context.bot.send_poll(GROUP, "[Poll {} of 5] · {}".format(i + 1, questions[i]), answers[i])
            time.sleep(3)

        context.bot.send_poll(GROUP, "[Poll 5 of 5] · {}".format(question_4), answers_4, allows_multiple_answers=True)

    else:
        print("--- sending poll message")

        previous_link = context.bot_data.get("previous_link", "https://t.me/realme_support/135222")

        delay_group_button_url(update, context,
                               "<b>Poll-Five</b> 🖐️"
                               "\n\nThis idea came up in @realme_offtopic. We thought it could just be "
                               "interesting to see what the community thinks about certain topics. "
                               "\n\nCredits go to all the ones who brought up the questions.",
                               "📊 Current Poll 📊", previous_link)
