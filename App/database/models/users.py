from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from App.database.base import Base

if TYPE_CHECKING:
    from App.database.models.guild_settings import GuildSettings


class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )
    xp: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    guild_settings_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("guild_settings.id"), nullable=False
    )

    guild_settings: Mapped[GuildSettings] = relationship(back_populates="users")

    def __repr__(self) -> str:
        return f"<Users(user_id={self.user_id})>"
