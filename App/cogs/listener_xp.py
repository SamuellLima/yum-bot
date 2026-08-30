import discord
from discord.ext import commands

from App.services.ranking import RankingManager
from App.utils.print import Print


class XP(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.ranking = RankingManager()

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
                "Você interagiu o suficiente com o servidor para receber XP! 🎁 Bom garoto(a)! Continue assim! 💞"
            )

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ) -> None:
        Print.info("in development")
        return


async def setup(bot: commands.Bot):
    await bot.add_cog(XP(bot))
