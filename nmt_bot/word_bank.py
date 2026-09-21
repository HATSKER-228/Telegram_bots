"""
Робота зі словником наголосів: завантаження words.json,
фільтрація за літерами та генерація варіантів наголосу для клавіатури.
"""
import json
import random
import re
from pathlib import Path

VOWELS = set("аеиіоуюяїє")

# Сучасний український алфавіт (33 літери) - потрібен для діапазонів "А-В"
UKR_ALPHABET = "абвгґдежзиіїйклмнопрстуфхцчшщьюя"

DATA_PATH = Path(__file__).parent / "words.json"

with DATA_PATH.open(encoding="utf-8") as f:
    ALL_WORDS: list[dict] = json.load(f)


def vowel_indices(word: str) -> list[int]:
    return [i for i, ch in enumerate(word) if ch in VOWELS]


def apply_stress(word: str, positions) -> str:
    """Повертає слово з великими літерами на вказаних позиціях (одна чи кілька)."""
    chars = list(word)
    for i in positions:
        chars[i] = chars[i].upper()
    return "".join(chars)


def make_variants(entry: dict) -> list[str]:
    """Кнопки для клавіатури: по одному варіанту з наголосом на кожному
    голосному (зліва направо) плюс, якщо в слові подвійна норма наголосу
    (кілька прийнятних позицій), ще один об'єднаний варіант з усіма
    наголошеними складами одночасно — саме так, як це подано в офіційному
    переліку (наприклад "алфАвІт", "веснЯнИй", "мАбУть")."""
    word = entry["word"]
    variants = [apply_stress(word, [i]) for i in vowel_indices(word)]
    if len(entry["stress"]) > 1:
        variants.append(apply_stress(word, entry["stress"]))
    return variants


def correct_variants(entry: dict) -> list[str]:
    """Правильний варіант для слова. Для слів зі звичайним наголосом -
    одна позначена голосна. Для слів із подвійною нормою наголосу -
    лише об'єднаний варіант з усіма наголошеними складами одночасно
    (наприклад "алфАвІт"), окремі склади нарізно НЕ зараховуються."""
    return [apply_stress(entry["word"], entry["stress"])]


def variant_stress_positions(word: str, variant: str) -> set:
    """Позиції літер, які користувач позначив як наголошені (може бути
    кілька, якщо натиснута об'єднана кнопка на кшталт 'алфАвІт')."""
    if len(word) != len(variant):
        return set()
    return {i for i, (a, b) in enumerate(zip(word, variant)) if a != b}


def is_correct(entry: dict, variant: str) -> bool:
    positions = variant_stress_positions(entry["word"], variant)
    stress = set(entry["stress"])
    # правильна відповідь - лише та, що позначає РІВНО ті склади, що
    # зазначені в normі: один склад для звичайних слів, усі одразу -
    # для слів із подвійною нормою наголосу.
    return positions == stress


def parse_letters(text: str):
    """Парсить рядок від користувача ('А-В', 'б, д', 'абд', 'всі')
    у множину малих літер. Повертає None, якщо йдеться про всі слова,
    і порожню множину, якщо нічого розпізнати не вдалося."""
    text = text.strip().lower()
    if text in ("всі", "усі", "all", "все", "будь-які"):
        return None

    letters: set[str] = set()
    parts = re.split(r"[,;\s]+", text)
    for part in parts:
        if not part:
            continue
        m = re.match(r"^([а-щьюяєіїй])\s*[-–—]\s*([а-щьюяєіїй])$", part)
        if m:
            a, b = m.group(1), m.group(2)
            ia, ib = UKR_ALPHABET.index(a), UKR_ALPHABET.index(b)
            if ia > ib:
                ia, ib = ib, ia
            letters.update(UKR_ALPHABET[ia : ib + 1])
        else:
            for ch in part:
                if ch in UKR_ALPHABET:
                    letters.add(ch)
    return letters


def filter_by_letters(letters):
    if letters is None:
        return list(ALL_WORDS)
    return [w for w in ALL_WORDS if w["word"][0] in letters]


def sample_words(pool: list[dict], count: int) -> list[dict]:
    count = min(count, len(pool))
    return random.sample(pool, count)
