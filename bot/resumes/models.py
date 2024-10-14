from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Text
from bot.database import Base


class Resume(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    name: Mapped[str] = mapped_column(nullable=False, default='Основное резюме')
    resume_text: Mapped[str] = mapped_column(Text, nullable=False)

    user: Mapped['User'] = relationship("User", back_populates="resumes")
