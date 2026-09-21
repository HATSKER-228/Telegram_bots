"""
Telegram-бот для тренування наголосів зі списку НМТ з української мови.
Запуск: python main.py (попередньо встанови BOT_TOKEN, див. config.py)
"""
import asyncio
import logging
import random

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import CallbackQuery, Message

import config
from keyboards import MAIN_MENU, SCOPE_KEYBOARD, STOP_BUTTON_TEXT, variants_keyboard
from states import Practice
from word_bank import (
    ALL_WORDS,
    correct_variants,
    filter_by_letters,
    is_correct,
    parse_letters,
    sample_words,
)

router = Router()


def word_display(entry: dict) -> str:
    text = entry["word"]
    if entry.get("note"):
        text += f" ({entry['note']})"
    return text


async def send_word(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    session = data["session"]
    entry = session["words"][session["index"]]
    idx = session["index"] + 1
    total = session["total"]
    await message.answer(
        f"Слово {idx} із {total}:\n\n"
        f"<b>{word_display(entry)}</b>\n\n"
        f"Обери правильний наголос 👇",
        reply_markup=variants_keyboard(entry),
    )


async def start_test(message: Message, state: FSMContext, pool: list) -> None:
    words = sample_words(pool, config.WORDS_PER_TEST)
    random.shuffle(words)
    await state.set_state(Practice.testing)
    await state.update_data(
        session={"words": words, "index": 0, "correct": 0, "total": len(words)}
    )
    note = ""
    if len(pool) < config.WORDS_PER_TEST:
        note = f"У цьому діапазоні лише {len(pool)} слів — тестуємо всі.\n\n"
    await message.answer(f"{note}Починаємо! Слів у тесті: {len(words)}.")
    await send_word(message, state)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "Привіт! Це бот для тренування наголосів до НМТ з української мови.\n\n"
        f"У базі {len(ALL_WORDS)} слів (офіційний перелік ЗНО/НМТ).\n"
        "Натисни «Практика», щоб почати тестування.",
        reply_markup=MAIN_MENU,
    )


@router.message(Command("practice"))
@router.message(F.text == "🧠 Практика")
async def cmd_practice(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        f"У базі {len(ALL_WORDS)} слів. Що тестуємо?",
        reply_markup=SCOPE_KEYBOARD,
    )


@router.callback_query(F.data == "scope:all")
async def scope_all(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.edit_reply_markup(reply_markup=None)
    await start_test(callback.message, state, ALL_WORDS)
    await callback.answer()


@router.callback_query(F.data == "scope:letters")
async def scope_letters(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.edit_reply_markup(reply_markup=None)
    await state.set_state(Practice.choosing_letters)
    await callback.message.answer(
        "Введи літери чи діапазон, наприклад:\n"
        "«А-В» — усі слова від А до В\n"
        "«Б» — лише на Б\n"
        "«А, В, Д» — кілька літер через кому"
    )
    await callback.answer()


@router.message(Practice.choosing_letters)
async def choose_letters(message: Message, state: FSMContext) -> None:
    letters = parse_letters(message.text or "")
    if letters is not None and not letters:
        await message.answer(
            "Не вдалося розпізнати літери. Спробуй ще раз, наприклад «А-В»."
        )
        return
    pool = filter_by_letters(letters)
    if not pool:
        await message.answer("На ці літери слів у базі немає. Спробуй інший діапазон.")
        return
    await start_test(message, state, pool)


@router.message(Practice.testing, F.text == STOP_BUTTON_TEXT)
async def stop_test(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    session = data.get("session", {})
    correct = session.get("correct", 0)
    index = session.get("index", 0)
    await state.clear()
    await message.answer(
        f"Тест перервано. Встигли пройти {index} слів, правильно — {correct}.",
        reply_markup=MAIN_MENU,
    )


@router.message(Practice.testing)
async def check_answer(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    session = data["session"]
    entry = session["words"][session["index"]]
    answer = (message.text or "").strip()

    if is_correct(entry, answer):
        session["correct"] += 1
        feedback = "✅ Правильно!"
    else:
        options = " / ".join(correct_variants(entry))
        feedback = f"❌ Неправильно. Правильно: {options}"

    session["index"] += 1
    await state.update_data(session=session)
    await message.answer(feedback)

    if session["index"] >= session["total"]:
        correct = session["correct"]
        total = session["total"]
        pct = round(correct / total * 100) if total else 0
        await state.clear()
        await message.answer(
            f"🏁 Тест завершено!\nПравильних відповідей: {correct} із {total} ({pct}%).",
            reply_markup=MAIN_MENU,
        )
    else:
        await send_word(message, state)


@router.message(Command("cancel"))
async def cancel(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Скасовано.", reply_markup=MAIN_MENU)


async def main() -> None:
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
