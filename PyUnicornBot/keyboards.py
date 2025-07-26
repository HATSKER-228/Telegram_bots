from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def kb_join_game(chat_id: int, creator_id: int) -> InlineKeyboardMarkup:
	btn = InlineKeyboardButton(text='Приєднатися✅', callback_data=f'join_game/{chat_id}/{creator_id}')
	return InlineKeyboardMarkup(inline_keyboard=[[btn]])
