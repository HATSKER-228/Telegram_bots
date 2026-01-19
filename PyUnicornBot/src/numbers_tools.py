import json
import os
from random import sample

FILE_PATH = 'PyUnicornBot/data/data_numbers.json'

def load_data() -> dict:
    if not os.path.exists(FILE_PATH):
        return {}
    with open(FILE_PATH, encoding='utf-8') as f:
        return json.load(f)


def save_data(data: dict) -> None:
    with open(FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


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
        'status': 'waiting'
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
    save_data(data)

    return True, ''


def set_player_number(user_id: int, number_str: str) -> tuple[bool, str, int | None, int | None]:
    str_user_id = str(user_id)
    data = load_data()

    for str_chat_id, game in data.items():
        if game['status'] != 'setting numbers':
            continue
        if str_user_id not in game['players']:
            continue
        if game['players'][str_user_id]['number'] is not None:
            return False, '❗ У тебе вже є число.', None, None

        if not number_str.isdigit() or len(number_str) != 4:
            return False, '❌ Число повинно містити рівно 4 цифри.', None, None
        if number_str[0] == '0':
            return False, '❌ Число не повинно починатися з 0.', None, None
        if len(set(number_str)) != 4:
            return False, '❌ Усі цифри мають бути різними.', None, None

        data[str_chat_id]['players'][str_user_id]['number'] = int(number_str)
        save_data(data)

        all_ready = all(p['number'] is not None for p in game['players'].values())
        if all_ready:
            first_player_id = game['turn']
            data = load_data()
            data[str_chat_id]['status'] = 'ongoing'
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


def get_number(chat_id: int, user_id: int) -> int | None:
    str_chat_id = str(chat_id)
    str_user_id = str(user_id)
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


def get_opponent_id(chat_id: int, user_id: int) -> str | None:
    str_opponent_id = None
    str_user_id = str(user_id)
    str_chat_id = str(chat_id)

    data = load_data()
    for str_id in data[str_chat_id]['players']:
        if str_id != str_user_id:
            str_opponent_id = str_id
    return str_opponent_id


def get_guesses(chat_id: int, user_id: int) -> str:
    str_user_id = str(user_id)
    str_chat_id = str(chat_id)

    data = load_data()
    guesses = ''
    for number, clue in data[str_chat_id]['players'][str_user_id]['guesses']:
        guesses += f'{number} {clue}\n'
    return guesses


def get_user_finished(chat_id: int, user_id: int) -> bool:
    data = load_data()
    return data[str(chat_id)]['players'][str(user_id)]['finished']


def guess_number(chat_id: int, user_id: int, number: str) -> tuple[bool, str]:
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

    str_opponent_id = get_opponent_id(chat_id, user_id)

    if not str_opponent_id:
        return False, '️⚠️ Опонент ще не приєднався.'
    if data[str_chat_id]['turn'] != user_id:
        return False, '❌ Зараз не твоя черга.'
    if number[0] == '0':
        return False, '❌ Число не повинно починатися з 0.'
    if len(set(number)) != 4:
        return False, '❌ Усі цифри мають бути різними.'

    target = data[str_chat_id]['players'][str_opponent_id]['number']
    clue = get_clue(number, str(target))
    data[str_chat_id]['players'][str_user_id]['guesses'].append((number, clue))
    if int(number) == target:
        data[str_chat_id]['players'][str_user_id]['finished'] = True
    data[str_chat_id]['turn'] = int(str_opponent_id)
    save_data(data)

    return True, clue
