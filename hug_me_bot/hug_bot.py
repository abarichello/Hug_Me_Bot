from config import TOKEN
from phrases import HUG_PHRASES, PHRASES_LENGTH

from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, 
InlineQueryHandler)
import logging, re, random

HELP_STRING = ("""
Hello! I am an inline bot!
To use me type @Hug_Me_Bot in any chat,
after that type the username of the person that needs a hug
and finally select the desired emote.
Free hugs guaranteed.

Need help? Contact @aBARICHELLO
Star me on github! https://github.com/aBARICHELLO/Hug_Me_Bot
""").strip('\n')

def start(bot, update):
    update.message.reply_text("Hi!")

def help(bot, update):
    update.message.reply_text(HELP_STRING)

def escape_markdown(text):
    escape_chars = ' \*_`\['
    text = re.sub(r'([%s])' % escape_chars, r'\\\1', text)
    return text

def phrase_generator():
    number = random.randint(0, PHRASES_LENGTH)
    phrase = HUG_PHRASES[number]
    return phrase

def inlinequery(bot, update):
    query = update.inline_query.query
    results = list()

    sender_username = update.inline_query.from_user.username
    if sender_username == None:
        sender_username = update.inline_query.from_user.first_name
    pre_phrase = "@{} sends ".format(sender_username)
    phrase = phrase_generator()
    typed_username = escape_markdown(query)
    hug_emote = '(>^-^)>'

    typed_username = formatTypedUsername(typed_username)

    results.append(InlineQueryResultArticle(id=1, 
        title="{} I will hug {}".format(hug_emote, str(query)), 
        input_message_content=InputTextMessageContent(
        pre_phrase + typed_username + phrase + hug_emote,
        parse_mode=ParseMode.MARKDOWN)))
    
    hug_emote = 'ʕ◉ᴥ◉ʔ'
    results.append(InlineQueryResultArticle(id=2, 
        title="{} I will give {} a hug!".format(hug_emote, str(query)), 
        input_message_content=InputTextMessageContent(
        pre_phrase + typed_username + phrase + hug_emote,
        parse_mode=ParseMode.MARKDOWN)))

    update.inline_query.answer(results)

def formatTypedUsername(typed_username):
    if len(typed_username) > 4 and '@' not in typed_username:
       typed_username = "@{}".format(typed_username)
    if ' ' in typed_username:
        typed_username = typed_username.replace(' ', '_')
    return typed_username

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
    dp.add_handler(InlineQueryHandler(inlinequery))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()