from django.core.management.base import BaseCommand
from environs import Env
from telegram import Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.utils.request import Request


def start_command(update, context):
    update.message.reply_text('Здравствуйте!')


def echo_message(update, context):
    update.message.reply_text(update.message.text)


class Command(BaseCommand):
    help = 'Start Telegram bot'

    def handle(self, *args, **options):
        env = Env()
        env.read_env()

        telegram_token = env("TELEGRAM_TOKEN")

        # request = Request(connect_timeout=0.5, read_timeout=1.0)
        # bot = Bot(request=request, token=telegram_token)
        #
        # print(bot.getMe())

        updater = Updater(telegram_token)
        dispatcher = updater.dispatcher

        dispatcher.add_handler(CommandHandler('start', start_command))
        dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo_message))

        updater.start_polling()
        updater.idle()
