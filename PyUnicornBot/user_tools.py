import json
import os
from time import time
from aiogram.types import User
from aiogram import BaseMiddleware

FILE_PATH: str = 'PyUnicornBot/data_users.json'
UPDATE_INTERVAL: int = 24 * 60 * 60 # 1 day


class UserUpdateMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        print('/')
        user = None

        if event.message:
            user = event.message.from_user
        elif event.callback_query:
            user = event.callback_query.from_user

        if user:
            update_user(user)

        return await handler(event, data)


def load_data() -> dict:
    if not os.path.exists(FILE_PATH):
        return {}
    with open(FILE_PATH, encoding='utf-8') as f:
        return json.load(f)


def save_data(data: dict) -> None:
    with open(FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def update_user(user: User) -> None:
    data = load_data()
    user_id = str(user.id)
    now = int(time())

    if user_id not in data:
        data[user_id] = {
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'full_name': user.full_name,
            'last_update': now
        }
        save_data(data)
        return

    last_update = data[user_id].get('last_update', 0)

    if (
        now - last_update > UPDATE_INTERVAL
        or data[user_id].get('username') != user.username
        or data[user_id].get('first_name') != user.first_name
        or data[user_id].get('last_name') != user.last_name
        or data[user_id].get('full_name') != user.full_name
    ):
        data[user_id].update({
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'full_name': user.full_name,
            'last_update': now
        })
        save_data(data)


def get_user_tag(user_id: int) -> str:
    str_user_id = str(user_id)
    data = load_data()

    if str_user_id not in data:
        return f'<a href="tg://user?id={user_id}">unknown user</a>'

    if username := data[str_user_id].get('username'):
        return f'@{username}'

    return f'<a href="tg://user?id={user_id}">{data[str_user_id].get('full_name', 'unknown user')}</a>'


def get_user_link(user_id: int) -> str:
    str_user_id = str(user_id)
    data = load_data()

    if str_user_id not in data:
        return f'<a href="tg://user?id={user_id}">unknown user</a>'

    return f'<a href="tg://user?id={user_id}">{data[str_user_id].get('full_name', 'unknown user')}</a>'


def get_username(user_id: int) -> str:
    str_user_id = str(user_id)
    data = load_data()
    if str_user_id not in data:
        return get_user_full_name(user_id)
    else:
        return data[str_user_id].get('username', get_user_full_name(user_id))


def get_user_full_name(user_id: int) -> str:
    str_user_id = str(user_id)
    data = load_data()

    if str_user_id not in data:
        return f'unknown user (id: {user_id})'

    return data[str_user_id].get('full_name', f'unknown user (id: {user_id})')
