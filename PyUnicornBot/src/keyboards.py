from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def num_join_game(chat_id: int, creator_id: int) -> InlineKeyboardMarkup:
    btn = InlineKeyboardButton(text='Приєднатися✅', callback_data=f'num_join/{chat_id}/{creator_id}')
    return InlineKeyboardMarkup(inline_keyboard=[[btn]])


def random_num() -> InlineKeyboardMarkup:
    btn = InlineKeyboardButton(text='Рандомне число🎲', callback_data='gen_random_num')
    return InlineKeyboardMarkup(inline_keyboard=[[btn]])


def baby_unreg(chat_id: int, user_id: int) -> InlineKeyboardMarkup:
    submit = InlineKeyboardButton(text='Так✅', callback_data=f'baby_unreg/submit/{chat_id}/{user_id}')
    decline = InlineKeyboardButton(text='Ні❌', callback_data=f'baby_unreg/decline/{chat_id}/{user_id}')
    return InlineKeyboardMarkup(inline_keyboard=[[submit, decline]])


def go_to_bot_pm() -> InlineKeyboardMarkup:
    btn = InlineKeyboardButton(text='Перейти до бота💬', url='https://t.me/PyUnicornBot')
    return InlineKeyboardMarkup(inline_keyboard=[[btn]])


def bj_join_game(chat_id: int) -> InlineKeyboardMarkup:
    join = InlineKeyboardButton(text='Приєднатися✅', callback_data=f'bj_join/{chat_id}')
    start = InlineKeyboardButton(text='Почати гру▶️', callback_data=f'bj_start/{chat_id}')
    return InlineKeyboardMarkup(inline_keyboard=[[join], [start]])


def bj_actions(chat_id: int) -> InlineKeyboardMarkup:
    hit = InlineKeyboardButton(text='Добрати🃏', callback_data=f'bj_hit/{chat_id}')
    stand = InlineKeyboardButton(text='Утриматись✋', callback_data=f'bj_stand/{chat_id}')
    show_hand = InlineKeyboardButton(text='Нагади мої карти👀', callback_data=f'bj_show/{chat_id}')
    return InlineKeyboardMarkup(inline_keyboard=[[hit, stand], [show_hand]])
