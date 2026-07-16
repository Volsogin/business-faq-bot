"""Telegram-бот: принимает вопрос текстом, отвечает через FAQAssistant."""

import logging

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from app.llm import FAQAssistant

logger = logging.getLogger(__name__)

router = Router()

START_TEXT = (
    "👋 Здравствуйте! Я бот-ассистент барбершопа.\n\n"
    "Задайте любой вопрос про услуги, цены, часы работы или запись — "
    "я отвечу на основе нашей базы. Если чего-то не знаю, передам администратору."
)

ADMIN_TEXT = (
    "🛠 <b>Панель администратора (демо)</b>\n\n"
    "База знаний бота хранится в отдельном файле "
    "<code>data/knowledge_base.yaml</code> и не зашита в код.\n\n"
    "Чтобы добавить или изменить вопрос/ответ:\n"
    "1. Откройте <code>data/knowledge_base.yaml</code>\n"
    "2. Добавьте новый пункт в список <code>faq</code>:\n"
    "<pre>  - question: \"Есть ли скидки студентам?\"\n"
    "    answer: \"Да, по студенческому — 10%.\"</pre>\n"
    "3. Перезапустите бота.\n\n"
    "Так базу можно расширять без правки кода. В реальном проекте здесь была бы "
    "форма редактирования и проверка прав администратора."
)


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(START_TEXT)


@router.message(Command("admin"))
async def cmd_admin(message: Message) -> None:
    await message.answer(ADMIN_TEXT)


@router.message(F.text)
async def handle_question(message: Message, assistant: FAQAssistant) -> None:
    await message.bot.send_chat_action(message.chat.id, "typing")
    answer = await assistant.answer(message.text)
    await message.answer(answer)


@router.message()
async def handle_non_text(message: Message) -> None:
    await message.answer("Пожалуйста, задайте вопрос текстом 🙂")
