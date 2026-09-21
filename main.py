import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

import config
from analytics.middleware import VisitTrackingMiddleware
from analytics.storage import init_db
from handlers import cases, demo, main_menu, start

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


async def main() -> None:
    init_db()

    bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())

    tracking = VisitTrackingMiddleware()
    dp.message.middleware(tracking)
    dp.callback_query.middleware(tracking)

    dp.include_router(start.router)
    dp.include_router(main_menu.router)
    dp.include_router(demo.router)
    dp.include_router(cases.router)

    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Bot started, polling...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped")
