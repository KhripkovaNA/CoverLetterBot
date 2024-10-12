from aiogram.filters import CommandObject, CommandStart
from loguru import logger
from aiogram.types import Message
from aiogram.dispatcher.router import Router
from bot.database import connection
from bot.users.repository import UserRepository

user_router = Router()


@user_router.message(CommandStart())
@connection
async def cmd_start(message: Message, command: CommandObject, session, **kwargs):
    try:
        user_id = message.from_user.id
        user_info = await UserRepository.find_one_or_none(session=session, telegram_id=user_id)

        if user_info:
            await message.answer(f"Здравствуйте, {message.from_user.first_name}! Выберите необходимое действие")
            return

        # add a new user
        await UserRepository.add(
            session=session,
            telegram_id=user_id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )

        #
        msg = f"<b>Вы успешно зарегестрированы!</b>. Выберите необходимое действие"

        await message.answer(msg)

    except Exception as e:
        logger.error(f"Ошибка при выполнении команды /start для пользователя {message.from_user.id}: {e}")
        await message.answer("Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте снова позже.")
