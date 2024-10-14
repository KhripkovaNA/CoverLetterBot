import os
from loguru import logger
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from pydantic_settings import BaseSettings, SettingsConfigDict

basedir = os.path.dirname(os.path.abspath(__file__))


class Settings(BaseSettings):
    BOT_TOKEN: str
    CLOUDMERSIVE_API_KEY: str
    FORMAT_LOG: str = "{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}"
    LOG_ROTATION: str = "10 MB"
    DB_URL: str = 'sqlite+aiosqlite:///' + os.path.join(basedir, "..", 'data/db.sqlite3')
    model_config = SettingsConfigDict(
        env_file=os.path.join(basedir, "..", ".env")
    )


settings = Settings()

# Bot and dispatcher initialisation
bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())


log_file_path = os.path.join(basedir, "log.txt")
logger.add(log_file_path, format=settings.FORMAT_LOG, level="INFO", rotation=settings.LOG_ROTATION)
database_url = settings.DB_URL
