from aiogram.filters import CommandStart
from loguru import logger
from aiogram.types import Message
from aiogram.dispatcher.router import Router
from bot.resumes.repository import ResumeRepository
from bot.users.repository import UserRepository

user_router = Router()


@user_router.message(CommandStart())
async def cmd_start(message: Message):
    try:
        telegram_id = message.from_user.id
        user_info = await UserRepository.find_one_or_none(
                telegram_id=telegram_id,
                related_objects=['resumes'],
                load_strategy='selectin'
            )

        if user_info:
            msg = f"С возвращением, {message.from_user.full_name}! Давайте составим сопроводительное письмо"
            await message.answer(msg)

            if len(user_info.resumes) > 0:
                msg = "У вас уже есть загруженное резюме. Скопируйте и отправьте текст вакансии"
                await message.reply(msg)
                return

        else:
            # add a new user
            await UserRepository.add(
                telegram_id=telegram_id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name
            )

            msg = f"Добро пожаловать, {message.from_user.full_name}! Давайте составим сопроводительное письмо"

            await message.answer(msg)

        await message.answer("Загрузите свое резюме в формате pdf (не более 1MB)")

    except Exception as e:
        logger.error(f"Ошибка при выполнении команды /start для пользователя {message.from_user.id}: {e}")
        await message.answer("Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте снова позже")
