# Telegram Cover Letter Generator Bot

## Overview
This project is a Telegram bot designed to help users generate personalized cover letters based on their resumes and job vacancy descriptions. By leveraging OpenAI's API, the bot converts user-uploaded resumes (in PDF format) into text and utilizes the provided vacancy text to create tailored cover letters.

## Features
- **User-Friendly Interaction:** Users can easily interact with the bot to upload their resumes and provide job descriptions.
- **Resume Handling:** The bot supports uploading resumes in PDF format (up to 1MB) and processes them asynchronously.
- **Automated Cover Letter Generation:** Utilizing OpenAI's API, the bot generates professional cover letters tailored to specific job vacancies.
- **Data Management:** User data and resumes are stored in a database, allowing for easy access and management.
- **Error Handling:** Comprehensive error handling ensures a smooth user experience.

## Technologies Used
- **Python 3.12:** The primary programming language used for backend development.
- **Aiogram:** A powerful framework for building Telegram bots with support for asynchronous operations.
- **Aiohttp:** An asynchronous HTTP client/server framework for handling HTTP requests in a non-blocking, concurrent manner.
- **SQLAlchemy:** For database management and ORM functionalities.
- **OpenAI API:** For generating cover letters based on user resumes and job descriptions.
- **SQLite:** Used as the database.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/KhripkovaNA/CoverLetterBot.git
   ```
2. Navigate to the project directory:
   ```bash
   cd CoverLetterBot
   ```
3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables for API keys and database configuration.
5. Run the bot:
   ```bash
   python main.py
   ```

## Usage
### Commands:
- **/start**: Starts the bot, saves the user in the database if needed, replies with a personalized greeting and asks to upload a resume.

### Interactive Messages:
- If a user uploads a resume, the bot converts it into text and saves it in the database. Then, the bot asks the user to copy and paste a vacancy description.
- When the user sends the vacancy description, the bot generates a cover letter tailored to the job vacancy and sends it back to the user.
