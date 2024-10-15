from io import BytesIO
import aiohttp
from loguru import logger
from bot.config import cm_api_key


# Function to convert a PDF file to text using the Cloudmersive API
async def convert_pdf_to_text(file_stream: BytesIO):
    url = "https://api.cloudmersive.com/convert/pdf/to/txt"
    headers = {
        "Apikey": cm_api_key,
        "textFormattingMode": "minimizeWhitespace"
    }
    files = {
        "file": file_stream
    }

    # Create an asynchronous HTTP session to make the request
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, headers=headers, data=files) as response:
                logger.info(f"Конвертация файла pdf в текст. Статус: {response.status}")

                if response.status == 200:
                    result = await response.json()
                    text = result.get("TextResult")

                    if text:
                        text = text.strip()
                        text = '\n'.join([line.strip() for line in text.splitlines() if line.strip()])

                    return text
                else:
                    logger.error(f"Failed to convert PDF. Status: {response.status}, Reason: {response.reason}")
                    return None
        except Exception as e:
            logger.error(f"Error during PDF conversion: {str(e)}")
            return None
