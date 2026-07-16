"""Интеграция с LLM через OpenRouter: отвечает на вопрос строго по базе знаний.

OpenRouter отдаёт OpenAI-совместимый API, поэтому используется официальный
клиент `openai` с указанием base_url OpenRouter. Модель задаётся в формате
provider/model (например, deepseek/deepseek-v4-flash).
"""

import logging

from openai import AsyncOpenAI, OpenAIError

from app.knowledge_base import KnowledgeBase

logger = logging.getLogger(__name__)

# фраза-заглушка, которую бот отдаёт, если ответа в базе нет
FALLBACK_ANSWER = "Не нашёл точного ответа в базе — уточню у администратора и вернусь к вам."

SYSTEM_PROMPT_TEMPLATE = """Ты — вежливый ассистент-консультант компании «{business_name}» в Telegram.

Отвечай на вопросы клиентов ТОЛЬКО на основе базы знаний ниже.

Правила:
- Если ответ есть в базе — дай его понятно и дружелюбно, можно чуть переформулировать.
- Если точного ответа в базе НЕТ — не выдумывай факты (цены, адреса, телефоны, часы).
  В этом случае ответь ровно фразой: "{fallback}"
- Не придумывай услуги, цены и условия, которых нет в базе.
- Отвечай кратко, на русском языке, по делу.

{kb_block}
"""


class FAQAssistant:
    def __init__(self, api_key: str, base_url: str, model: str,
                 knowledge_base: KnowledgeBase):
        self._client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self._model = model
        self._system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
            business_name=knowledge_base.business_name,
            fallback=FALLBACK_ANSWER,
            kb_block=knowledge_base.as_prompt_block(),
        )

    async def answer(self, question: str) -> str:
        """Возвращает ответ на вопрос. При сбое API — мягкий fallback."""
        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                max_tokens=1024,
                messages=[
                    {"role": "system", "content": self._system_prompt},
                    {"role": "user", "content": question},
                ],
            )
        except OpenAIError as e:
            logger.error("Ошибка LLM API: %s", e)
            return FALLBACK_ANSWER

        if not response.choices:
            return FALLBACK_ANSWER
        text = (response.choices[0].message.content or "").strip()
        return text or FALLBACK_ANSWER
