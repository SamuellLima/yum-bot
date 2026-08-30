from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from App.database.base import Base

if TYPE_CHECKING:
    from App.database.models.guild_role_reaction import GuildRoleReaction
    from App.database.models.users import Users


class GuildSettings(Base):
    __tablename__ = "guild_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guild_id: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    welcome_channel_id: Mapped[str | None] = mapped_column(String(20), nullable=True)
    welcome_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    roles_select_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    roles_select_title: Mapped[str | None] = mapped_column(String(256), nullable=True)
    roles_select_channel_id: Mapped[str | None] = mapped_column(String(20), nullable=True)
    roles_select_message_id: Mapped[str | None] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )
    join_role_id: Mapped[str | None] = mapped_column(String(20), nullable=True)
    users: Mapped[list[Users]] = relationship(back_populates="guild_settings")
    role_reactions: Mapped[list[GuildRoleReaction]] = relationship(
        back_populates="guild_settings", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<GuildSettings(guild_id={self.guild_id})>"
