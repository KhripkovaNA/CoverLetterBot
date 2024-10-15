from io import BytesIO
from aiogram import F
from aiogram.types import Message
from aiogram.dispatcher.router import Router
from loguru import logger
from bot.resumes.repository import ResumeRepository
from bot.resumes.utils import convert_pdf_to_text
from bot.users.repository import UserRepository

resume_router = Router()


# Handler for processing uploaded resumes
@resume_router.message(F.content_type == 'document')
async def handle_resume_upload(message: Message):
    try:
        # Check if the uploaded file is a pdf
        if message.document.mime_type == 'application/pdf':
            telegram_id = message.from_user.id

            # Fetch user data and related resumes
            user = await UserRepository.find_one_or_none(
                telegram_id=telegram_id,
                related_objects=['resumes'],
                load_strategy='selectin'
            )

            # If the user has an existing resume, inform them and return
            if len(user.resumes) > 0:
                await message.reply("У вас уже есть загруженное резюме")
                return

            # Retrieve the uploaded file and download it as a stream
            file_info = await message.bot.get_file(message.document.file_id)
            file_stream = await message.bot.download_file(file_info.file_path)

            await message.answer("Резюме обрабатывается, пожалуйста, подождите...")

            # Convert the pdf to text using the helper function
            resume_text = await convert_pdf_to_text(BytesIO(file_stream.read()))

            if resume_text:
                # Save the extracted text into the database
                await ResumeRepository.add(
                    user_id=user.id,
                    resume_text=resume_text
                )

                await message.answer("Ваше резюме успешно сохранено!")
                await message.answer("Скопируйте и отправьте текст вакансии")

            else:
                # Inform the user if the pdf conversion fails
                await message.answer("Не удалось конвертировать pdf в текст. Попробуйте загрузить другой файл")

        else:
            # Notify the user to upload a pdf file if the document is not in pdf format
            await message.answer("Пожалуйста, загрузите pdf файл")

    except Exception as e:
        # Log any errors and inform the user of the failure
        logger.error(f"Ошибка при загрузке резюме: {e}")
        await message.answer("Произошла ошибка при обработке вашего резюме")
