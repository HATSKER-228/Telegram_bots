from aiogram import BaseMiddleware
from aiogram.types import Message
from aiogram.filters import BaseFilter
from user_tools import update_user


class UserUpdateMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user = None

        if event.message:
            user = event.message.from_user
        elif event.callback_query:
            user = event.callback_query.from_user

        if user:
            update_user(user)

        return await handler(event, data)


class GroupOnlyFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if message.chat.type == 'private':
            await message.answer('Цю команду можна використати тільки в групі 🧌')
            return False
        return True


class ReplyOnlyFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if not message.reply_to_message:
            await message.answer('Шановний представник виду <i>Homo Sapiens</i>, команду необхідно писати у '
                        'ВІДПОВІДЬ на повідомлення 🧌', parse_mode='HTML')
            return False
        return True
