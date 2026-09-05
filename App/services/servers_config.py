from sqlalchemy import func, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert

from App.database.models import GuildSettings, Users
from App.database.session import get_db
from App.utils.print import Print

_MEMBER_INSERT_CHUNK = 2000

class ServersConfigManager:
    """Gerencia a configuração dos servidores."""

    async def get_server_config(self, server_id: int) -> GuildSettings | None:
        async with get_db() as db:
            return await db.scalar(
                select(GuildSettings).where(GuildSettings.guild_id == str(server_id))
            )

    async def update_server_config(self, server_id: int, **values) -> None:
        async with get_db() as db:
            await db.execute(
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
        async with get_db() as db:
            config = await db.scalar(
                select(GuildSettings).where(GuildSettings.guild_id == str(server_id))
            )
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

    async def bootstrap_guild(
        self, server_id: int, members: list[tuple[str, str]]
    ) -> dict[str, int | bool]:
        """Cadastra o servidor e os membros em lote (INSERT ... ON CONFLICT).

        `members` é uma lista de `(user_id, username)`. Quem já estiver no banco
        não é alterado (XP e contadores ficam intactos).
        """
        unique_members = {user_id: username[:100] for user_id, username in members if user_id}
        async with get_db() as db:
            guild_insert = (
                pg_insert(GuildSettings)
                .values(guild_id=str(server_id))
                .on_conflict_do_nothing(index_elements=[GuildSettings.guild_id])
                .returning(GuildSettings.id)
            )
            guild_pk = await db.scalar(guild_insert)
            guild_created = guild_pk is not None
            if guild_pk is None:
                guild_pk = await db.scalar(
                    select(GuildSettings.id).where(GuildSettings.guild_id == str(server_id))
                )
            if guild_pk is None:
                Print.error(f"Não foi possível cadastrar o servidor {server_id}.")
                raise RuntimeError(f"Não foi possível cadastrar o servidor {server_id}.")

            if guild_created:
                Print.info(f"Servidor {server_id} cadastrado no banco de dados.")

            rows = [
                {
                    "user_id": user_id,
                    "username": username,
                    "xp": 0,
                    "guild_settings_id": guild_pk,
                    "count_messages": 0,
                    "total_messages": 0,
                    "count_voice_minutes": 0,
                }
                for user_id, username in unique_members.items()
            ]
            registered = 0
            if rows:
                for offset in range(0, len(rows), _MEMBER_INSERT_CHUNK):
                    chunk = rows[offset : offset + _MEMBER_INSERT_CHUNK]
                    result = await db.execute(
                        pg_insert(Users)
                        .values(chunk)
                        .on_conflict_do_nothing(constraint="uq_users_user_id_guild_settings_id")
                    )
                    registered += result.rowcount or 0

            already = len(unique_members) - registered
            total = (
                await db.scalar(
                    select(func.count())
                    .select_from(Users)
                    .where(Users.guild_settings_id == guild_pk)
                )
                or 0
            )
            Print.info(
                f"Setup do servidor {server_id}: {registered} novos, {already} já cadastrados."
            )
            return {
                "guild_created": guild_created,
                "registered": registered,
                "already": already,
                "total": total,
            }
