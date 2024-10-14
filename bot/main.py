import asyncio
from aiogram.types import BotCommand, BotCommandScopeDefault
from loguru import logger
from bot.config import bot, dp
from bot.resumes.router import resume_router
from bot.users.router import user_router


# Function to set default command menu
async def set_commands():
    commands = [BotCommand(command='start', description='Старт')]
    await bot.set_my_commands(commands, BotCommandScopeDefault())


# Function to be executed when the bot is started
async def start_bot():
    await set_commands()
    logger.info("Бот запущен")


# Function to be executed when the bot is stopped
async def stop_bot():
    logger.error("Бот остановлен")


async def main():
    # registration of the routs
    dp.include_router(user_router)
    dp.include_router(resume_router)

    # registration of the functions
    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)

    # launching the bot in long polling mode cleaning all the updates during standby
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
