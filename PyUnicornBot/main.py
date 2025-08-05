import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ChatType
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, User, FSInputFile
from aiogram import F
import shutil
import os
from random import randint
from baby_data import register_user, unregister_user, get_stats, select_baby, get_path, is_in_list, get_ids
from numbers_tools import create_game, join_to_game, set_player_number, cancel_game, guess_number, delete_game
from numbers_tools import get_opponent_id, get_guesses, get_user_finished, get_number, get_random_num
from keyboards import kb_join_game, kb_random_num, kb_submit_baby_unreg
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


def get_tag(user: User) -> str:
    return f'@{user.username}' if user.username else f'<a href="tg://user?id={user.id}">{user.full_name}</a>'


def get_link(user: User) -> str:
    return f'<a href="tg://user?id={user.id}">{user.full_name}</a>'


async def get_user_from_chat(chat_id: int, user_id: int) -> User:
    return (await bot.get_chat_member(chat_id, user_id)).user


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
    await message.answer(
        'Привіт, пупсику ❤️. Я - Unicorn Bot. Ти можеш побачити, що я вмію робити, надіславши команду /help.')


@dp.message(Command('start'), F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}))
async def cmd_start_group(message: Message) -> None:
    await message.answer(
        'Привіт, пупсики ❤️. Я - Unicorn Bot. Ви можете побачити, що я вмію робити, надіславши команду /help@PyUnicornBot.')


@dp.message(Command('help'))
async def cmd_help(message: Message) -> None:
    await message.answer('''Ось список того, що я вмію:
/start - привітаннячка від мене
/help - надішлю оце повідомлення
/fix - виправлю розкладку повідомлення (з qwerty на йцукен, або ж навпаки)
/shypko - оціню повідомлення від 0 до 10
/rules - надішлю правила кожної мінігри

<b>!!!Тільки в групі!!!</b>
<u>Пупсик дня</u>
/baby_reg - додам тебе у список Пупсиків
/baby_unreg - видалю тебе з Пупсиків
/baby_select - оберу Пупсика дня (лише раз в день)
/baby_stats - надішлю статистику хто скільки разів був Пупсиком дня
/all - покличу усіх Пупсиків у чат

<u>Гра "Числа"</u>
/create - створю гру
/guess [число] - надішлю тобі підказку, щоб відгадати число суперника
/cancel - скасувати гру''', parse_mode='HTML')


@dp.message(Command('fix'))
async def cmd_fix(message: Message) -> None:
    if message.reply_to_message and message.reply_to_message.text:
        text = message.reply_to_message.text
        fixed = fix_ytsuken(text) if determinate_lang(text) == 'ua' else fix_qwerty(text)
        await message.reply_to_message.reply(fixed)
    else:
        await message.reply('Шановний тупорилий представник виду <i>Homo Sapiens</i>, команду необхідно писати у '
                            'ВІДПОВІДЬ на ТЕКСТОВЕ повідомлення 🧌', parse_mode='HTML')


@dp.message(Command('shypko'))
async def cmd_shypko(message: Message) -> None:
    if message.reply_to_message:
        await message.reply_to_message.reply(f'Я оцінюю це повідомлення на {randint(0, 10)} шипко з 10.')
    else:
        await message.reply('Шановний тупорилий представник виду <i>Homo Sapiens</i>, команду необхідно писати у '
                            'ВІДПОВІДЬ на повідомлення 🧌', parse_mode='HTML')


@dp.message(Command('rules'))
async def cmd_rules(message: Message) -> None:
    text = '''📜 <b>Правила мініігор</b>
👶 <i>Пупсик дня:</i>
• Щоб долучитися, напиши мені /baby_reg.
• Якщо передумаєш — вийди з гри командою /baby_unreg.
• Я можу обрати пупсика дня — для цього напиши /baby_select.
• Я обираю випадкового гравця зі списку, і роблю це лише один раз на день.
• Подивитися, скільки разів хто ставав пупсиком, можна через /baby_stats.
    
🎯 <i>Гра "Числа":</i>
• Це гра для двох гравців, які мають бути в одній групі.
• Створити гру можна командою /create.
• Я сам напишу кожному з гравців у приват і попрошу загадати 4-цифрове число з різних цифр.
• Після цього гравці по черзі надсилають мені здогадки командою, наприклад /guess 1234.
• Я у відповідь надсилаю підказку:
    X — цифра є і стоїть на правильному місці.
    O — цифра є, але стоїть не там.
• Виграє той, хто першим вгадає число суперника повністю.
• Якщо хочете зупинити гру — напишіть /cancel.
• В одній групі може бути лише одна активна гра.'''
    await message.answer(text, parse_mode='HTML')


