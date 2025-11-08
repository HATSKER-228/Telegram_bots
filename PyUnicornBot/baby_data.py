import json
import os
from random import choice
from datetime import date
FILE_PATH: str = 'PyUnicornBot/data_baby.json'


def get_path() -> str:
    return FILE_PATH


def get_today() -> str:
    return date.today().isoformat()


def load_data() -> dict:
    if not os.path.exists(FILE_PATH):
        return {}
    with open(FILE_PATH, encoding='utf-8') as f:
        return json.load(f)


def save_data(data: dict) -> None:
    with open(FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def register_user(chat_id: int, user_id: int, username: str | None) -> bool:
    data: dict = load_data()
    str_chat_id = str(chat_id)
    str_user_id = str(user_id)

    if str_chat_id not in data:
        data[str_chat_id] = {'players': {}, 'last_play': None, 'last_winner': None}

    if str_user_id not in data[str_chat_id]['players']:
        data[str_chat_id]['players'][str_user_id] = {
            'username': username,
            'count': 0
        }
        save_data(data)
        return True
    else:
        return False


def is_in_list(chat_id: int, user_id: int) -> bool:
    data: dict = load_data()
    str_chat_id = str(chat_id)
    str_user_id = str(user_id)

    if str_chat_id not in data:
        data[str_chat_id] = {'players': {}, 'last_play': None, 'last_winner': None}
        save_data(data)

    if str_user_id in data[str_chat_id]['players']:
        return True
    else:
        return False


def unregister_user(chat_id: int, user_id: int) -> bool:
    data: dict = load_data()
    str_chat_id = str(chat_id)
    str_user_id = str(user_id)

    if str_chat_id not in data:
        data[str_chat_id] = {'players': {}, 'last_play': None, 'last_winner': None}
        save_data(data)

    if str_user_id in data[str_chat_id]['players']:
        del data[str_chat_id]['players'][str_user_id]
        save_data(data)
        return True
    else:
        return False


def get_stats(chat_id: int) -> list | None:
    data: dict = load_data()
    str_chat_id = str(chat_id)

    if str_chat_id not in data or len(data[str_chat_id]['players']) == 0:
        return None

    stats = list()
    for str_user_id in data[str_chat_id]['players'].keys():
        user_info: dict = data[str_chat_id]['players'][str_user_id]
        stats.append((int(str_user_id), user_info['username'], user_info['count']))
    return sorted(stats, key=lambda x: x[2], reverse=True)


def select_baby(chat_id: int) -> tuple[bool, int | None]:
    data: dict = load_data()
    str_chat_id = str(chat_id)

    if str_chat_id not in data or not data[str_chat_id]['players']:
        return False, None

    today: str = get_today()
    if data[str_chat_id]['last_play'] == today:
        last_id = data[str_chat_id]['last_winner']
        return False, last_id

    players: dict = data[str_chat_id]['players']
    winner_id: str = choice(list(players.keys()))
    players[winner_id]['count'] += 1

    data[str_chat_id]['last_play'] = today
    data[str_chat_id]['last_winner'] = int(winner_id)

    save_data(data)
    return True, int(winner_id)
