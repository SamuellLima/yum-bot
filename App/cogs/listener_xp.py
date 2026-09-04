import discord
from discord.ext import commands, tasks

from App.services.ranking import RankingManager
from App.utils.print import Print


class XP(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.ranking = RankingManager()
        self.voice_xp_loop.start()

    def cog_unload(self) -> None:
        self.voice_xp_loop.cancel()

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

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ) -> None:
        if member.bot or member.guild is None:
            return

        if before.channel is None and after.channel is not None:
            await self.ranking.ensure_user(member.guild.id, member.id, member.display_name)

    @tasks.loop(minutes=1)
    async def voice_xp_loop(self) -> None:
        for guild in self.bot.guilds:
            for voice_channel in guild.voice_channels:
                for member in voice_channel.members:
                    if not member.bot:
                        xp_gained = await self.ranking.add_voice_minutes(guild.id, member.id, 1)
                        if xp_gained:
                            Print.success(
                                f"User {member.id} recebeu {xp_gained} XP por tempo em call"
                            )

    @voice_xp_loop.before_loop
    async def before_voice_xp_loop(self) -> None:
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    await bot.add_cog(XP(bot))
