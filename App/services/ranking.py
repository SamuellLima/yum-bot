from sqlalchemy import select
from sqlalchemy.orm import Session

from App.database.models import GuildSettings, Users
from App.database.session import get_db
from App.utils.print import Print


class RankingManager:
    """Gerencia o ranking de XP dos usuários."""

    def _verify_user(
        self, db: Session, server_id: int, user_id: int, username: str = ""
    ) -> Users | None:
        guild = db.scalars(
            select(GuildSettings).where(GuildSettings.guild_id == str(server_id))
        ).first()
        if guild is None:
            return None

        user = db.scalars(
            select(Users).where(
                Users.user_id == str(user_id),
                Users.guild_settings_id == guild.id,
            )
        ).first()
        if user:
            return user

        user = Users(
            user_id=str(user_id),
            username=username[:100] if username else "",
            xp=0,
            guild_settings_id=guild.id,
        )
        db.add(user)
        db.flush()
        Print.info(f"Usuário {user_id} adicionado ao banco de dados.")
        return user

    async def ensure_user(self, server_id: int, user_id: int, username: str = "") -> None:
        with get_db() as db:
            self._verify_user(db, server_id, user_id, username)

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
                select(GuildSettings.guild_id, Users.user_id, Users.username, Users.xp)
                .join(GuildSettings)
                .order_by(Users.xp.desc())
                .limit(limit)
            ).all()
            return [
                {"guild_id": row[0], "id": row[1], "name": row[2], "xp": row[3]} for row in rows
            ]

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
            if user.count_messages >= 100:
                user.xp += 1
                user.count_messages = 0
            return user.count_messages

    async def add_voice_minutes(self, server_id: int, user_id: int, minutes: int) -> None:
        with get_db() as db:
            user = self._verify_user(db, server_id, user_id)
            if user is None:
                return
            user.count_voice_minutes += minutes
