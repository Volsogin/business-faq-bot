"""Загрузка базы знаний из YAML и сборка её в текст для системного промпта.

База короткая (15-20 пунктов), поэтому «RAG» здесь — это просто вставка всей
базы в системный промпт. Для большой базы тут появился бы поиск релевантных
пунктов, но для FAQ локального бизнеса это избыточно.
"""

from dataclasses import dataclass, field

import yaml


@dataclass
class KnowledgeBase:
    business_name: str
    city: str
    faq: list[dict] = field(default_factory=list)

    def as_prompt_block(self) -> str:
        """Форматирует базу знаний как текст для вставки в системный промпт."""
        lines = [f"Бизнес: {self.business_name} (город: {self.city}).", "", "База знаний (вопрос → ответ):"]
        for i, item in enumerate(self.faq, 1):
            lines.append(f"{i}. В: {item['question']}")
            lines.append(f"   О: {item['answer']}")
        return "\n".join(lines)


def load_knowledge_base(path: str) -> KnowledgeBase:
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    business = data.get("business") or {}
    return KnowledgeBase(
        business_name=business.get("name", "наш бизнес"),
        city=business.get("city", ""),
        faq=data.get("faq") or [],
    )
