import asyncio

from loguru import logger
from aiogram.types import Message
from aiogram.dispatcher.router import Router
from bot.cover_letters.utils import generate_cover_letter
from bot.users.repository import UserRepository

cover_letter_router = Router()

MESSAGE_TIMEOUT = 2
user_messages_cache = {}


@cover_letter_router.message()
async def on_vacancy_received(message: Message):
    telegram_id = message.from_user.id
    logger.info(f"Получен запрос от пользователя с telegram_id: {telegram_id}")

    # Если это первое сообщение для пользователя, создаем запись в кэше
    if telegram_id not in user_messages_cache:
        user_messages_cache[telegram_id] = []

    # Добавляем сообщение пользователя в кэш
    user_messages_cache[telegram_id].append(message.text)

    # Ждем указанное время на случай, если придут еще сообщения
    await asyncio.sleep(MESSAGE_TIMEOUT)

    # После истечения тайм-аута проверяем, что больше сообщений не пришло
    if len(user_messages_cache[telegram_id]) > 1:
        logger.info(f"Получено несколько сообщений от пользователя {telegram_id}. Объединение в один текст.")

    vacancy_text = ' '.join(user_messages_cache[telegram_id]).strip()

    # Очищаем кэш сообщений после обработки
    user_messages_cache.pop(telegram_id, None)
    telegram_id = message.from_user.id

    try:
        # Поиск пользователя по telegram_id
        user = await UserRepository.find_one_or_none(
            telegram_id=telegram_id,
            related_objects=['resumes'],
            load_strategy='selectin'
        )

        # Проверка наличия резюме
        if not user or not user.resumes:
            if not user:
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
            return

        if not vacancy_text or len(vacancy_text) < 20:
            logger.warning(f"Текст вакансии пуст или слишком короткий для пользователя {telegram_id}")
            msg = """
                Текст вакансии слишком короткий.
                Пожалуйста, отправьте текст вакансии для генерации сопроводительного письма
            """
            await message.reply(msg)
            return

        resume_text = user.resumes[0].resume_text

        logger.info(f"Генерацию сопроводительного письма для пользователя {telegram_id}")
        await message.answer("Составляем сопроводительное письмо, пожалуйста, подождите...")

        # Генерация сопроводительного письма
        cover_letter = await generate_cover_letter(resume_text, vacancy_text)

        # Ответ пользователю
        if cover_letter:
            logger.info(f"Сопроводительное письмо сгенерировано для пользователя {telegram_id}")
            await message.answer("Ваше сопроводительное письмо готово!")
            await message.answer(cover_letter)
        else:
            logger.error(f"Не удалось сгенерировать сопроводительное письмо для пользователя {telegram_id}")
            await message.answer("Не удалось сгенерировать сопроводительное письмо.")

    except Exception as e:
        logger.error(f"Ошибка при генерации сопроводительного письма для пользователя {telegram_id}: {e}")
        await message.answer("Произошла ошибка при генерации сопроводительного письма.")
