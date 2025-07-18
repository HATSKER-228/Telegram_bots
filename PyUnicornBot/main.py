import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ChatType
from aiogram.filters import Command
from aiogram.types import Message
from aiogram import F
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


bot = Bot(token=os.environ.get('TOKEN'))
dp = Dispatcher()


@dp.message(Command("start"), F.chat.type == ChatType.PRIVATE)
async def start_private(message: Message) -> None:
	await message.answer("Привіт, пупсику. Я - Unicorn Bot. Ти можеш побачити, що я вмію робити, надіславши команду /help.")


@dp.message(Command("start"), F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}))
async def start_group(message: Message) -> None:
	await message.answer("Привіт, пупсики. Я - Unicorn Bot. Ви можете побачити, що я вмію робити, надіславши команду /help@PyUnicornBot.")


@dp.message(Command("help"))
async def help_command(message: Message) -> None:
	await message.answer("""Ось список того, що я вмію:
/start - привітаннячка від мене
/help - надішлю оце повідомлення
/fix - виправлю розкладку повідомлення (з qwerty на йцукен, або ж навпаки)""")


@dp.message(Command("fix"))
async def fix_command(message: Message) -> None:
	if message.reply_to_message and message.reply_to_message.text:
		text = message.reply_to_message.text
		fixed = fix_ytsuken(text) if determinate_lang(text) == 'ua' else fix_qwerty(text)
		await message.reply_to_message.reply(fixed)
	else:
		await message.reply('Command must be a reply to another <u><i>text</i></u> message!', parse_mode='HTML')


async def main() -> None:
	await dp.start_polling(bot)


if __name__ == "__main__":
	asyncio.run(main())
