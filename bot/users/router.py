from aiogram.filters import CommandStart
from loguru import logger
from aiogram.types import Message
from aiogram.dispatcher.router import Router
from bot.users.repository import UserRepository

user_router = Router()


# Handler for processing /start command
@user_router.message(CommandStart())
async def cmd_start(message: Message):
    try:
        telegram_id = message.from_user.id

        # Check if the user already exists in the database
        user_info = await UserRepository.find_one_or_none(
                telegram_id=telegram_id,
                related_objects=['resumes'],
                load_strategy='selectin'
            )

        if user_info:
            # If the user is found, welcome them back
            msg = f"С возвращением, {message.from_user.full_name}! Давайте составим сопроводительное письмо"
            await message.answer(msg)

            if len(user_info.resumes) > 0:
                # If the user already has resumes uploaded, prompt them to send the job description
                msg = "У вас уже есть загруженное резюме. Скопируйте и отправьте текст вакансии"
                await message.reply(msg)
                return

        else:
            # If the user doesn't exist, add them to the database
            await UserRepository.add(
                telegram_id=telegram_id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name
            )

            # Send a welcome message to the new user
            msg = f"Добро пожаловать, {message.from_user.full_name}! Давайте составим сопроводительное письмо"

            await message.answer(msg)

        # Ask the user to upload their resume in pdf format
        await message.answer("Загрузите свое резюме в формате pdf (не более 1MB)")

    except Exception as e:
        # Log the error and inform the user that something went wrong
        logger.error(f"Ошибка при выполнении команды /start для пользователя {message.from_user.id}: {e}")
        await message.answer("Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте снова позже")
