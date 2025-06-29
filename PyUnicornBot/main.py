import telebot
import os
from keep_alive import keep_alive
keep_alive()

QWERTY_TO_YTSUKEN: dict = {
	'@': '"', '#': '№', '$': ';', '^': ':', '&': '?',
	'q': 'й', 'w': 'ц', 'e': 'у', 'r': 'к', 't': 'е', 'y': 'н', 'u': 'г', 'i': 'ш', 'o': 'щ', 'p': 'з', '[': 'х',
	'{': 'Х', ']': 'ї', '}': 'Ї',
	'a': 'ф', 's': 'і', 'd': 'в', 'f': 'а', 'g': 'п', 'h': 'р', 'j': 'о', 'k': 'л', 'l': 'д', ';': 'ж', ':': 'Ж',
	"'": 'є', '"': 'Є',
	'z': 'я', 'x': 'ч', 'c': 'с', 'v': 'м', 'b': 'и', 'n': 'т', 'm': 'ь', ',': 'б', '<': 'Б', '.': 'ю', '>': 'Ю',
	'/': '.', '?': ','
}
YTSUKEN_TO_QWERTY: dict = dict([(value, key) for key, value in QWERTY_TO_YTSUKEN.items()])
BOT = telebot.TeleBot(os.environ.get('TOKEN'))


def fix_qwerty(s: str) -> str:
	new: str = ''
	username = False
	for char in s:
		if char == '@':
			username = True
		elif char in ' []{};\':",./<>?':
			username = False
		if username:
			new += char
		else:
			new_char: str = QWERTY_TO_YTSUKEN.get(char if char in '{[}]:;"\'<,>.' else char.lower(), char)
			new += new_char.upper() if char.isupper() else new_char
	return new


def fix_ytsuken(s: str) -> str:
	new: str = ''
	for char in s:
		new_char: str = YTSUKEN_TO_QWERTY.get(char if char in 'хХїЇжЖєЄбБюЮ' else char.lower(), char)
		new += new_char.upper() if char.isupper() else new_char
	return new


def determinate_lang(text: str) -> str:
	s: set = set(text.lower())
	ua: set = set('йцукенгшщзфівапролджєячсмитьбю')
	if len(s.intersection(ua)):
		return 'ua'
	return 'eng'


@BOT.message_handler(chat_types=['private'], commands=['start'])
def start_cmd(message):
	BOT.send_message(message.chat.id,
					 'Привіт, пупсику. Я - Unicorn Bot. Ти можеш побачити, що я вмію робити, надіславши команду /help.')


@BOT.message_handler(chat_types=['group', 'supergroup'], commands=['start'])
def start_cmd(message):
	BOT.send_message(message.chat.id,
					 'Привіт, пупсики. Я - Unicorn Bot. Ви можете побачити, що я вмію робити, надіславши команду /help@PyUnicornBot.')


@BOT.message_handler(commands=['help'])
def help_cmd(message):
	BOT.send_message(message.chat.id,
					 '''Ось список того, що я вмію:
/start - привітаннячка від мене
/help - надішлю оце повідомлення
/fix - виправлю розкладку повідомлення (з qwerty на йцукен, або ж навпаки)''')


@BOT.message_handler(commands=['fix'])
def fix_cmd(message):
	if to_fix := message.reply_to_message:
		if to_fix.content_type == 'text':
			if determinate_lang(to_fix.text) == 'ua':
				fixed: str = fix_ytsuken(to_fix.text)
			else:
				fixed: str = fix_qwerty(to_fix.text)
			BOT.reply_to(to_fix, fixed)
			return
	BOT.reply_to(message, 'Command must be a reply to another <u><i>text</i></u> message!', parse_mode='HTML')


if __name__ == '__main__':
	print('Bot starting...')
	BOT.polling()
