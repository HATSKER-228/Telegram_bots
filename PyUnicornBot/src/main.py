import asyncio
import shutil
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, FSInputFile, InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from random import randint, choice

import baby_tools as baby
import numbers_tools as num
import user_tools as us
import keyboards as kb
import fix_layout as fl
import midwares_filters as mwf

ADMIN_ID = 1250738671
bot = Bot(token=os.environ.get('TOKEN'))
dp = Dispatcher()

dp.update.middleware(mwf.UserUpdateMiddleware())


@dp.message(Command('start'))
async def cmd_start(message: Message) -> None:
    if message.chat.type == 'private':
        text = 'Привіт, пупсику ❤️. Я - Unicorn Bot. Ти можеш побачити, що я вмію робити, надіславши команду /help.'
    elif message.chat.type in {'group', 'supergroup'}:
        text = 'Привіт, пупсики ❤️. Я - Unicorn Bot. Ви можете побачити, що я вмію робити, надіславши команду /help@PyUnicornBot.'
    else:
        text = 'Цю команду можна використати тільки в групі або в особистих повідомленнях зі мною 🧌'
    await message.answer(text)


@dp.message(Command('help'))
async def cmd_help(message: Message) -> None:
    await message.answer('''Ось список того, що я вмію:
/start - привітаннячка від мене
/help - надішлю оце повідомлення
/fix - виправлю розкладку повідомлення (з qwerty на йцукен, або ж навпаки)
/shypko - оціню повідомлення від 0 до 10
/rules - надішлю правила кожної мініігри
/updates - скажу що нового

<b>!!!Тільки в групі!!!</b>
<u>Пупсик дня</u>
/baby_reg - додам тебе у список Пупсиків
/baby_unreg - видалю тебе з Пупсиків
/baby_select - оберу Пупсика дня (лише раз в день)
/baby_stats - надішлю статистику хто скільки разів був Пупсиком дня

<u>Гра "Числа"</u>
/create - створю гру
/cancel - скасувати гру''', parse_mode='HTML')


@dp.message(Command('fix'), mwf.ReplyOnlyFilter())
async def cmd_fix(message: Message) -> None:
    replied = message.reply_to_message
    text = replied.text or replied.caption
    entities = replied.entities or replied.caption_entities

    if text:
        src = fl.detect_layout(text)
        dst = fl.KB_LAYOUT_PAIRS[src]
        fixed = fl.fix_layout(text, entities, fl.KB_LAYOUTS[src], fl.KB_LAYOUTS[dst])

        await replied.reply(text=fixed, entities=entities)
        await message.delete()
    else:
        await message.reply('Шановний тупорилий представник виду <i>Homo Sapiens</i>, команду необхідно писати у '
                            'відповідь на ТЕКСТ 🧌', parse_mode='HTML')


@dp.message(Command('shypko'), mwf.ReplyOnlyFilter())
async def cmd_shypko(message: Message) -> None:
    await message.reply_to_message.reply(f'Я оцінюю це повідомлення на {randint(0, 10)} шипко з 10.')


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
• Після цього гравці по черзі надсилають у групу здогадки, написавши @PyUnicornBot.
• Я у відповідь надсилаю підказку виду ХХО або ж ХХОО:
    X — цифра є і стоїть на правильному місці.
    O — цифра є, але стоїть не там.
• Розташування символів в підказці не пов'язане з розташуванням цифр у числі опонента.
• Виграє той, хто першим вгадає число суперника повністю.
• Якщо хочете скасувати гру — напишіть /cancel.
• В одній групі може бути лише одна активна гра.
• Якшо гра не активна більше доби, вона автоматично видаляється'''
    await message.answer(text, parse_mode='HTML')


@dp.message(Command('updates'))
async def cmd_updates(message: Message) -> None:
    text = '''📜 <u><b>Що нового у Unicorn Bot</b></u>
<b>17.07.2026</b>    
<i>Анімація обирання Пупсика дня</i>
• Якшо Пупсика сьогодні все ще не обрано, то під час вибору бот буде крутить рулетку хто сьогодні Пупсик.

<i>Різні виправлення помилок та оптимізація</i>

<b>07.07.2026</b>
<i>Оновлення в грі "Числа"</i>
• Якшо гра неактивна більше ніж добу, вона автоматично видаляється.
• При спробі відправити не валідне число як здогадку, з'являється табличка, що число не валідне.
• Тепер бот не спамить "⚠️ Немає гри, де очікується число." в приватних повідомленнях, якшо немає гри, в який користувач бере участь.

