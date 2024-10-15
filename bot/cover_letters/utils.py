from openai import AsyncOpenAI
from bot.config import openai_key
from loguru import logger

client = AsyncOpenAI(
    api_key=openai_key,
    base_url="https://api.proxyapi.ru/openai/v1",
)


# Function to generate cover letter using the OpenAI API
async def generate_cover_letter(resume_text, vacancy_text):
    prompt = f"""
    Напиши сопроводительное письмо на основе следующего резюме и текста вакансии.

    Резюме:
    {resume_text}

    Вакансия:
    {vacancy_text}

    Сопроводительное письмо:
    """

    try:
        logger.info("Отправка запроса на генерацию сопроводительного письма...")

        # Asynchronous request to OpenAI using AsyncOpenAI client
        response = await client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="gpt-4o-mini"
        )

        # Retrieving the response
        cover_letter = response.choices[0].message.content.strip()

        logger.info("Сопроводительное письмо успешно сгенерировано.")
        return cover_letter

    except Exception as e:
        logger.error(f"Ошибка при генерации сопроводительного письма: {str(e)}")
        return None
