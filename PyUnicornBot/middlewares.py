from aiogram import BaseMiddleware
from aiogram.types import Message
from user_tools import update_user

GROUP_ONLY_CMD: set = {'baby_reg', 'baby_unreg', 'baby_select', 'baby_stats', 'create', 'cancel'}
REPLY_ONLY_CMD: set = {'fix', 'shypko'}

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


class GroupOnlyCmdMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data):
        if not isinstance(event, Message):
            return await handler(event, data)

        if event.chat.type == 'private':
            command = data.get('command')

            if command and command.command in GROUP_ONLY_CMD:
                await event.answer('Цю команду можна використати тільки в групі 🧌')
                return None

        return await handler(event, data)


class ReplyOnlyCmdMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data):
        if not isinstance(event, Message):
            return await handler(event, data)

        if not event.reply_to_message:
            command = data.get('command')

            if command and command.command in REPLY_ONLY_CMD:
                await event.answer('Шановний тупорилий представник виду <i>Homo Sapiens</i>, команду необхідно писати у '
                            'ВІДПОВІДЬ на повідомлення 🧌', parse_mode='HTML')
                return None

        return await handler(event, data)
