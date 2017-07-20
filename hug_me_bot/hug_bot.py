from config import TOKEN, PORT, APPNAME, DEBUG_CHANNEL, MONGODB_URI
from phrases import HUG_PHRASES, PHRASES_LENGTH

from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, 
InlineQueryHandler)
from datetime import datetime
import logging, re, random, pymongo

HELP_STRING = ("""
Hello! I am an inline bot!
To use me type @Hug_Me_Bot in any chat,
after that type the username of the person that needs a hug
and finally select the desired emote.
Free hugs guaranteed.

Need help? Contact @aBARICHELLO
Star me on github! https://github.com/aBARICHELLO/Hug_Me_Bot
""").strip('\n')

conn = pymongo.MongoClient(MONGODB_URI)
db = conn.get_default_database()
collection = db.hugs

def start(bot, update):
	bot.send_message(chat_id=update.message.chat_id, text=HELP_STRING)

def help(bot, update):
	bot.send_message(chat_id=update.message.chat_id, text=HELP_STRING)

def escape_markdown(text):
	escape_chars = '\*_`\['
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

	if len(typed_username) > 5:
		add_stats(sender_username, typed_username)
	update.inline_query.answer(results)

def formatTypedUsername(typed_username):
	if len(typed_username) > 4 and '@' not in typed_username:
		typed_username = "@{}".format(typed_username)
	if ' ' in typed_username:
		typed_username = typed_username.replace(' ', '_')
	return typed_username

def add_stats(sender_username, typed_username):
	date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

	doc = {
		"sender": sender_username,
		"receiver": typed_username,
		"date": date
	}
	collection.insert(doc)

def statistics(bot, update):
	a = "test"
	update.message.reply_text("Bot stats:")
	cursor = collection.find()

	hugs = []
	senders = []
	receivers = []
	for document in cursor:
		if document not in hugs:
			hugs.append(document)
		if document['sender'] not in senders:
			senders.append(document['sender'])
		if document['receiver'] not in receivers:
			receivers.append(document['receiver'])
	
	totalHugs = len(hugs)
	totalSenders = len(senders)
	totalReceivers = len(receivers)
	totalNetwork = totalSenders + totalReceivers

	STATS_STRING = (
	"""Hugs given: {}
	Number of huggers: {}
	Number of people hugged: {}
	Total network: {}""").format(totalHugs, totalSenders, totalReceivers, totalNetwork)

	update.message.reply_text(STATS_STRING)

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
	dp.add_handler(CommandHandler('stats', statistics))

	updater.start_webhook(listen='0.0.0.0', port=int(PORT), url_path=TOKEN)
	updater.bot.setWebhook("https://" + APPNAME + ".herokuapp.com/" + TOKEN)
	updater.idle()

if __name__ == '__main__':
	main()