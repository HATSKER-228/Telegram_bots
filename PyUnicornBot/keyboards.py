from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def kb_join_game(chat_id: int, creator_id: int) -> InlineKeyboardMarkup:
	btn = InlineKeyboardButton(text='Приєднатися✅', callback_data=f'join_game/{chat_id}/{creator_id}')
	return InlineKeyboardMarkup(inline_keyboard=[[btn]])


def kb_random_num() -> InlineKeyboardMarkup:
	btn = InlineKeyboardButton(text='Рандомне число🎲', callback_data='gen_random_num')
	return InlineKeyboardMarkup(inline_keyboard=[[btn]])


def kb_submit_baby_unreg(chat_id: int, user_id: int) -> InlineKeyboardMarkup:
	submit = InlineKeyboardButton(text='Так✅', callback_data=f'baby_unreg/submit/{chat_id}/{user_id}')
	decline = InlineKeyboardButton(text='Ні❌', callback_data=f'baby_unreg/decline/{chat_id}/{user_id}')
	return InlineKeyboardMarkup(inline_keyboard=[[submit, decline]])
