from config import TOKEN

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging

def start(bot, update):
    update.message.reply_text("Hi!")

def error_callback(bot, update, error):
    logging.error(error)

if __name__ == '__main__':
    logging.basicConfig(format='[%(asctime)s] &(message)s')

    updater = Updater(token=TOKEN)
    dispatcher = updater.dispatcher
    updater.dispatcher.add_error_handler(error_callback)
    updater.dispatcher.add_handler(CommandHandler('start', start))

    updater.start_polling()
    updater.idle()