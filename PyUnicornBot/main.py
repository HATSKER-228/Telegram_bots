import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ChatType
from aiogram.filters import Command
from aiogram.types import Message
from aiogram import F

import os
from baby_data import register_user, unregister_user, get_stats, select_baby
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


@dp.message(Command('start'), F.chat.type == ChatType.PRIVATE)
async def cmd_start_private(message: Message) -> None:
	await message.answer('Привіт, пупсику ❤️. Я - Unicorn Bot. Ти можеш побачити, що я вмію робити, надіславши команду /help.')


@dp.message(Command('start'), F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}))
async def cmd_start_group(message: Message) -> None:
	await message.answer('Привіт, пупсики ❤️. Я - Unicorn Bot. Ви можете побачити, що я вмію робити, надіславши команду /help@PyUnicornBot.')


@dp.message(Command('help'))
async def cmd_help(message: Message) -> None:
	await message.answer('''Ось список того, що я вмію:
/start - привітаннячка від мене
/help - надішлю оце повідомлення
/fix - виправлю розкладку повідомлення (з qwerty на йцукен, або ж навпаки)

<b>!!!Тільки в групі!!!</b>
/baby_reg - зареєструю користувача до кандидатів на звання Пупсика дня
/baby_unreg - видалю користувача із кандидатів на звання Пупсика дня
/baby_select - оберу Пупсика дня (лише раз в день)
/baby_stats - надішлю статистику хто скільки разів був Пупсиком дня''', parse_mode='HTML')


@dp.message(Command('fix'))
async def cmd_fix(message: Message) -> None:
	if message.reply_to_message and message.reply_to_message.text:
		text = message.reply_to_message.text
		fixed = fix_ytsuken(text) if determinate_lang(text) == 'ua' else fix_qwerty(text)
		await message.reply_to_message.reply(fixed)
	else:
		await message.reply('Шановний тупорилий представник виду <i>Homo Sapiens</i>, команду необхідно писати у ВІДПОВІДЬ на ТЕКСТОВЕ повідомлення 🧌', parse_mode='HTML')


@dp.message(Command('baby_reg'), F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}))
async def cmd_baby_reg(message: Message) -> None:
	user = message.from_user
	added = register_user(message.chat.id, user.id, user.username)
	if added:
		await message.reply(f'{user.full_name} тепер у списку пупсиків! 🐣')
	else:
		await message.reply('Ти вже зареєстрований як пупсик 😘')


@dp.message(Command('baby_unreg'), F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}))
async def cmd_baby_unreg(message: Message) -> None:
	user = message.from_user
	deleted = unregister_user(message.chat.id, user.id, user.username)
	if deleted:
		await message.reply(f'{user.full_name} покинув список пупсиків 😭')
	else:
		await message.reply(f'{user.full_name} не було в списку пупсиків. Варто приєднатися!')


@dp.message(Command('baby_select'), F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}))
async def cmd_baby_play(message: Message) -> None:
	username, error = select_baby(message.chat.id)
	if error:
		await message.reply(error)
	else:
		await message.reply(f'🎉 Пупсік дня — @{username}!')


@dp.message(Command('baby_stats'), F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}))
async def cmd_baby_stats(message: Message) -> None:
	data = get_stats(message.chat.id)
	if data:
		s = 'Статистика пупсиків дня:\n'
		for index, user_info in enumerate(data):
			row = f'{index+1}) {user_info[0]} - {user_info[1]}\n'
			s += row
		await message.reply(s)
	else:
		await message.reply('У цьому чаті ще немає зареєстрованих пупсіків!')


async def main() -> None:
	await dp.start_polling(bot)


if __name__ == "__main__":
	asyncio.run(main())
