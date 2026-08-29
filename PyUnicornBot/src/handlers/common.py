from aiogram import Router, F
from aiogram.types import Message, MessageReactionUpdated
from aiogram.filters import Command
from random import randint

from src import fix_layout as fl
from src import midwares_filters as mwf

router = Router()


@router.message(Command('start'))
async def cmd_start(message: Message) -> None:
    if message.chat.type == 'private':
        text = 'Привіт, пупсику ❤️. Я - Unicorn Bot. Ти можеш побачити, що я вмію робити, надіславши команду /help.'
    elif message.chat.type in {'group', 'supergroup'}:
        text = 'Привіт, пупсики ❤️. Я - Unicorn Bot. Ви можете побачити, що я вмію робити, надіславши команду /help@PyUnicornBot.'
    else:
        text = 'Цю команду можна використати тільки в групі або в особистих повідомленнях зі мною 🧌'
    await message.answer(text)
     

@router.message(Command('help'))
async def cmd_help(message: Message) -> None:
    await message.answer('''Ось список того, що я вмію:
/start - привітаннячка від мене
/help - надішлю оце повідомлення
/fix - виправлю розкладку повідомлення (з qwerty на йцукен, або ж навпаки)
/shypko - оціню повідомлення від 0 до 10
/rules - надішлю правила кожної мініігри
/updates - скажу що нового

<b>!!!Тільки в групі!!!</b>
<u>Пупсик дня</u>
/baby_reg - додам тебе у список Пупсиків
/baby_unreg - видалю тебе з Пупсиків
/baby_select - оберу Пупсика дня (лише раз в день)
/baby_stats - надішлю статистику хто скільки разів був Пупсиком дня

<u>Гра "Числа"</u>
/create - створю гру
/cancel - скасувати гру''', parse_mode='HTML')
    

@router.message(Command('fix'), mwf.ReplyOnlyFilter())
async def cmd_fix(message: Message) -> None:
    replied = message.reply_to_message
    text = replied.text or replied.caption
    entities = replied.entities or replied.caption_entities

    if text:
        src = fl.detect_layout(text)
        dst = fl.KB_LAYOUT_PAIRS[src]
        fixed = fl.fix_layout(text, entities, fl.KB_LAYOUTS[src], fl.KB_LAYOUTS[dst])

        await replied.reply(text=fixed, entities=entities)
        await message.delete()
    else:
        await message.reply('Шановний тупорилий представник виду <i>Homo Sapiens</i>, команду необхідно писати у '
                            'відповідь на ТЕКСТ 🧌', parse_mode='HTML')


@router.message(Command('shypko'), mwf.ReplyOnlyFilter())
async def cmd_shypko(message: Message) -> None:
    await message.reply_to_message.reply(f'Я оцінюю це повідомлення на {randint(0, 10)} шипко з 10.')


@router.message(Command('rules'))
async def cmd_rules(message: Message) -> None:
    text = '''📜 <b>Правила мініігор</b>
👶 <i>Пупсик дня:</i>
• Щоб долучитися, напиши мені /baby_reg.
• Якщо передумаєш — вийди з гри командою /baby_unreg.
• Я можу обрати пупсика дня — для цього напиши /baby_select.
• Я обираю випадкового гравця зі списку, і роблю це лише один раз на день.
• Подивитися, скільки разів хто ставав пупсиком, можна через /baby_stats.

🎯 <i>Гра "Числа":</i>
• Це гра для двох гравців, які мають бути в одній групі.
• Створити гру можна командою /create.
• Я сам напишу кожному з гравців у приват і попрошу загадати 4-цифрове число з різних цифр.
• Після цього гравці по черзі надсилають у групу здогадки, написавши @PyUnicornBot.
• Я у відповідь надсилаю підказку виду ХХО або ж ХХОО:
    X — цифра є і стоїть на правильному місці.
    O — цифра є, але стоїть не там.
• Розташування символів в підказці не пов'язане з розташуванням цифр у числі опонента.
• Виграє той, хто першим вгадає число суперника повністю.
• Якщо хочете скасувати гру — напишіть /cancel.
• В одній групі може бути лише одна активна гра.
• Якшо гра не активна більше доби, вона автоматично видаляється'''
    await message.answer(text, parse_mode='HTML')


@router.message(Command('updates'))
async def cmd_updates(message: Message) -> None:
    text = '''📜 <u><b>Що нового у Unicorn Bot</b></u>
<b>27.08.2026</b>    
<i>👍</i>
• Тепер в групах, якщо хтось напише 👍, бот теж відповість 👍
• Бот ставить реакцію "👍", якщо хтось теж поставив "👍"

<b>17.07.2026</b>    
<i>Анімація обирання Пупсика дня</i>
• Якшо Пупсика сьогодні все ще не обрано, то під час вибору бот буде крутить рулетку хто сьогодні Пупсик.

<i>Різні виправлення помилок та оптимізація</i>


<u><b>Попередні оновлення:</b></u>
07.07.2026 - оптимізація UI/UX гри "Числа"
07.01.2026 - оновлення команди /fix, inline-прийняття спроб у грі "Числа"
05.01.2026 - оновлення команди /fix
03.01.2026 - додання команди /updates, кешування імен користувачів
08.11.2025 - видалення команди /all
04.08.2025 - оновлення команди /baby_unreg
01.08.2025 - додання команди /all
28.07.2025 - додання кнопки "Рандомне число" у грі "Числа"
27.07.2025 - додання команд /rules, /shypko, а також показ числа переможця у грі "Числа"
26.07.2025 - додання гри "Числа"
18.07.2025 - додання Пупсиків дня
18.07.2025 - перехід на бібліотеку aiogram
'''
    await message.answer(text, parse_mode='HTML')


@router.message(F.chat.type.in_({'group', 'supergroup'}), F.text.contains('👍'))
async def thumbs_up_reply(message: Message) -> None:
    try:
        await message.reply('👍')
    except Exception:
        pass


@router.message_reaction()
async def on_like_reaction(event: MessageReactionUpdated) -> None:
    liked = any(r.type == 'emoji' and r.emoji == '👍' for r in event.new_reaction)

    if liked:
        try:
            await event.bot.set_message_reaction(
                chat_id=event.chat.id,
                message_id=event.message_id,
                reaction=[{'type': 'emoji', 'emoji': '👍'}]
            )
        except Exception:
            pass