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

    @commands.hybrid_command(name="profile", description="Mostra o perfil de um usuário.")
    @commands.guild_only()
    @app_commands.guild_only()
    @app_commands.describe(user="O usuário para ver o perfil.")
    async def profile(self, ctx: commands.Context, user: discord.Member | None = None):
        if ctx.guild is None:
            await ctx.reply("Esse comando só funciona em um servidor.")
            return

        target = user or ctx.author
        stats = await self.ranking_manager.get_profile(ctx.guild.id, target.id)
        if stats is None:
            await ctx.reply("Ainda não há um perfil para este servidor.")
            return

        embed = discord.Embed(
            title=f"Perfil de {target.display_name}",
            color=discord.Color.from_rgb(255, 120, 160),
        )
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.set_author(
            name=str(target),
            icon_url=target.display_avatar.url,
        )
        embed.add_field(name=f"🧪  XP · **{stats['xp']}**", value="", inline=False)
        embed.add_field(
            name="🏆  Progressão",
            value=(
                f"Rank local  ·  **#{stats['rank_local']}**\n"
                f"Rank global  ·  **#{stats['rank_global']}**"
            ),
            inline=False,
        )
        embed.add_field(
            name="📚  Estudos",
            value="Exercícios resolvidos  ·  **0**",
            inline=False,
        )
        embed.add_field(
            name="🍪  Presença",
            value=(
                f"Mensagens  ·  **{stats['total_messages']}**\n"
                f"Tempo em call  ·  **{_format_voice_time(stats['voice_minutes'])}**"
            ),
            inline=False,
        )
        embed.set_footer(text=f"{ctx.guild.name}  ·  ID {target.id}")
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(User(bot))
