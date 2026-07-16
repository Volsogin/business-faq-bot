"""Точка входа: собирает базу знаний, ассистента и бота."""

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app import config
from app.bot import router
from app.knowledge_base import load_knowledge_base
from app.llm import FAQAssistant

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> None:
    if not config.BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN не задан. Скопируйте .env.example в .env и заполните.")
    if not config.OPENROUTER_API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY не задан. Скопируйте .env.example в .env и заполните.")

    knowledge_base = load_knowledge_base(config.KNOWLEDGE_BASE_PATH)
    logger.info("База знаний загружена: %d пунктов.", len(knowledge_base.faq))

    assistant = FAQAssistant(
        api_key=config.OPENROUTER_API_KEY,
        base_url=config.OPENROUTER_BASE_URL,
        model=config.LLM_MODEL,
        knowledge_base=knowledge_base,
    )

    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()
    dp.include_router(router)
    # aiogram прокинет assistant в хендлеры как одноимённый аргумент
    dp["assistant"] = assistant

    logger.info("Бот запущен. Модель: %s", config.LLM_MODEL)
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Остановлено.")