@dp.message(Command('baby_reg'))
async def cmd_baby_reg(message: Message) -> None:
    if message.chat.type == 'private':
        await message.reply('Цю команду можна використати тільки в групі 🧌')
        return
    user = message.from_user

    added = register_user(message.chat.id, user.id, user.username)
    if added:
        await message.reply(f'{get_tag(user)} тепер у списку пупсиків! 🐣', parse_mode='HTML')
    else:
        await message.reply('Ти вже зареєстрований як пупсик 😘')


@dp.message(Command('baby_unreg'))
async def cmd_baby_unreg(message: Message) -> None:
    if message.chat.type == 'private':
        await message.reply('Цю команду можна використати тільки в групі 🧌')
        return
    user = message.from_user
    in_list = is_in_list(message.chat.id, user.id)
    if not in_list:
        await message.reply(f'{get_tag(user)} не було в списку пупсиків. Варто приєднатися!', parse_mode='HTML')
        return

    kb = kb_submit_baby_unreg(message.chat.id, user.id)
    await message.answer(f'{get_link(user)}, ти точно хочеш вийти зі списку Пупсиків?', parse_mode='HTML', reply_markup=kb)
    await message.delete()


@dp.message(Command('baby_select'))
async def cmd_baby_select(message: Message) -> None:
    if message.chat.type == 'private':
        await message.reply('Цю команду можна використати тільки в групі 🧌')
        return
    chat_id: int = message.chat.id
    is_successful, baby_id = select_baby(chat_id)
    if is_successful:
        baby = await get_user_from_chat(chat_id, baby_id)
        await message.answer(f'🎉 Пупсик дня — {get_tag(baby)}!', parse_mode='HTML')
    elif baby_id:
        baby = await get_user_from_chat(chat_id, baby_id)
        await message.reply(f'Сьогоднішній пупсік уже обраний: {get_tag(baby)}💖', parse_mode='HTML')
    else:
        await message.reply('У цьому чаті ще немає зареєстрованих пупсіків😢')


@dp.message(Command('baby_stats'))
async def cmd_baby_stats(message: Message) -> None:
    if message.chat.type == 'private':
        await message.reply('Цю команду можна використати тільки в групі 🧌')
        return
    data = get_stats(message.chat.id)
    if data:
        s = 'Статистика Пупсиків дня:\n'
        for index, user_info in enumerate(data):
            if user_info[1]:
                row = f'{index+1}) {user_info[1]} - {user_info[2]}\n'
            else:
                user = await get_user_from_chat(message.chat.id, user_info[0])
                row = f'{index+1}) {user.full_name} - {user_info[2]} (додай юзернейм будь ласка🙏)\n'
            s += row
        await message.reply(s)
    else:
        await message.reply('У цьому чаті ще немає зареєстрованих Пупсіків 😢')


@dp.message(Command('all'))
async def cmd_all(message: Message) -> None:
    if message.chat.type == 'private':
        await message.reply('Цю команду можна використати тільки в групі 🧌')
        return
    data = get_ids(message.chat.id)
    if data:
        await message.answer('Пупсики, всі сюди 🤗')
        text = ''
        count = 0
        for i, user_id in enumerate(data):
            user = await get_user_from_chat(message.chat.id, user_id)
            text += f'{get_tag(user)}\n'
            count += 1
            if count == 5:
                count = 0
                await message.answer(text, parse_mode='HTML')
                text = ''
        await message.answer(text, parse_mode='HTML')
    else:
        await message.reply('У цьому чаті немає зареєстрованих Пупсиків, яких я міг би покликати 😢')


