import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

import config
import handlers

bot = Bot(token=config.BOT_TOKEN)


async def main():
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(handlers.router)

    # Удаляет все обновления которые пришли боту за время его простоя
    await bot.delete_webhook(drop_pending_updates=True)

    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    # Логируем всё кроме DEBUG
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
