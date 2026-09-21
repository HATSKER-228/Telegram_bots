"""
Перетворює RAW (raw_list.py) на words.json:
кожне слово -> {"word": "<слово малими літерами>",
                 "stress": [індекси наголошених літер],
                 "note": "<примітка або null>"}
"stress" - список індексів (0-based, у символах слова), бо в частини слів
допустимі два варіанти наголосу (подвійна норма), напр. "мАбУть".
"""
import json
import re
from raw_list import RAW

UPPER_RE = re.compile(r"[А-ЯЇЄІ]")

VOWELS = set("аеиіоуюяїє")


def parse(word_marked: str):
    positions = [i for i, ch in enumerate(word_marked) if UPPER_RE.match(ch)]
    word = word_marked.lower()
    # sanity: кожна позначена позиція має бути голосною
    for p in positions:
        assert word[p] in VOWELS, f"{word_marked}: позиція {p} ('{word[p]}') не голосна"
    return word, positions


def vowel_indices(word: str):
    return [i for i, ch in enumerate(word) if ch in VOWELS]


entries = []
seen = {}
for marked, note in RAW:
    word, stress = parse(marked)
    vi = vowel_indices(word)
    for p in stress:
        assert p in vi, f"{marked}: наголос не на голосній за списком vowel_indices"
    # якщо слово-омограф (той самий запис, різні наголоси/значення) - не зливаємо
    key = (word, note)
    entries.append({"word": word, "stress": stress, "note": note})

with open("words.json", "w", encoding="utf-8") as f:
    json.dump(entries, f, ensure_ascii=False, indent=2)

print(f"Всього слів: {len(entries)}")
letters = {}
for e in entries:
    l = e["word"][0]
    letters[l] = letters.get(l, 0) + 1
print("Розподіл за першою літерою:")
for l in sorted(letters):
    print(f"  {l}: {letters[l]}")
