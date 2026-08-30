from sqlalchemy import select, update

from App.database.models import GuildSettings
from App.database.session import get_db


class ServersConfigManager:
    """Gerencia a configuração dos servidores."""

    async def get_server_config(self, server_id: int) -> GuildSettings | None:
        with get_db() as db:
            return db.scalars(
                select(GuildSettings).where(GuildSettings.guild_id == str(server_id))
            ).first()

    async def update_server_config(self, server_id: int, **values) -> None:
        with get_db() as db:
            db.execute(
                update(GuildSettings)
                .where(GuildSettings.guild_id == str(server_id))
                .values(**values)
            )

    async def get_welcome_channel_id(self, server_id: int) -> str | None:
        config = await self.get_server_config(server_id)
        return config.welcome_channel_id if config else None

    async def get_welcome_message(self, server_id: int) -> str | None:
        config = await self.get_server_config(server_id)
        return config.welcome_message if config else None

    async def set_welcome_channel_id(self, server_id: int, channel_id: int | str) -> None:
        channel_id = str(channel_id)
        with get_db() as db:
            config = db.scalars(
                select(GuildSettings).where(GuildSettings.guild_id == str(server_id))
            ).first()
            if config:
                config.welcome_channel_id = channel_id
            else:
                db.add(
                    GuildSettings(
                        guild_id=str(server_id),
                        welcome_channel_id=channel_id,
                    )
                )

    async def set_welcome_message(self, server_id: int, message: str) -> None:
        await self.update_server_config(server_id, welcome_message=message)
