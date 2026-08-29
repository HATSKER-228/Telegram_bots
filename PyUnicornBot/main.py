import asyncio
from aiogram import Bot, Dispatcher

from src.config import TOKEN
from src.tools import numbers as num
from src import midwares_filters as mwf
from src.handlers import routers

bot = Bot(token=TOKEN)
dp = Dispatcher()

dp.update.middleware(mwf.UserUpdateMiddleware())

for router in routers:
    dp.include_router(router)


async def cleanup_stale_games_loop() -> None:
    while True:
        await asyncio.sleep(60 * 60)  # раз на годину
        stale_chat_ids = num.cleanup_stale_games()
        for str_chat_id in stale_chat_ids:
            try:
                await bot.send_message(int(str_chat_id), '🗑 Гру "Числа" видалено через бездіяльність (більше доби без активності).')
            except Exception:
                pass  # бота могли видалити з чату/заблокувати за цей час


async def main() -> None:
    asyncio.create_task(cleanup_stale_games_loop())
    await dp.start_polling(bot, allowed_updates=['message', 'callback_query', 'inline_query', 'message_reaction'])


if __name__ == "__main__":
    asyncio.run(main())
