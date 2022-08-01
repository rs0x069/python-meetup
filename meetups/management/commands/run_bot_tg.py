from django.core.management.base import BaseCommand
from environs import Env
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


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

        updater = Updater(telegram_token)
        dispatcher = updater.dispatcher

        dispatcher.add_handler(CommandHandler('start', start_command))
        dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo_message))

        updater.start_polling()
        updater.idle()
