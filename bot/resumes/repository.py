from bot.repository.base import BaseRepository
from bot.resumes.models import Resume


class ResumeRepository(BaseRepository):
    model = Resume