@dp.message(Command('create'))
async def cmd_numbers_create_game(message: Message) -> None:
    if message.chat.type == 'private':
        await message.reply('Цю команду можна використати тільки в групі 🧌')
        return

    chat_id = message.chat.id
    user_id = message.from_user.id

    is_successful = create_game(chat_id, user_id)
    if is_successful:
        await message.reply(f'🔢{get_link(message.from_user)} хоче зіграти в Числа!\nТикайте кнопку нижче👇',
                            reply_markup=kb_join_game(chat_id, user_id), parse_mode='HTML')
    else:
        await message.reply('У цьому чаті вже створена гра.')


@dp.message(Command('cancel'))
async def cmd_numbers_cancel(message: Message) -> None:
    if message.chat.type == 'private':
        await message.reply('Цю команду можна використати тільки в групі 🧌')
        return

    reply = cancel_game(message.chat.id)
    await message.answer(reply)


@dp.message(Command('guess'))
async def cmd_numbers_guess(message: Message) -> None:
    if message.chat.type == 'private':
        await message.reply('Цю команду можна використати тільки в групі 🧌')
        return

    chat_id = message.chat.id
    user = message.from_user

    _, *text = message.text.strip().split()
    is_successful, reply = guess_number(chat_id, user.id, text)

    if not is_successful:
        await message.reply(reply)
        return

    await message.reply(reply)
    await asyncio.sleep(1.5)

    str_opponent_id = get_opponent_id(chat_id, user.id)
    opponent = await get_user_from_chat(chat_id, int(str_opponent_id))

    opponent_link = get_link(opponent)
    user_link = get_link(user)

    user_guesses = get_guesses(chat_id, user.id)
    opponent_guesses = get_guesses(chat_id, opponent.id)

    user_attempts = user_guesses.count('\n')
    opponent_attempts = opponent_guesses.count('\n')

    user_finished = get_user_finished(chat_id, user.id)
    opponent_finished = get_user_finished(chat_id, opponent.id)

    if user_attempts == opponent_attempts:
        if user_finished:
            if opponent_finished:
                result = 'draw'
            else:
                result = 'user win'
        else:
            if opponent_finished:
                result = 'opponent win'
            else:
                result = 'continue'
    else:
        if user_finished:
            result = 'chance for draw'
        else:
            result = 'continue'

    match result:
        case 'user win':
            ending = ''
            if user_attempts == 1:
                ending = 'у'
            elif 2 <= user_attempts <= 4:
                ending = 'и'
            await message.answer(
                f'🥳🎉 ПЕРЕМОГА!\n{user_link} вгадав(-ла) число за {user_attempts} спроб{ending}.\n'
                f'Його/Її число було: {get_number(chat_id, user.id)}', parse_mode='HTML')
            delete_game(chat_id)

        case 'opponent win':
            ending = ''
            if opponent_attempts == 1:
                ending = 'у'
            elif 2 <= opponent_attempts <= 4:
                ending = 'и'
            await message.answer(f'🥳🎉 ПЕРЕМОГА!\n{opponent_link} вгадав(-ла) число за {opponent_attempts} спроб{ending}.\n'
                                 f'Його/Її число було: {get_number(chat_id, opponent.id)}', parse_mode='HTML')
            delete_game(chat_id)

        case 'draw':
            await message.answer('🏁 НІЧИЯ! Обидва гравці вгадали число за однакову кількість спроб 🤝')
            delete_game(chat_id)

        case 'chance for draw':
            ending = ''
            if user_attempts == 1:
                ending = 'у'
            elif 2 <= user_attempts <= 4:
                ending = 'и'
            await message.answer(
                f'{user_link} уже вгадав(-ла) число за {user_attempts} спроб{ending}, але {opponent_link} ще має шанс 🤔',
                parse_mode='HTML')

        case 'continue':
            await message.answer(f'Спроби {user_link}:\n' + user_guesses, parse_mode='HTML')
            await message.answer(f'🟢Черга {opponent_link}', parse_mode='HTML')
            if opponent_attempts != 0:
                await message.answer(f'Спроби {opponent_link}:\n' + opponent_guesses, parse_mode='HTML')


