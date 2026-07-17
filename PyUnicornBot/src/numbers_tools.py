import json
import os
from random import sample
from time import time

FILE_PATH = 'PyUnicornBot/data/data_numbers.json'
STALE_TIMEOUT = 24 * 60 * 60  # доба

def load_data() -> dict:
    if not os.path.exists(FILE_PATH):
        return {}
    with open(FILE_PATH, encoding='utf-8') as f:
        return json.load(f)


def save_data(data: dict) -> None:
    with open(FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def touch_game(data: dict, str_chat_id: str) -> None:
    data[str_chat_id]['updated_at'] = int(time())


def create_game(chat_id: int, user_id: int) -> bool:
    str_chat_id = str(chat_id)
    str_user_id = str(user_id)
    data = load_data()

    if str_chat_id in data:
        return False

    data[str_chat_id] = {
        'players': {
            str_user_id: {
                'number': None,
                'guesses': [],
                'finished': False,
            }
        },
        'turn': None,
        'status': 'waiting',
        'updated_at': int(time()),
    }
    save_data(data)
    return True


def join_to_game(chat_id: int, user_id: int, creator_id: int) -> tuple[bool, str]:
    str_chat_id = str(chat_id)
    str_user_id = str(user_id)
    data = load_data()

    if user_id == creator_id:
        return False, 'Ти вже створив(-ла) гру.'

    if str_chat_id not in data or data[str_chat_id]['status'] != 'waiting':
        return False, 'Гра вже почалась або була скасована.'

    data[str_chat_id]['players'][str_user_id] = {
        'number': None,
        'guesses': [],
        'finished': False,
    }
    data[str_chat_id]['turn'] = creator_id
    data[str_chat_id]['status'] = 'setting numbers'
    touch_game(data, str_chat_id)
    save_data(data)

    return True, ''


def is_awaiting_number(user_id: int) -> bool:
    str_user_id = str(user_id)
    data = load_data()

    for game in data.values():
        if game['status'] != 'setting numbers':
            continue
        if str_user_id not in game['players']:
            continue
        if game['players'][str_user_id]['number'] is None:
            return True

    return False


def set_player_number(user_id: int, str_number: str) -> tuple[bool, str, int | None, int | None]:
    str_user_id = str(user_id)
    data = load_data()

    for str_chat_id, game in data.items():
        if game['status'] != 'setting numbers':
            continue
        if str_user_id not in game['players']:
            continue
        if game['players'][str_user_id]['number'] is not None:
            return False, '❗ У тебе вже є число.', None, None

        if not str_number.isdigit() or len(str_number) != 4:
            return False, '❌ Число повинно містити рівно 4 цифри.', None, None
        if str_number[0] == '0':
            return False, '❌ Число не повинно починатися з 0.', None, None
        if len(set(str_number)) != 4:
            return False, '❌ Усі цифри мають бути різними.', None, None

        data[str_chat_id]['players'][str_user_id]['number'] = str_number
        touch_game(data, str_chat_id)
        save_data(data)

        all_ready = all(p['number'] is not None for p in game['players'].values())
        if all_ready:
            first_player_id = game['turn']
            data[str_chat_id]['status'] = 'ongoing'
            touch_game(data, str_chat_id)
            save_data(data)
            return True, '✅ Число прийнято! Усі гравці готові.', int(str_chat_id), first_player_id
        else:
            return True, '✅ Число прийнято! Очікуємо опонента.', None, None

    return False, '⚠️ Немає гри, де очікується число.', None, None


def cancel_game(chat_id: int) -> str:
    str_chat_id = str(chat_id)
    data = load_data()

    if str_chat_id in data:
        del data[str_chat_id]
        save_data(data)
        return '❌ Гру скасовано'

    return '⚠️ В цьому чаті не знайдено гри.'


def delete_game(chat_id: int) -> None:
    data = load_data()
    del data[str(chat_id)]
    save_data(data)


def get_random_num() -> str:
    while True:
        number = sample('0123456789', 4)
        if number[0] != '0':
            return ''.join(number)


def get_number(chat_id: int, user_id: int, data: dict | None = None) -> str | None:
    str_chat_id = str(chat_id)
    str_user_id = str(user_id)
    if data is None:
        data = load_data()

    if str_chat_id not in data or str_user_id not in data[str_chat_id]['players']:
        return None

    return data[str_chat_id]['players'][str_user_id]['number']


def get_clue(guess: str, target: str) -> str:
    o = 0
    x = 0
    for i in range(4):
        if guess[i] == target[i]:
            x += 1
        elif guess[i] in target:
            o += 1
    result = 'X' * x + 'O' * o
    return result if len(result) > 0 else '-'


def get_opponent_id(chat_id: int, user_id: int, data: dict | None = None) -> int:
    str_user_id = str(user_id)
    if data is None:
        data = load_data()
    for str_id in data[str(chat_id)]['players']:
        if str_id != str_user_id:
            return int(str_id)
    raise ValueError(f'[numbers_tools.get_opponent_id] Opponent not found in chat {chat_id} for user {user_id}')


def get_guesses(chat_id: int, user_id: int, data: dict | None = None) -> str:
    if data is None:
        data = load_data()
    guesses = ''
    for number, clue in data[str(chat_id)]['players'][str(user_id)]['guesses']:
        guesses += f'{number} {clue}\n'
    return guesses


def get_user_finished(chat_id: int, user_id: int, data: dict | None = None) -> bool:
    if data is None:
        data = load_data()
    return data[str(chat_id)]['players'][str(user_id)]['finished']


def guess_number(chat_id: int, user_id: int, str_number: str) -> tuple[bool, str]:
    str_chat_id = str(chat_id)
    str_user_id = str(user_id)
    data = load_data()

    if str_chat_id not in data:
        return False, '⚠️ В цьому чаті не знайдено гри.'
    if data[str_chat_id]['status'] == 'setting numbers':
        return False, '⚠️ Не всі гравці обрали числа!'
    if data[str_chat_id]['status'] != 'ongoing':
        return False, '⚠️ В цьому чаті гра ще не розпочата.'
    if str_user_id not in data[str_chat_id]['players']:
        return False, '❌ Ти не береш участі в поточній грі.'

    str_opponent_id = str(get_opponent_id(chat_id, user_id, data))

    if not str_opponent_id:
        return False, '️⚠️ Опонент ще не приєднався.'
    if data[str_chat_id]['turn'] != user_id:
        return False, '❌ Зараз не твоя черга.'
    if str_number == 'Яке треба число?':
        return False, '• рівно 4 цифри\n• не починається з 0\n• всі цифри різні'

    target: str = data[str_chat_id]['players'][str_opponent_id]['number']
    clue = get_clue(str_number, target)
    data[str_chat_id]['players'][str_user_id]['guesses'].append((str_number, clue))
    if str_number == target:
        data[str_chat_id]['players'][str_user_id]['finished'] = True
    data[str_chat_id]['turn'] = int(str_opponent_id)
    touch_game(data, str_chat_id)
    save_data(data)

    return True, clue


def cleanup_stale_games() -> list[str]:
    data = load_data()
    now = int(time())
    stale_chat_ids = []

    for str_chat_id, game in data.items():
        updated_at = game.get('updated_at', 0)
        if now - updated_at > STALE_TIMEOUT:
            stale_chat_ids.append(str_chat_id)

    for str_chat_id in stale_chat_ids:
        del data[str_chat_id]

    if stale_chat_ids:
        save_data(data)

    return stale_chat_ids
