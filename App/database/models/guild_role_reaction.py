from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from App.database.base import Base

if TYPE_CHECKING:
    from App.database.models.guild_settings import GuildSettings


class GuildRoleReaction(Base):
    __tablename__ = "guild_role_reactions"
    __table_args__ = (
        UniqueConstraint(
            "guild_settings_id",
            "emoji",
            name="uq_guild_role_reactions_guild_emoji",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guild_settings_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("guild_settings.id"), nullable=False
    )
    emoji: Mapped[str] = mapped_column(String(80), nullable=False)
    role_id: Mapped[str] = mapped_column(String(20), nullable=False)

    guild_settings: Mapped[GuildSettings] = relationship(back_populates="role_reactions")

    def __repr__(self) -> str:
        return f"<GuildRoleReaction(emoji={self.emoji}, role_id={self.role_id})>"
