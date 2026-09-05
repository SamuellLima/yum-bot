import discord
from discord import app_commands
from discord.ext import commands

from App.services.ranking import RankingManager


def _format_voice_time(minutes: int) -> str:
    hours, remaining = divmod(minutes, 60)
    if hours:
        return f"{hours}h {remaining}min"
    return f"{remaining}min"


class User(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.ranking_manager = RankingManager()

    @commands.hybrid_command(name="profile", description="Mostra informações do usuário.")
    @commands.guild_only()
    @app_commands.guild_only()
    async def profile(self, ctx: commands.Context):
        if ctx.guild is None:
            await ctx.reply("Esse comando só funciona em um servidor.")
            return

        stats = await self.ranking_manager.get_profile(ctx.guild.id, ctx.author.id)
        if stats is None:
            await ctx.reply("Ainda não há um perfil para este servidor.")
            return

        embed = discord.Embed(
            title=f"{ctx.author.name}'s Profile",
            description="Aqui você pode ver as informações do seu perfil.",
            color=discord.Color.from_rgb(255, 120, 160),
        )
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        embed.set_author(name=ctx.author.name)
        embed.add_field(name="XP", value=str(stats["xp"]), inline=True)
        embed.add_field(name="Rank Global", value=f"#{stats['rank_global']}", inline=True)
        embed.add_field(name="Rank Local", value=f"#{stats['rank_local']}", inline=True)
        embed.add_field(name="Exercicios Resolvidos", value="0", inline=True)
        embed.add_field(name="Mensagens Enviadas", value=str(stats["total_messages"]), inline=True)
        embed.add_field(
            name="Tempo em Call",
            value=_format_voice_time(stats["voice_minutes"]),
            inline=True,
        )
        embed.set_footer(text=f"ID: {ctx.author.id}")
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(User(bot))
