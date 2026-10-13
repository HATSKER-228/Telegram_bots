import json

from src.config import DATA_DIR

FILE_PATH = DATA_DIR / 'blackjack_stats.json'


def load_data() -> dict:
    if not FILE_PATH.exists():
        return {}
    with open(FILE_PATH, encoding='utf-8') as f:
        return json.load(f)


def save_data(data: dict) -> None:
    with open(FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def update_stats(outcomes: dict[str, str]) -> None:
    data = load_data()

    for str_user_id, outcome in outcomes.items():
        stats = data.setdefault(str_user_id, {'games': 0, 'wins': 0, 'draws': 0, 'losses': 0})
        stats['games'] += 1
        stats[{'win': 'wins', 'draw': 'draws', 'lose': 'losses'}[outcome]] += 1

    save_data(data)


def get_stats(user_id: int) -> dict:
    stats = load_data().get(str(user_id), {})
    return {key: stats.get(key, 0) for key in ('games', 'wins', 'draws', 'losses')}