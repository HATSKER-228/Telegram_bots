import asyncio
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from random import choice

from src.func_results import SelectBabyResult
from src.tools import baby as baby_tools
from src.tools import user as us
from src import keyboards as kb
from src import midwares_filters as mwf

router = Router()


@router.message(Command('baby_reg'), mwf.GroupOnlyFilter())
async def cmd_reg(message: Message) -> None:
    user = message.from_user

    added = baby_tools.register_user(message.chat.id, user.id)
    if added:
        await message.reply(f'{us.get_user_tag(user.id)} тепер у списку пупсиків! 🐣', parse_mode='HTML')
    else:
        await message.reply('Ти вже зареєстрований як пупсик 😘')


@router.message(Command('baby_unreg'), mwf.GroupOnlyFilter())
async def cmd_unreg(message: Message) -> None:
    user_id = message.from_user.id
    in_list = baby_tools.is_in_list(message.chat.id, user_id)
    if not in_list:
        await message.reply(f'Тебе не було в списку пупсиків. Варто приєднатися!')
        return

    keyboard = kb.baby_unreg(message.chat.id, user_id)
    await message.answer(f'{us.get_user_link(user_id)}, ти точно хочеш вийти зі списку Пупсиків?', parse_mode='HTML', reply_markup=keyboard)
    await message.delete()


@router.message(Command('baby_select'), mwf.GroupOnlyFilter())
async def cmd_select(message: Message) -> None:
    chat_id: int = message.chat.id
    result: SelectBabyResult = baby_tools.select_baby(chat_id)

    if not result.has_players:
        await message.reply('У цьому чаті ще немає зареєстрованих пупсіків😢')
        return

    if not result.selected:
        await message.reply(f'Сьогоднішній пупсік уже обраний: {us.get_user_tag(result.baby_id)}💖', parse_mode='HTML')
        return

    players = baby_tools.get_players(chat_id)
    candidates = [p for p in players if p != result.baby_id] or players

    spin_frames = ['🎰', '🎲', '🔄', '🌀', '✨']
    spin_msg = await message.answer(f'{spin_frames[0]} Запускаю рулеточку Пупсиків...')

    for i in range(6):
        await asyncio.sleep(1)
        candidate = choice(candidates) if candidates else result.baby_id
        frame = spin_frames[i % len(spin_frames)]
        try:
            await spin_msg.edit_text(
                f'{frame} Кручу-верчу, обрати Пупсика хочу...\n👉 {us.get_user_tag(candidate)}',
                parse_mode='HTML'
            )
        except Exception:
            pass
    await asyncio.sleep(1)
    try:
        await spin_msg.edit_text('А ось і він ...', parse_mode='HTML')
    except Exception:
        pass
    await message.answer(f'🎉 Пупсик дня — {us.get_user_tag(result.baby_id)}!', parse_mode='HTML')


@router.message(Command('baby_stats'), mwf.GroupOnlyFilter())
async def cmd_stats(message: Message) -> None:
    data = baby_tools.get_stats(message.chat.id)
    if data:
        s = 'Статистика Пупсиків дня:\n'
        for index, (user_id, count) in enumerate(data):
            s += f'{index+1}) {us.get_username(user_id)} - {count}\n'
        await message.reply(s)
    else:
        await message.reply('У цьому чаті ще немає зареєстрованих Пупсіків 😢')


@router.callback_query(F.data.startswith('baby_unreg'))
async def callback_unreg(callback: CallbackQuery) -> None:
    _, action, str_chat_id, str_creator_id = callback.data.split('/')
    user_id = callback.from_user.id

    if user_id != int(str_creator_id):
        await callback.answer(text='Ці кнопки не для тебе🧌', show_alert=True)
        return
    if action == 'decline':
        await callback.answer(text='Виключення тебе з Пупсиків відхилено✅', show_alert=True)
        await callback.message.delete()
        return
    deleted = baby_tools.unregister_user(int(str_chat_id), int(str_creator_id))
    if deleted:
        await callback.answer('Тебе було виключено з Пупсиків😢', show_alert=True)
        await callback.message.answer(f'{us.get_user_link(user_id)} покинув список Пупсиків😭', parse_mode='HTML')
        await callback.message.delete()
    else:
        await callback.answer(text='Тебе не було в списку пупсиків. Варто приєднатися!', show_alert=True)
