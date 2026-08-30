from sqlalchemy import select
from sqlalchemy.orm import Session

from App.database.models import GuildSettings, Users
from App.database.session import get_db


class RankingManager:
    """Gerencia o ranking de XP dos usuários."""

    def _verify_user(self, db: Session, server_id: int, user_id: int) -> Users | None:
        user = db.scalars(select(Users).where(Users.user_id == str(user_id))).first()
        if user:
            return user

        guild = db.scalars(
            select(GuildSettings).where(GuildSettings.guild_id == str(server_id))
        ).first()
        if guild is None:
            return None

        user = Users(
            user_id=str(user_id),
            username="",
            xp=0,
            guild_settings_id=guild.id,
        )
        db.add(user)
        db.flush()
        return user

    async def add_xp(self, server_id: int, user_id: int, xp: int) -> None:
        with get_db() as db:
            user = self._verify_user(db, server_id, user_id)
            if user is None:
                return
            user.xp += xp

    async def remove_xp(self, server_id: int, user_id: int, xp: int) -> None:
        with get_db() as db:
            user = self._verify_user(db, server_id, user_id)
            if user is None:
                return
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

    async def add_message_count(self, server_id: int, user_id: int) -> int:
        with get_db() as db:
            user = self._verify_user(db, server_id, user_id)
            if user is None:
                return 0
            user.count_messages += 1
            return user.count_messages

    async def get_message_count(self, server_id: int, user_id: int) -> int:
        with get_db() as db:
            user = self._verify_user(db, server_id, user_id)
            if user is None:
                return 0
            if user.count_messages >= 20:
                user.xp += 1
                user.count_messages = 0
            return user.count_messages

    async def add_voice_minutes(self, server_id: int, user_id: int, minutes: int) -> None:
        with get_db() as db:
            user = self._verify_user(db, server_id, user_id)
            if user is None:
                return
            user.count_voice_minutes += minutes
