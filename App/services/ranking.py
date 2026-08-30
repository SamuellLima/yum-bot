from sqlalchemy import select

from App.database.models import GuildSettings, Users
from App.database.session import get_db


class RankingManager:
    """Gerencia o ranking de XP dos usuários."""

    async def add_xp(self, server_id: int, user_id: int, xp: int) -> None:
        with get_db() as db:
            user = db.scalars(select(Users).where(Users.user_id == str(user_id))).first()
            if user:
                user.xp += xp
                return

            guild = db.scalars(
                select(GuildSettings).where(GuildSettings.guild_id == str(server_id))
            ).first()
            if guild is None:
                return

            db.add(
                Users(
                    user_id=str(user_id),
                    username="",
                    xp=xp,
                    guild_settings_id=guild.id,
                )
            )

    async def remove_xp(self, server_id: int, user_id: int, xp: int) -> None:
        with get_db() as db:
            user = db.scalars(select(Users).where(Users.user_id == str(user_id))).first()
            if user:
                user.xp = max(0, user.xp - xp)

    async def get_global_ranking(self, limit: int = 10) -> list[dict]:
        with get_db() as db:
            rows = db.execute(
                select(Users.user_id, Users.username, Users.xp)
                .order_by(Users.xp.desc())
                .limit(limit)
            ).all()
            return [{"id": row[0], "name": row[1], "xp": row[2]} for row in rows]

    async def get_server_ranking(self, server_id: int, limit: int = 10) -> list[dict]:
        with get_db() as db:
            rows = db.execute(
                select(Users.user_id, Users.username, Users.xp)
                .join(GuildSettings)
                .where(GuildSettings.guild_id == str(server_id))
                .order_by(Users.xp.desc())
                .limit(limit)
            ).all()
            return [{"id": row[0], "name": row[1], "xp": row[2]} for row in rows]
