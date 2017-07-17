from config import TOKEN
from phrases import HUG_PHRASES, PHRASES_LENGTH

from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, 
InlineQueryHandler)
import logging, re, random

HELP_STRING = ("""
useful helpful text
""")

def start(bot, update):
    update.message.reply_text("Hi!")

def help(bot, update):
    update.message.reply_text(HELP_STRING)

def escape_markdown(text):
    escape_chars = '\*_`\['
    Ntext = re.sub(r'([%s])' % escape_chars, r'\\\1', text)
    return Ntext

def phrase_generator():
    number = random.randint(0, PHRASES_LENGTH)
    phrase = HUG_PHRASES[number]
    return phrase

def inlinequery(bot, update):
    query = update.inline_query.query
    results = list()

    pre_phrase = "I'm sending "
    phrase = phrase_generator()
    username = escape_markdown(query)
    hug_emote = "(>^-^)>"

    if '@' not in username:
        username = "@{}".format(username)

    typed_name = InputTextMessageContent(str(query))
    results.append(InlineQueryResultArticle(id=1, 
        title="I will hug {} {}".format(str(query), hug_emote), 
        input_message_content=InputTextMessageContent(
        pre_phrase + username + phrase + hug_emote,
        parse_mode=ParseMode.MARKDOWN)))
    
    update.inline_query.answer(results)

def error_callback(bot, update, error):
    logging.error(error)

def main():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    updater = Updater(token=TOKEN)
    dp = updater.dispatcher
    dp.add_error_handler(error_callback)
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('help', help))
    #dp.add_handler(CommandHandler('phrase', phrase_generator))
    dp.add_handler(InlineQueryHandler(inlinequery))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()