@dp.callback_query(F.data.startswith('join_game'))
async def callback_join_game(callback: CallbackQuery) -> None:
    _, str_chat_id, str_creator_id = callback.data.split('/')
    chat_id = int(str_chat_id)
    creator_id = int(str_creator_id)
    joiner = callback.from_user

    is_successful, msg = join_to_game(chat_id, joiner.id, creator_id)

    if is_successful:
        creator = await get_user_from_chat(chat_id, creator_id)
        creator_tag = get_tag(creator)
        joiner_tag = get_tag(joiner)

        text = f'🟢Опонент знайшовся!\n{creator_tag} та {joiner_tag} надішліть свої числа мені в особисті повідомлення🤗'
        await callback.message.answer(text=text, parse_mode='HTML')
        await callback.message.delete()
        await callback.answer()

        instructions = (
            '🧠 Чекаю ваше 4-цифрове число!\n\n'
            '✅ Число не повинно:\n'
            '• починатися з 0\n'
            '• мати повторювані цифри\n\n'
            '📩 Просто надішли число без додаткових символів.\n\n'
            'Або тикай кнопку нижче, щоб я сам обрав для тебе число👇'
        )
        await callback.bot.send_message(creator.id, instructions, reply_markup=kb_random_num())
        await callback.bot.send_message(joiner.id, instructions, reply_markup=kb_random_num())
    else:
        await callback.answer(text=msg, show_alert=True)


@dp.callback_query(F.data == 'gen_random_num')
async def callback_gen_random_num(callback: CallbackQuery) -> None:
    str_number = get_random_num()
    instructions = (
        '🧠 Чекаю ваше 4-цифрове число!\n\n'
        '✅ Число не повинно:\n'
        '• починатися з 0\n'
        '• мати повторювані цифри\n\n'
        '📩 Просто надішли число без додаткових символів.\n\n'
        f'Можеш обрати число <u>{str_number}</u>, або натиснути кнопку ще раз👇'
    )
    await callback.message.edit_text(text=instructions, reply_markup=kb_random_num(), parse_mode='HTML')
    await callback.answer()


@dp.callback_query(F.data.startswith('baby_unreg'))
async def callback_baby_unreg(callback: CallbackQuery) -> None:
    _, action, str_chat_id, str_creator_id = callback.data.split('/')
    user = callback.from_user

    if user.id != int(str_creator_id):
        await callback.answer(text='Ці кнопки не для тебе🧌', show_alert=True)
        return
    if action == 'decline':
        await callback.answer(text='Виключення тебе з Пупсиків відхилено✅', show_alert=True)
        await callback.message.delete()
        return
    deleted = unregister_user(int(str_chat_id), int(str_creator_id))
    if deleted:
        await callback.answer('Тебе було виключино з Пупсиків😢', show_alert=True)
        await callback.message.answer(f'{get_link(user)} покинув список Пупсиків😭', parse_mode='HTML')
        await callback.message.delete()
    else:
        await callback.answer(text='Тебе не було в списку пупсиків. Варто приєднатися!', show_alert=True)


@dp.message(Command('get_baby_stats'), F.chat.type == 'private', F.from_user.id == 1250738671)
async def admin_cmd_get_baby_stats(message: Message) -> None:
    file = FSInputFile(get_path())
    await message.answer_document(file, caption='Ось файл зі статистикою пупсиків 👶')


@dp.message(Command('upload_baby_stats'), F.chat.type == 'private', F.from_user.id == 1250738671)
async def admin_cmd_upload_baby_stats(message: Message) -> None:
    if not message.document:
        await message.answer('Будь ласка, надішли файл як документ.')
        return

    if not message.document.file_name.endswith('.json'):
        await message.answer('Це має бути JSON-файл.')
        return

    file = await message.bot.get_file(message.document.file_id)
    await message.bot.download_file(file.file_path, 'temp_uploaded.json')

    shutil.move('temp_uploaded.json', get_path())

    await message.answer('Файл зі статистикою успішно оновлено.')


@dp.message(F.chat.type == 'private')
async def set_number(message: Message) -> None:
    user_id = message.from_user.id
    number_str = message.text.strip()

    success, reply, group_id, first_player_id = set_player_number(user_id, number_str)

    await message.answer(reply)

    if success and group_id is not None and first_player_id is not None:
        first_player = (await bot.get_chat_member(group_id, first_player_id)).user
        await message.bot.send_message(group_id, '🎯 Обидва гравці надіслали числа! Починаймо гру!')
        await message.bot.send_message(group_id, f'🟢Черга {get_link(first_player)}\n'
                                                 f'📩Надсилай спробу через команду /guess [твоя_здогадка]',
                                       parse_mode='HTML')


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
