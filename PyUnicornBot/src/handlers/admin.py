import shutil
from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command

from src.tools import baby
from src.tools import numbers as num
from src.tools import user as us
from src.config import ADMIN_ID

router = Router()


@router.message(Command('get_jsons'), F.chat.type == 'private', F.from_user.id == ADMIN_ID)
async def cmd_get_jsons(message: Message) -> None:
    babies = FSInputFile(baby.FILE_PATH)
    numbers = FSInputFile(num.FILE_PATH)
    users = FSInputFile(us.FILE_PATH)
    await message.answer_document(babies)
    await message.answer_document(numbers)
    await message.answer_document(users)


@router.message(Command('upload_baby_stats'), F.chat.type == 'private', F.from_user.id == ADMIN_ID)
async def cmd_upload_baby_stats(message: Message) -> None:
    if not message.document:
        await message.answer('Будь ласка, надішли файл як документ.')
        return

    if not message.document.file_name.endswith('.json'):
        await message.answer('Це має бути JSON-файл.')
        return

    file = await message.bot.get_file(message.document.file_id)
    await message.bot.download_file(file.file_path, 'temp_uploaded.json')

    shutil.move('temp_uploaded.json', baby.FILE_PATH)

    await message.answer('Файл зі статистикою успішно оновлено.')


@router.message(Command('upload_users_data'), F.chat.type == 'private', F.from_user.id == ADMIN_ID)
async def cmd_upload_users_data(message: Message) -> None:
    if not message.document:
        await message.answer('Будь ласка, надішли файл як документ.')
        return

    if not message.document.file_name.endswith('.json'):
        await message.answer('Це має бути JSON-файл.')
        return

    file = await message.bot.get_file(message.document.file_id)
    await message.bot.download_file(file.file_path, 'temp_uploaded.json')

    shutil.move('temp_uploaded.json', us.FILE_PATH)

    await message.answer('Файл успішно оновлено.')
