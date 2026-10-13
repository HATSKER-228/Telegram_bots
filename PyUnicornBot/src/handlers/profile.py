from html import escape
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from src.tools import blackjack_stats as bj_stats

router = Router()


@router.message(Command('profile'))
async def cmd_profile(message: Message) -> None:
    user = message.from_user
    stats = bj_stats.get_stats(user.id)

    games = stats['games']
    winrate = f'{stats["wins"] / games * 100:.1f}%' if games else '—'

    text = (
        f'👤 <b>Профіль: {escape(user.full_name)}</b>\n\n'
        f'🃏 <u>Блекджек</u>\n'
        f'• Зіграно ігор: <b>{games}</b>\n'
        f'• 🏆 Перемог: <b>{stats["wins"]}</b>\n'
        f'• 🤝 Нічиїх: <b>{stats["draws"]}</b>\n'
        f'• ❌ Поразок: <b>{stats["losses"]}</b>\n'
        f'• 📊 Вінрейт: <b>{winrate}</b>'
    )
    await message.answer(text, parse_mode='HTML')