import asyncio
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from aiogram.filters import Command

from src.func_results import SetNumberResult
from src.tools import numbers as num
from src.tools import user as us
from src import keyboards as kb
from src import midwares_filters as mwf

router = Router()


@router.message(Command('create'), mwf.GroupOnlyFilter())
async def cmd_create_game(message: Message) -> None:
    chat_id = message.chat.id
    user_id = message.from_user.id

    is_successful = num.create_game(chat_id, user_id)
    if is_successful:
        await message.answer(f'🔢{us.get_user_link(user_id)} хоче зіграти в Числа!\nТикайте кнопку нижче👇',
                            reply_markup=kb.num_join_game(chat_id, user_id), parse_mode='HTML')
    else:
        await message.reply('У цьому чаті вже створена гра.')


@router.message(Command('cancel'), mwf.GroupOnlyFilter())
async def cmd_cancel_game(message: Message) -> None:
    reply = num.cancel_game(message.chat.id)
    await message.answer(reply)


@router.inline_query()
async def inline_sending_guess(query: InlineQuery):
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


@router.callback_query(F.data.startswith('num_join'))
async def callback_join_game(callback: CallbackQuery) -> None:
    _, str_chat_id, str_creator_id = callback.data.split('/')
    chat_id = int(str_chat_id)
    creator_id = int(str_creator_id)
    joiner_id = callback.from_user.id

    is_successful, msg = num.join_game(chat_id, joiner_id, creator_id)

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


@router.callback_query(F.data == 'gen_random_num')
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


@router.message(F.via_bot.id == F.bot.id)
async def handle_guess(message: Message) -> None:
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


async def awaiting_number_filter(message: Message) -> bool:
    return num.is_awaiting_number(message.from_user.id)


@router.message(F.chat.type == 'private', F.text, awaiting_number_filter)
async def set_number(message: Message) -> None:
    user_id = message.from_user.id
    number_str = message.text.strip()

    result: SetNumberResult = num.set_player_number(user_id, number_str)

    await message.answer(result.message)

    if result.game_ready:
        await message.bot.send_message(result.chat_id, '🎯 Обидва гравці надіслали числа! Починаймо гру!')
        await message.bot.send_message(result.chat_id, f'🟢Черга {us.get_user_link(result.first_player_id)}\n'
                                                 f'📩Надсилай здогадку написавши @PyUnicornBot',
                                                 parse_mode='HTML')
