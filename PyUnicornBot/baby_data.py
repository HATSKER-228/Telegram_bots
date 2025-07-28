import json
import os
from random import choice
from datetime import date

FILE_PATH = 'PyUnicornBot/data_baby.json'


def get_path():
    return FILE_PATH


def get_today() -> str:
    return date.today().isoformat()


def load_data() -> dict:
    if not os.path.exists(FILE_PATH):
        return {}
    with open(FILE_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_data(data: dict) -> None:
    with open(FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def register_user(chat_id: int, user_id: int, username: str) -> bool:
    data = load_data()
    str_chat_id = str(chat_id)
    str_user_id = str(user_id)

    if str_chat_id not in data:
        data[str_chat_id] = {'players': {}, 'last_play': None, 'last_winner': None}

    if str_user_id not in data[str_chat_id]['players']:
        data[str_chat_id]['players'][str_user_id] = {
            'username': username or f'user_{user_id}',
            'count': 0
        }
        save_data(data)
        return True  # був доданий новий користувач
    else:
        return False  # вже був у списку


def unregister_user(chat_id: int, user_id: int, username: str) -> bool:
    data = load_data()
    str_chat_id = str(chat_id)
    str_user_id = str(user_id)

    if str_chat_id not in data:
        data[str_chat_id] = {'players': {}, 'last_play': None, 'last_winner': None}
        save_data(data)

    if str_user_id in data[str_chat_id]['players']:
        del data[str_chat_id]['players'][str_user_id]
        save_data(data)
        return True  # був видалений зі списку
    else:
        return False  # нема у списку


def get_stats(chat_id: int) -> list | None:
    data = load_data()
    str_chat_id = str(chat_id)

    if str_chat_id not in data or len(data[str_chat_id]['players']) == 0:
        return None

    stats = list()
    for str_user_id in data[str_chat_id]['players'].keys():
        user_info = data[str_chat_id]['players'][str_user_id]
        stats.append((user_info['username'], user_info['count']))
    return sorted(stats, key=lambda x: x[1], reverse=True)


def select_baby(chat_id: int):
    data = load_data()
    str_chat_id = str(chat_id)

    if str_chat_id not in data or not data[str_chat_id]['players']:
        return None, 'У цьому чаті ще немає зареєстрованих пупсіків!'

    today = get_today()
    if data[str_chat_id]['last_play'] == today:
        last_id = data[str_chat_id]['last_winner']
        last_username = data[str_chat_id]['players'].get(str(last_id), {}).get('username', 'невідомий пупсік')
        return None, f'Сьогоднішній пупсік уже обраний: @{last_username} 💖'

    # вибираємо випадкового пупсіка
    players = data[str_chat_id]['players']
    winner_id = choice(list(players.keys()))
    players[winner_id]['count'] += 1

    data[str_chat_id]['last_play'] = today
    data[str_chat_id]['last_winner'] = int(winner_id)

    save_data(data)
    return players[winner_id]['username'], None
