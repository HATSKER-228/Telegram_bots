import json
from time import time
from random import shuffle

from src.func_results import BjHitResult, BjStandResult
from src.tools import user as us
from src.config import DATA_DIR

FILE_PATH = DATA_DIR / 'blackjack.json'


def load_data() -> dict:
    if not FILE_PATH.exists():
        return {}
    with open(FILE_PATH, encoding='utf-8') as f:
        return json.load(f)


def save_data(data: dict) -> None:
    with open(FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def touch_game(data: dict, str_chat_id: str) -> None:
    data[str_chat_id]['updated_at'] = int(time())


def build_deck() -> list[str]:
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    suits = ['♣️', '♦️', '♥️', '♠️']
    deck = [r+s for r in ranks for s in suits]
    shuffle(deck)
    return deck


def calculate_hand(hand: list[str]) -> int:
    s = 0
    aces = 0
    for rank in map(lambda x: x[:-2], hand):
        if rank.isdigit():
            s += int(rank)
        elif rank == 'A':
            s += 11
            aces += 1
        else:
            s += 10
    while aces > 0 and s > 21:
        aces -= 1
        s -= 10
    return s


def get_lobby_text(chat_id: int) -> str:
    game: dict = load_data()[str(chat_id)]
    creator_link = us.get_user_link(game['creator_id'])
    players_links = [us.get_user_link(int(uid)) for uid in game['players']]

    text = f'🃏 {creator_link} хоче зіграти в Блекджек!\n\n'
    text += 'Гравці:\n' + '\n'.join(f'• {link}' for link in players_links)
    return text


def get_round_text(chat_id: int) -> str:
    active_players: list = load_data()[str(chat_id)]['pending_this_round']
    players_links = [us.get_user_link(int(uid)) for uid in active_players]

    text = f'🎲 Наступний раунд! Оберіть дію.\n\n'
    text += 'Ще не походили:\n' + '\n'.join(f'• {link}' for link in players_links)
    return text


def get_show_hand_text(chat_id: int, user_id: int) -> str:
    data = load_data()
    str_chat_id = str(chat_id)
    str_user_id = str(user_id)

    if str_chat_id not in data:
        return 'В цьому чаті ще немає гри.'

    if str_user_id not in data[str_chat_id]['players']:
        return 'Тебе немає в поточній грі'

    hand: list[str] = data[str_chat_id]['players'][str_user_id]['hand']

    text = 'Твої карти: ' + ', '.join(hand)
    text += f'\nСума: {calculate_hand(hand)}'

    if data[str_chat_id]['players'][str_user_id]['status'] == 'bust':
        text += '\nТи перебрав 💥'
    elif data[str_chat_id]['players'][str_user_id]['status'] == 'stand':
        text += '\nТи завершив брати карти 🏁'

    return text


def create_game(chat_id: int, creator_id: int) -> bool:
    data = load_data()
    str_chat_id = str(chat_id)

    if str_chat_id in data:
        return False

    data[str_chat_id] = {
        'status': 'waiting',
        'creator_id': creator_id,
        'players': {
            str(creator_id): {'hand': [], 'status': 'playing'},
        },
        'dealer': {'hand': [], 'status': 'playing'},
        'deck': [],
        'updated_at': int(time())
    }

    save_data(data)
    return True


def join_game(chat_id: int, user_id: int) -> tuple[bool, str]:
    data = load_data()
    str_chat_id = str(chat_id)
    str_user_id = str(user_id)

    if str_chat_id not in data:
        return False, 'Гру ще не створено.'

    if data[str_chat_id]['status'] != 'waiting':
        return False, 'Гра вже почалась або завершена. Приєднатися не можна.'

    if str_user_id in data[str_chat_id]['players']:
        return False, 'Ти вже у грі.'

    if len(data[str_chat_id]['players']) >= 15:
        return False, 'Стіл заповнений — максимум 15 гравців 🧌'

    data[str_chat_id]['players'][str_user_id] = {'hand': [], 'status': 'playing'}

    touch_game(data, str_chat_id)
    save_data(data)
    return True, ''


def start_game(chat_id: int, user_id: int) -> tuple[bool, str]:
    data = load_data()
    str_chat_id = str(chat_id)

    if str_chat_id not in data:
        return False, 'Гру ще не створено'

    if data[str_chat_id]['status'] != 'waiting':
        return False, 'Гра вже почалась!'

    if user_id != data[str_chat_id]['creator_id']:
        return False, 'Лише організатор може розпочати гру.'

    deck = build_deck()
    for player_id, player_data in data[str_chat_id]['players'].items():
        player_data['hand'].append(deck.pop())
        player_data['hand'].append(deck.pop())

    data[str_chat_id]['dealer']['hand'].append(deck.pop())
    data[str_chat_id]['dealer']['hand'].append(deck.pop())

    data[str_chat_id]['deck'] = deck
    data[str_chat_id]['pending_this_round'] = list(data[str_chat_id]['players'].keys())
    data[str_chat_id]['status'] = 'round_in_progress'

    touch_game(data, str_chat_id)
    save_data(data)
    return True, ''


def hit(chat_id: int, player_id: int) -> BjHitResult:
    data = load_data()
    str_chat_id = str(chat_id)
    str_player_id = str(player_id)

    if str_chat_id not in data:
        return BjHitResult(message='В цьому чаті нема гри')

    if str_player_id not in data[str_chat_id]['players']:
        return BjHitResult(message='Зараз ти не граєш 🧌')

    if data[str_chat_id]['players'][str_player_id]['status'] == 'stand':
        return BjHitResult(message='Ти вже завершив(-ла) брати карти 🏁')

    if data[str_chat_id]['players'][str_player_id]['status'] == 'bust':
        return BjHitResult(message='Ти вже перебрав(-ла) 💥')

    if str_player_id not in data[str_chat_id]['pending_this_round']:
        return BjHitResult(message='Ти вже зробив(-ла) хід')

    card = data[str_chat_id]['deck'].pop()
    data[str_chat_id]['players'][str_player_id]['hand'].append(card)
    data[str_chat_id]['pending_this_round'].remove(str_player_id)
    summ = calculate_hand(data[str_chat_id]['players'][str_player_id]['hand'])

    if summ > 21:
        data[str_chat_id]['players'][str_player_id]['status'] = 'bust'

    touch_game(data, str_chat_id)
    save_data(data)

    message = get_show_hand_text(chat_id, player_id)
    return BjHitResult(message=message, success=True)


def stand(chat_id: int, player_id: int) -> BjStandResult:
    data = load_data()
    str_chat_id = str(chat_id)
    str_player_id = str(player_id)

    if str_chat_id not in data:
        return BjStandResult(message='В цьому чаті нема гри')

    if str_player_id not in data[str_chat_id]['players']:
        return BjStandResult(message='Зараз ти не граєш 🧌')

    if data[str_chat_id]['players'][str_player_id]['status'] == 'stand':
        return BjStandResult(message='Ти вже завершив(-ла) брати карти 🏁')

    if data[str_chat_id]['players'][str_player_id]['status'] == 'bust':
        return BjStandResult(message='Ти вже перебрав(-ла) 💥')

    if str_player_id not in data[str_chat_id]['pending_this_round']:
        return BjStandResult(message='Ти вже зробив(-ла) хід')

    data[str_chat_id]['pending_this_round'].remove(str_player_id)
    data[str_chat_id]['players'][str_player_id]['status'] = 'stand'

    touch_game(data, str_chat_id)
    save_data(data)

    message = get_show_hand_text(chat_id, player_id)
    return BjStandResult(message=message, success=True)
