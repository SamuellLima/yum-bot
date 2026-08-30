import discord
from discord import app_commands
from discord.ext import commands

from App.services.ranking import RankingManager


class RankingXP(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.ranking_manager = RankingManager()

    @commands.hybrid_command(name="xp", description="Explica como ganhar XP e quais comandos usar.")
    async def xp(self, ctx: commands.Context):
        embed = discord.Embed(
            title="oii... quer xp?? 💞",
            description=(
                
                "para ganhar xp, voce precisa interagir com o servidor.\n"
                "\n"
                "vc sobe xp quando:\n"
                "💭 envia **mensagens** — mas tem q interagir muuuuuito com o servidor "
                "não é só mandar uma mensagem e vazar\n"
                "🎤 **call** — conversar com os amiguinhos, ficar um tempinho no canal de voz, tambem conta\n"
                "🤖 **e ate mesmo usar os bots do servidor, tambem conta\n"
                "\n"
                "basicamente, apenas exista\n"
                "eu te vejo! 💞\n"
                "\n"
                "Agora quanto aos comandos relacionados ao xp:\n"
                "`/rank` ou `!rank` → ranking deste servidor\n"
                "`/grank` ou `!grank` → ranking global 🌍\n"
                "\n"
                "é isso, tenha um otimo dia! 💕"
            ),
            color=discord.Color.from_rgb(255, 120, 160),
        )
        await ctx.send(embed=embed)

    async def _ranking_embed(
        self,
        ranking: list[dict],
        title: str,
        guild: discord.Guild | None,
    ) -> discord.Embed:
        lines: list[str] = []
        for position, entry in enumerate(ranking, start=1):
            name = entry["name"] or entry["id"]
            if guild is not None:
                member = guild.get_member(int(entry["id"]))
                if member is not None:
                    name = member.display_name
            lines.append(f"#{position} - **{name}** - {entry['xp']} XP")

        embed = discord.Embed(
            title=title,
            description="\n".join(lines),
            color=discord.Color.from_rgb(200, 40, 40),
        )

        top_id = int(ranking[0]["id"])
        top_member = guild.get_member(top_id) if guild is not None else None
        if top_member is not None:
            embed.set_thumbnail(url=top_member.display_avatar.url)
        else:
            try:
                top_user = await self.bot.fetch_user(top_id)
                embed.set_thumbnail(url=top_user.display_avatar.url)
            except discord.NotFound:
                pass

        embed.set_footer(text=f"Total de usuários: {len(ranking)}")
        return embed

    @commands.hybrid_command(name="rank", description="Mostra o ranking de XP deste servidor.")
    @commands.guild_only()
    @app_commands.guild_only()
    async def rank(self, ctx: commands.Context):
        if ctx.guild is None:
            await ctx.reply("Esse comando só funciona em um servidor.")
            return

        ranking = await self.ranking_manager.get_server_ranking(ctx.guild.id)
        if not ranking:
            await ctx.send("Ainda não há um ranking neste servidor.")
            return

        embed = await self._ranking_embed(ranking, "🏆 Ranking de XP", ctx.guild)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="grank", description="Mostra o ranking global de XP.")
    async def grank(self, ctx: commands.Context):
        ranking = await self.ranking_manager.get_global_ranking()
        if not ranking:
            await ctx.send("Ainda não há um ranking global.")
            return

        embed = await self._ranking_embed(ranking, "🏆 Ranking global de XP", ctx.guild)
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(RankingXP(bot))
