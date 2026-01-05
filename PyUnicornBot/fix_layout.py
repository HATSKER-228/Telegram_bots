from aiogram.types import MessageEntity


KB_LAYOUTS: dict[str, str] = {
    'qwerty': '`1234567890-=qwertyuiop[]\\asdfghjkl;\'zxcvbnm,./~!@#$%^&*()_+QWERTYUIOP{}|ASDFGHJKL:"ZXCVBNM<>?',
    'ytsuken': '\'1234567890-=йцукенгшщзхї\фівапролджєячсмитьбю.₴!"№;%:?*()_+ЙЦУКЕНГШЩЗХЇ/ФІВАПРОЛДЖЄЯЧСМИТЬБЮ,'
}
PROTECTED_ENTITIES: set[str] = {'mention', 'hashtag', 'cashtag', 'bot_command', 'url', 'email', 'code', 'pre', 'text_link', 'text_mention'}


def get_utf16_len(s: str) -> int:
    return len(s.encode('utf-16-le')) // 2


def map_utf16_to_indexes(text: str) -> list[int]:
    lst = []
    for i, char in enumerate(text):
        utf16_char_len = get_utf16_len(char)
        for _ in range(utf16_char_len):
            lst.append(i)
    return lst


def get_protected_indexes(text: str, entities: list[MessageEntity]) -> set[int]:
    protected = set()

    if not entities:
        return protected

    utf16_to_indexes: list[int] = map_utf16_to_indexes(text)

    for ent in entities:
        if ent.type in PROTECTED_ENTITIES:
            for utf16_pos in range(ent.offset, ent.offset + ent.length):
                protected.add(utf16_to_indexes[utf16_pos])

    return protected


def fix_layout(text: str, entities: list[MessageEntity], from_layout: str, to_layout: str) -> str:
    protected: set[int] = get_protected_indexes(text, entities)
    result: str = ''

    for i, char in enumerate(text):
        if i in protected:
            result += char
            continue
        index: int = from_layout.find(char)
        if index == -1:
            result += char
        else:
            result += to_layout[index]

    return result


def determinate_lang(text: str) -> str:
    s: set = set(text.lower())
    ua: set = set('йцукенгшщзфівапролджєячсмитьбю')
    if len(s.intersection(ua)):
        return 'ua'
    return 'eng'
