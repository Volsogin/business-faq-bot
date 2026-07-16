import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "deepseek/deepseek-v4-flash")
KNOWLEDGE_BASE_PATH = os.getenv("KNOWLEDGE_BASE_PATH", "data/knowledge_base.yaml")
