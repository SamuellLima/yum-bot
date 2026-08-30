from sqlalchemy import select

from App.database.models import GuildRoleReaction, GuildSettings
from App.database.session import get_db

DEFAULT_ROLES_SELECT_TITLE = "Comunidades"
DEFAULT_ROLES_SELECT_MESSAGE = (
    "Seja bem-vindo ao canal de comunidades, aqui você poderá ingressar a "
    "comunidades específicas e ter acesso a canais de texto e de voz "
    "exclusivos para cada uso.\n"
    "\n"
    "\n"
    "Para começar veja as comunidades disponíveis e seus respectivos emojis. "
    "Reaja com o emoji equivalente a comunidade que você quer entrar:"
)


class RolesManager:
    """Mensagem de cargos e mapeamento emoji → cargo por servidor."""

    async def get_join_role(self, server_id: int) -> str | None:
        with get_db() as db:
            config = db.scalars(
                select(GuildSettings).where(GuildSettings.guild_id == str(server_id))
            ).first()
            if config is None:
                return None
            return config.join_role_id

    async def set_join_role(self, server_id: int, role_id: int) -> None:
        with get_db() as db:
            config = self._get_or_create_guild(db, server_id)
            config.join_role_id = str(role_id)

    def _get_or_create_guild(self, db, server_id: int) -> GuildSettings:
        config = db.scalars(
            select(GuildSettings).where(GuildSettings.guild_id == str(server_id))
        ).first()
        if config is None:
            config = GuildSettings(guild_id=str(server_id))
            db.add(config)
            db.flush()
        return config

    async def get_roles_select_message(self, server_id: int) -> str:
        with get_db() as db:
            config = db.scalars(
                select(GuildSettings).where(GuildSettings.guild_id == str(server_id))
            ).first()
            if config is None or not config.roles_select_message:
                return DEFAULT_ROLES_SELECT_MESSAGE
            return config.roles_select_message

    async def set_roles_select_message(self, server_id: int, message: str | None) -> None:
        with get_db() as db:
            config = self._get_or_create_guild(db, server_id)
            config.roles_select_message = message.strip() if message and message.strip() else None

    async def get_roles_select_title(self, server_id: int) -> str:
        with get_db() as db:
            config = db.scalars(
                select(GuildSettings).where(GuildSettings.guild_id == str(server_id))
            ).first()
            if config is None or not config.roles_select_title:
                return DEFAULT_ROLES_SELECT_TITLE
            return config.roles_select_title

    async def set_roles_select_title(self, server_id: int, title: str | None) -> None:
        with get_db() as db:
            config = self._get_or_create_guild(db, server_id)
            if title and title.strip():
                config.roles_select_title = title.strip()[:256]
            else:
                config.roles_select_title = None

    async def set_roles_select_panel(
        self, server_id: int, channel_id: int, message_id: int
    ) -> None:
        with get_db() as db:
            config = self._get_or_create_guild(db, server_id)
            config.roles_select_channel_id = str(channel_id)
            config.roles_select_message_id = str(message_id)

    async def get_roles_select_panel(self, server_id: int) -> tuple[str | None, str | None]:
        with get_db() as db:
            config = db.scalars(
                select(GuildSettings).where(GuildSettings.guild_id == str(server_id))
            ).first()
            if config is None:
                return None, None
            return config.roles_select_channel_id, config.roles_select_message_id

    async def list_role_reactions(self, server_id: int) -> list[dict]:
        with get_db() as db:
            config = db.scalars(
                select(GuildSettings).where(GuildSettings.guild_id == str(server_id))
            ).first()
            if config is None:
                return []
            rows = db.scalars(
                select(GuildRoleReaction).where(GuildRoleReaction.guild_settings_id == config.id)
            ).all()
            return [{"emoji": row.emoji, "role_id": row.role_id} for row in rows]

    async def set_role_reaction(self, server_id: int, emoji: str, role_id: int) -> None:
        with get_db() as db:
            config = self._get_or_create_guild(db, server_id)
            existing = db.scalars(
                select(GuildRoleReaction).where(
                    GuildRoleReaction.guild_settings_id == config.id,
                    GuildRoleReaction.emoji == emoji,
                )
            ).first()
            if existing:
                existing.role_id = str(role_id)
                return
            db.add(
                GuildRoleReaction(
                    guild_settings_id=config.id,
                    emoji=emoji,
                    role_id=str(role_id),
                )
            )

    async def remove_role_reaction(self, server_id: int, emoji: str) -> bool:
        with get_db() as db:
            config = db.scalars(
                select(GuildSettings).where(GuildSettings.guild_id == str(server_id))
            ).first()
            if config is None:
                return False
            row = db.scalars(
                select(GuildRoleReaction).where(
                    GuildRoleReaction.guild_settings_id == config.id,
                    GuildRoleReaction.emoji == emoji,
                )
            ).first()
            if row is None:
                return False
            db.delete(row)
            return True

    async def get_role_id_for_emoji(self, server_id: int, emoji: str) -> str | None:
        with get_db() as db:
            config = db.scalars(
                select(GuildSettings).where(GuildSettings.guild_id == str(server_id))
            ).first()
            if config is None:
                return None
            row = db.scalars(
                select(GuildRoleReaction).where(
                    GuildRoleReaction.guild_settings_id == config.id,
                    GuildRoleReaction.emoji == emoji,
                )
            ).first()
            return row.role_id if row else None
