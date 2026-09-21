from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from word_bank import make_variants

MAIN_MENU = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🧠 Практика")]],
    resize_keyboard=True,
)

SCOPE_KEYBOARD = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Усі слова", callback_data="scope:all")],
        [InlineKeyboardButton(text="Обрати літери", callback_data="scope:letters")],
    ]
)

STOP_BUTTON_TEXT = "⛔ Завершити тест"


def variants_keyboard(entry: dict) -> ReplyKeyboardMarkup:
    """Клавіатура з варіантами наголосу під полем вводу (по 2 в ряд)."""
    variants = make_variants(entry)
    rows = [variants[i : i + 2] for i in range(0, len(variants), 2)]
    keyboard = [[KeyboardButton(text=v) for v in row] for row in rows]
    keyboard.append([KeyboardButton(text=STOP_BUTTON_TEXT)])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
