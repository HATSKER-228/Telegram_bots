from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from src.tools import blackjack as bj
from src.tools import user as us
from src import keyboards as kb
from src import midwares_filters as mwf

router = Router()


@router.message(Command('blackjack'), mwf.GroupOnlyFilter())
async def cmd_create_game(message: Message) -> None:
    chat_id = message.chat.id
    user_id = message.from_user.id

    is_successful = bj.create_game(chat_id, user_id)
    if is_successful:
        await message.answer(text=bj.get_lobby_text(chat_id),
                             reply_markup=kb.bj_join_game(chat_id), parse_mode='HTML')
    else:
        await message.reply('У цьому чаті вже створена гра.')


@router.callback_query(F.data.startswith('bj_join'))
async def callback_join_game(callback: CallbackQuery) -> None:
    _, str_chat_id = callback.data.split('/')
    chat_id = int(str_chat_id)
    user_id = callback.from_user.id

    is_successful, msg = bj.join_game(chat_id, user_id)

    if is_successful:
        text = bj.get_lobby_text(chat_id)
        await callback.message.edit_text(text=text, reply_markup=kb.bj_join_game(chat_id), parse_mode='HTML')
        await callback.answer()
    else:
        await callback.answer(text=msg, show_alert=True)


@router.callback_query(F.data.startswith('bj_start'))
async def callback_start_game(callback: CallbackQuery) -> None:
    _, str_chat_id = callback.data.split('/')
    chat_id = int(str_chat_id)
    user_id = callback.from_user.id

    is_successful, msg = bj.start_game(chat_id, user_id)

    if not is_successful:
        await callback.answer(text=msg, show_alert=True)
        return

    await callback.message.delete()
    await callback.answer()
    await callback.bot.send_message(chat_id, text=bj.get_round_text(chat_id),
                                    reply_markup=kb.bj_actions(chat_id), parse_mode='HTML')


@router.callback_query(F.data.startswith('bj_show'))
async def callback_show_hand(callback: CallbackQuery) -> None:
    _, str_chat_id = callback.data.split('/')
    chat_id = int(str_chat_id)
    user_id = callback.from_user.id

    await callback.answer(text=bj.get_show_hand_text(chat_id, user_id), show_alert=True)


@router.callback_query(F.data.startswith('bj_hit'))
async def callback_hit(callback: CallbackQuery) -> None:
    # TODO
    _, str_chat_id = callback.data.split('/')
    chat_id = int(str_chat_id)
    user_id = callback.from_user.id

    result = bj.hit(chat_id, user_id)

    await callback.answer(text=result.message, show_alert=True)

    if result.success:
        await callback.message.edit_text(text=bj.get_round_text(chat_id), parse_mode='HTML',
                                         reply_markup=kb.bj_actions(chat_id))
        await callback.bot.send_message(chat_id, text=f'{us.get_user_link(user_id)} взяв(-ла) карту 🃏',
                                        parse_mode='HTML')


@router.callback_query(F.data.startswith('bj_stand'))
async def callback_stand(callback: CallbackQuery) -> None:
    # TODO
    _, str_chat_id = callback.data.split('/')
    chat_id = int(str_chat_id)
    user_id = callback.from_user.id

    result = bj.stand(chat_id, user_id)

    await callback.answer(text=result.message, show_alert=True)

    if result.success:
        await callback.message.edit_text(text=bj.get_round_text(chat_id), parse_mode='HTML',
                                         reply_markup=kb.bj_actions(chat_id))
        await callback.bot.send_message(chat_id, text=f'{us.get_user_link(user_id)} завершив(-ла) набирати карти 🃏',
                                        parse_mode='HTML')
