import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramNetworkError
from aiogram.fsm.storage.memory import MemoryStorage

import config
from analytics.middleware import VisitTrackingMiddleware
from analytics.storage import init_db
from handlers import cases, demo, main_menu, privacy, start
from handlers.consent_gate import ConsentGateMiddleware

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


async def main() -> None:
    init_db()

    session = AiohttpSession(proxy=config.BOT_PROXY) if config.BOT_PROXY else AiohttpSession()
    bot = Bot(
        token=config.BOT_TOKEN,
        session=session,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    gate = ConsentGateMiddleware()
    dp.message.middleware(gate)
    dp.callback_query.middleware(gate)

    tracking = VisitTrackingMiddleware()
    dp.message.middleware(tracking)
    dp.callback_query.middleware(tracking)

    dp.include_router(privacy.router)
    dp.include_router(start.router)
    dp.include_router(main_menu.router)
    dp.include_router(demo.router)
    dp.include_router(cases.router)

    # api.telegram.org с некоторых хостингов отвечает нестабильно — ретраим, а не падаем.
    for attempt in range(1, 6):
        try:
            await bot.delete_webhook(drop_pending_updates=True)
            break
        except TelegramNetworkError as exc:
            logger.warning("Telegram API недоступен (попытка %d/5): %s", attempt, exc)
            if attempt == 5:
                raise
            await asyncio.sleep(10 * attempt)
    logger.info("Bot started, polling...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped")
