from bot.repository.base import BaseRepository
from bot.users.models import User


class UserRepository(BaseRepository):
    model = User
