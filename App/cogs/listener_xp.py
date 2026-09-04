from datetime import UTC, datetime

import discord
from discord.ext import commands

from App.services.ranking import RankingManager
from App.utils.print import Print


class XP(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.ranking = RankingManager()
        self._voice_joined_at: dict[tuple[int, int], datetime] = {}
        self._voice_seeded = False

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        if self._voice_seeded:
            return
        self._voice_seeded = True

        now = datetime.now(UTC)
        for guild in self.bot.guilds:
            for member in guild.members:
                if member.bot or member.voice is None or member.voice.channel is None:
                    continue
                self._voice_joined_at.setdefault((guild.id, member.id), now)

    @commands.Cog.listener()
    async def on_message(self, data: discord.Message) -> None:
        if data.author.bot or data.guild is None:
            return

        message_count = await self.ranking.add_message_count(data.guild.id, data.author.id)
        Print.success(f"Message count added for user {data.author.id}")

        if message_count >= 100:
            Print.success(f"User {data.author.id} sent 20 messages, adding 1 XP")
            await self.ranking.get_message_count(data.guild.id, data.author.id)
            await data.channel.send(
                "Você interagiu o suficiente com o servidor para receber XP! 🎁 "
                "Bom garoto(a)! Continue assim! 💞"
            )

    async def _flush_voice_time(self, guild_id: int, user_id: int) -> None:
        started = self._voice_joined_at.pop((guild_id, user_id), None)
        if started is None:
            return
        minutes = int((datetime.now(UTC) - started).total_seconds() // 60)
        if minutes <= 0:
            return
        await self.ranking.add_voice_minutes(guild_id, user_id, minutes)

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ) -> None:
        if member.bot or member.guild is None:
            return

        key = (member.guild.id, member.id)
        was_in = before.channel is not None
        now_in = after.channel is not None

        if now_in and not was_in:
            self._voice_joined_at[key] = datetime.now(UTC)
        elif was_in and not now_in:
            await self._flush_voice_time(member.guild.id, member.id)


async def setup(bot: commands.Bot):
    await bot.add_cog(XP(bot))