<i>Різні виправлення помилок</i>

<u><b>Попередні оновлення:</b></u>
07.01.2026 - оновлення команди /fix, inline-прийняття спроб у грі "Числа"
05.01.2026 - оновлення команди /fix
03.01.2026 - додання команди /updates, кешування імен користувачів
08.11.2025 - видалення команди /all
04.08.2025 - оновлення команди /baby_unreg
01.08.2025 - додання команди /all
28.07.2025 - додання кнопки "Рандомне число" у грі "Числа"
27.07.2025 - додання команд /rules, /shypko, а також показ числа переможця у грі "Числа"
26.07.2025 - додання гри "Числа"
18.07.2025 - додання Пупсиків дня
18.07.2025 - перехід на бібліотеку aiogram
'''
    await message.answer(text, parse_mode='HTML')


@dp.message(Command('baby_reg'), mwf.GroupOnlyFilter())
async def cmd_baby_reg(message: Message) -> None:
    user = message.from_user

    added = baby.register_user(message.chat.id, user.id)
    if added:
        await message.reply(f'{us.get_user_tag(user.id)} тепер у списку пупсиків! 🐣', parse_mode='HTML')
    else:
        await message.reply('Ти вже зареєстрований як пупсик 😘')


@dp.message(Command('baby_unreg'), mwf.GroupOnlyFilter())
async def cmd_baby_unreg(message: Message) -> None:
    user_id = message.from_user.id
    in_list = baby.is_in_list(message.chat.id, user_id)
    if not in_list:
        await message.reply(f'Тебе не було в списку пупсиків. Варто приєднатися!')
        return

    keyboard = kb.baby_unreg(message.chat.id, user_id)
    await message.answer(f'{us.get_user_link(user_id)}, ти точно хочеш вийти зі списку Пупсиків?', parse_mode='HTML', reply_markup=keyboard)
    await message.delete()


@dp.message(Command('baby_select'), mwf.GroupOnlyFilter())
async def cmd_baby_select(message: Message) -> None:
    chat_id: int = message.chat.id
    is_successful, baby_id = baby.select_baby(chat_id)

    if not is_successful and baby_id is None:
        await message.reply('У цьому чаті ще немає зареєстрованих пупсіків😢')
        return

    if not is_successful:
        await message.reply(f'Сьогоднішній пупсік уже обраний: {us.get_user_tag(baby_id)}💖', parse_mode='HTML')
        return

    players = baby.get_players(chat_id)
    candidates = [p for p in players if p != baby_id] or players

    spin_frames = ['🎰', '🎲', '🔄', '🌀', '✨']
    spin_msg = await message.answer(f'{spin_frames[0]} Запускаю рулеточку Пупсиків...')

    for i in range(6):
        await asyncio.sleep(1)
        candidate = choice(candidates) if candidates else baby_id
        frame = spin_frames[i % len(spin_frames)]
        try:
            await spin_msg.edit_text(
                f'{frame} Кручу-верчу, обрати Пупсика хочу...\n👉 {us.get_user_tag(candidate)}',
                parse_mode='HTML'
            )
        except Exception:
            pass
    await asyncio.sleep(1)
    await spin_msg.edit_text('А ось і він ...', parse_mode='HTML')
    await message.answer(f'🎉 Пупсик дня — {us.get_user_tag(baby_id)}!', parse_mode='HTML')


@dp.message(Command('baby_stats'), mwf.GroupOnlyFilter())
async def cmd_baby_stats(message: Message) -> None:
    data = baby.get_stats(message.chat.id)
    if data:
        s = 'Статистика Пупсиків дня:\n'
        for index, (user_id, count) in enumerate(data):
            s += f'{index+1}) {us.get_username(user_id)} - {count}\n'
        await message.reply(s)
    else:
        await message.reply('У цьому чаті ще немає зареєстрованих Пупсіків 😢')


@dp.message(Command('create'), mwf.GroupOnlyFilter())
async def cmd_numbers_create_game(message: Message) -> None:
    chat_id = message.chat.id
    user_id = message.from_user.id

    is_successful = num.create_game(chat_id, user_id)
    if is_successful:
        await message.reply(f'🔢{us.get_user_link(user_id)} хоче зіграти в Числа!\nТикайте кнопку нижче👇',
                            reply_markup=kb.join_game(chat_id, user_id), parse_mode='HTML')
    else:
        await message.reply('У цьому чаті вже створена гра.')


@dp.message(Command('cancel'), mwf.GroupOnlyFilter())
async def cmd_numbers_cancel(message: Message) -> None:
    reply = num.cancel_game(message.chat.id)
    await message.answer(reply)


@dp.message(F.via_bot.id == F.bot.id)
async def numbers_guess(message: Message) -> None:
    chat_id = message.chat.id
    user_id = message.from_user.id

    number = message.text.strip()
    is_successful, reply = num.guess_number(chat_id, user_id, number)

    if not is_successful:
        await message.reply(reply)
        return

    await message.reply(reply)
    await asyncio.sleep(1.5)

    data = num.load_data()

    opponent_id = num.get_opponent_id(chat_id, user_id, data)

    opponent_link = us.get_user_link(opponent_id)
    user_link = us.get_user_link(user_id)

    user_guesses = num.get_guesses(chat_id, user_id, data)
    opponent_guesses = num.get_guesses(chat_id, opponent_id, data)

    user_attempts = len(user_guesses)
    opponent_attempts = len(opponent_guesses)

    user_finished = num.get_user_finished(chat_id, user_id, data)
    opponent_finished = num.get_user_finished(chat_id, opponent_id, data)

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
                f'Його/Її число було: {num.get_number(chat_id, user_id, data)}', parse_mode='HTML')
            num.delete_game(chat_id)

        case 'opponent win':
            ending = ''
            if opponent_attempts == 1:
                ending = 'у'
            elif 2 <= opponent_attempts <= 4:
                ending = 'и'
            await message.answer(f'🥳🎉 ПЕРЕМОГА!\n{opponent_link} вгадав(-ла) число за {opponent_attempts} спроб{ending}.\n'
                                 f'Його/Її число було: {num.get_number(chat_id, opponent_id, data)}', parse_mode='HTML')
            num.delete_game(chat_id)

        case 'draw':
            await message.answer('🏁 НІЧИЯ! Обидва гравці вгадали число за однакову кількість спроб 🤝')
            num.delete_game(chat_id)

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
            await message.answer(f'Спроби {user_link}:\n' + num.format_guesses(user_guesses), parse_mode='HTML')
            await message.answer(f'🟢Черга {opponent_link}', parse_mode='HTML')
            if opponent_attempts != 0:
                await message.answer(f'Спроби {opponent_link}:\n' + num.format_guesses(opponent_guesses), parse_mode='HTML')


@dp.inline_query()
async def inline_guess_number(query: InlineQuery):
    text = query.query.strip()

    if not text:
        await query.answer(results=[], is_personal=True, cache_time=1)
        return

    if not text.isdigit() or len(text) != 4 or text[0] == '0' or len(set(text)) != 4:
        result = InlineQueryResultArticle(
            id='invalid_number',
            title='❌ Не валідне число',
            description='• рівно 4 цифри\n• не починається з 0\n• всі цифри різні',
            input_message_content=InputTextMessageContent(message_text='Яке треба число?')
        )
        await query.answer(results=[result], is_personal=True, cache_time=1)
        return

    result = InlineQueryResultArticle(
        id='numbers_guess',
        title=f'Зробити припущення: {text}',
        description='Надіслати це число як здогадку',
        input_message_content=InputTextMessageContent(message_text=text)
    )

    await query.answer(results=[result], is_personal=True, cache_time=1)


@dp.callback_query(F.data.startswith('join_game'))
async def callback_join_game(callback: CallbackQuery) -> None:
    _, str_chat_id, str_creator_id = callback.data.split('/')
    chat_id = int(str_chat_id)
    creator_id = int(str_creator_id)
    joiner_id = callback.from_user.id

    is_successful, msg = num.join_to_game(chat_id, joiner_id, creator_id)

    if is_successful:
        creator_tag = us.get_user_tag(creator_id)
        joiner_tag = us.get_user_tag(joiner_id)

        text = f'🟢Опонент знайшовся!\n{creator_tag} та {joiner_tag} надішліть свої числа мені в особисті повідомлення🤗'
        await callback.message.answer(text=text, parse_mode='HTML', reply_markup=kb.go_to_bot_pm())
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
        await callback.bot.send_message(creator_id, instructions, reply_markup=kb.random_num())
        await callback.bot.send_message(joiner_id, instructions, reply_markup=kb.random_num())
    else:
        await callback.answer(text=msg, show_alert=True)


@dp.callback_query(F.data == 'gen_random_num')
async def callback_gen_random_num(callback: CallbackQuery) -> None:
    str_number = num.get_random_num()
    instructions = (
        '🧠 Чекаю ваше 4-цифрове число!\n\n'
        '✅ Число не повинно:\n'
        '• починатися з 0\n'
        '• мати повторювані цифри\n\n'
        '📩 Просто надішли число без додаткових символів.\n\n'
        f'Можеш обрати число <u>{str_number}</u>, або натиснути кнопку ще раз👇'
    )
    await callback.message.edit_text(text=instructions, reply_markup=kb.random_num(), parse_mode='HTML')
    await callback.answer()


@dp.callback_query(F.data.startswith('baby_unreg'))
async def callback_baby_unreg(callback: CallbackQuery) -> None:
    _, action, str_chat_id, str_creator_id = callback.data.split('/')
    user_id = callback.from_user.id

    if user_id != int(str_creator_id):
        await callback.answer(text='Ці кнопки не для тебе🧌', show_alert=True)
        return
    if action == 'decline':
        await callback.answer(text='Виключення тебе з Пупсиків відхилено✅', show_alert=True)
        await callback.message.delete()
        return
    deleted = baby.unregister_user(int(str_chat_id), int(str_creator_id))
    if deleted:
        await callback.answer('Тебе було виключено з Пупсиків😢', show_alert=True)
        await callback.message.answer(f'{us.get_user_link(user_id)} покинув список Пупсиків😭', parse_mode='HTML')
        await callback.message.delete()
    else:
        await callback.answer(text='Тебе не було в списку пупсиків. Варто приєднатися!', show_alert=True)


@dp.message(Command('get_jsons'), F.chat.type == 'private', F.from_user.id == ADMIN_ID)
async def admin_cmd_get_jsons(message: Message) -> None:
    babies = FSInputFile(baby.FILE_PATH)
    numbers = FSInputFile(num.FILE_PATH)
    users = FSInputFile(us.FILE_PATH)
    await message.answer_document(babies)
    await message.answer_document(numbers)
    await message.answer_document(users)


@dp.message(Command('upload_baby_stats'), F.chat.type == 'private', F.from_user.id == ADMIN_ID)
async def admin_cmd_upload_baby_stats(message: Message) -> None:
    if not message.document:
        await message.answer('Будь ласка, надішли файл як документ.')
        return

    if not message.document.file_name.endswith('.json'):
        await message.answer('Це має бути JSON-файл.')
        return

    file = await message.bot.get_file(message.document.file_id)
    await message.bot.download_file(file.file_path, 'temp_uploaded.json')

    shutil.move('temp_uploaded.json', baby.FILE_PATH)

    await message.answer('Файл зі статистикою успішно оновлено.')


@dp.message(Command('upload_users_data'), F.chat.type == 'private', F.from_user.id == ADMIN_ID)
async def admin_cmd_upload_users_data(message: Message) -> None:
    if not message.document:
        await message.answer('Будь ласка, надішли файл як документ.')
        return

    if not message.document.file_name.endswith('.json'):
        await message.answer('Це має бути JSON-файл.')
        return

    file = await message.bot.get_file(message.document.file_id)
    await message.bot.download_file(file.file_path, 'temp_uploaded.json')

    shutil.move('temp_uploaded.json', us.FILE_PATH)

    await message.answer('Файл успішно оновлено.')


async def awaiting_number_filter(message: Message) -> bool:
    return num.is_awaiting_number(message.from_user.id)


@dp.message(F.chat.type == 'private', F.text, awaiting_number_filter)
async def set_number(message: Message) -> None:
    user_id = message.from_user.id
    number_str = message.text.strip()

    success, reply, group_id, first_player_id = num.set_player_number(user_id, number_str)

    await message.answer(reply)

    if success and group_id is not None and first_player_id is not None:
        await message.bot.send_message(group_id, '🎯 Обидва гравці надіслали числа! Починаймо гру!')
        await message.bot.send_message(group_id, f'🟢Черга {us.get_user_link(first_player_id)}\n'
                                                 f'📩Надсилай здогадку написавши @PyUnicornBot',
                                                 parse_mode='HTML')


async def cleanup_stale_games_loop() -> None:
    while True:
        await asyncio.sleep(60 * 60)  # раз на годину
        stale_chat_ids = num.cleanup_stale_games()
        for str_chat_id in stale_chat_ids:
            try:
                await bot.send_message(int(str_chat_id), '🗑 Гру "Числа" видалено через бездіяльність (більше доби без активності).')
            except Exception:
                pass  # бота могли видалити з чату/заблокувати за цей час


async def main() -> None:
    asyncio.create_task(cleanup_stale_games_loop())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
