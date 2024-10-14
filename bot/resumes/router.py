from io import BytesIO
from aiogram import F
from aiogram.types import Message
from aiogram.dispatcher.router import Router
from loguru import logger
from bot.resumes.repository import ResumeRepository
from bot.resumes.utils import convert_pdf_to_text
from bot.users.repository import UserRepository

resume_router = Router()


@resume_router.message(F.content_type == 'document')
async def handle_resume_upload(message: Message):
    try:
        if message.document.mime_type == 'application/pdf':
            telegram_id = message.from_user.id
            user = await UserRepository.find_one_or_none(
                telegram_id=telegram_id,
                related_objects=['resumes'],
                load_strategy='selectin'
            )

            if len(user.resumes) > 0:
                await message.reply("У вас уже есть загруженное резюме")
                return

            file_info = await message.bot.get_file(message.document.file_id)
            file_stream = await message.bot.download_file(file_info.file_path)

            await message.answer("Резюме обрабатывается, пожалуйста, подождите...")

            # Convert PDF to text
            resume_text = await convert_pdf_to_text(BytesIO(file_stream.read()))

            if resume_text:

                await ResumeRepository.add(
                    user_id=user.id,
                    resume_text=resume_text
                )

                await message.answer("Ваше резюме успешно сохранено!")
                await message.answer("Скопируйте и отправьте текст вакансии")

            else:
                await message.answer("Не удалось конвертировать pdf в текст. Попробуйте загрузить другой файл")

        else:
            await message.answer("Пожалуйста, загрузите pdf файл")

    except Exception as e:
        logger.error(f"Ошибка при загрузке резюме: {e}")
        await message.answer("Произошла ошибка при обработке вашего резюме")
