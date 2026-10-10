import random

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from word_bank import make_variants

PRACTICE_TEXT = "🧠 Практика"
THEORY_TEXT = "📖 Теорія"
SHUFFLE_ON_TEXT = "🔀 Перемішування: УВІМК"
SHUFFLE_OFF_TEXT = "🔀 Перемішування: ВИМК"
STOP_BUTTON_TEXT = "⛔ Завершити тест"


def main_menu(shuffle: bool = False) -> ReplyKeyboardMarkup:
    toggle = SHUFFLE_ON_TEXT if shuffle else SHUFFLE_OFF_TEXT
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=PRACTICE_TEXT), KeyboardButton(text=THEORY_TEXT)],
            [KeyboardButton(text=toggle)],
        ],
        resize_keyboard=True,
    )


SCOPE_KEYBOARD = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Усі слова", callback_data="scope:all")],
        [InlineKeyboardButton(text="Обрати літери", callback_data="scope:letters")],
    ]
)

THEORY_SCOPE_KEYBOARD = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Усі слова", callback_data="theory:all")],
        [InlineKeyboardButton(text="Обрати літери", callback_data="theory:letters")],
    ]
)


def variants_keyboard(entry: dict, shuffle: bool = False) -> ReplyKeyboardMarkup:
    """Клавіатура з варіантами наголосу під полем вводу (по 2 в ряд).
    Якщо shuffle=True — порядок кнопок щоразу випадковий."""
    variants = make_variants(entry)
    if shuffle:
        random.shuffle(variants)
    rows = [variants[i : i + 2] for i in range(0, len(variants), 2)]
    keyboard = [[KeyboardButton(text=v) for v in row] for row in rows]
    keyboard.append([KeyboardButton(text=STOP_BUTTON_TEXT)])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
