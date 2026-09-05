import contextlib

import discord
from discord import app_commands
from discord.ext import commands

from App.services.servers_config import ServersConfigManager


class Setup(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.servers = ServersConfigManager()

    @commands.hybrid_command(
        name="setup",
        description="Cadastra o servidor e todos os membros no banco do bot.",
    )
    @commands.has_guild_permissions(manage_guild=True)
    @commands.guild_only()
    @app_commands.guild_only()
    @app_commands.default_permissions(manage_guild=True)
    async def setup_server(self, ctx: commands.Context):
        if ctx.guild is None:
            await ctx.reply("Esse comando só funciona em um servidor.")
            return

        await ctx.defer()

        guild = ctx.guild
        if guild.member_count and len(guild.members) < guild.member_count:
            with contextlib.suppress(discord.HTTPException):
                await guild.chunk()

        humans = [member for member in guild.members if not member.bot]
        bots_skipped = sum(1 for member in guild.members if member.bot)
        incomplete = bool(guild.member_count and len(guild.members) < guild.member_count)

        result = await self.servers.bootstrap_guild(
            guild.id,
            [(str(member.id), member.name) for member in humans],
        )

        guild_status = (
            "acabei de cadastrar este servidor"
            if result["guild_created"]
            else "este servidor já estava no banco"
        )
        if result["registered"]:
            members_value = (
                f"**{result['registered']}** pessoas novas no banco\n"
                f"**{result['already']}** já tinham perfil (XP intacto)"
            )
        elif humans:
            members_value = f"todo mundo já estava cadastrado · **{result['already']}** perfis"
        else:
            members_value = "não achei nenhum membro humano para cadastrar"

        embed = discord.Embed(
            title="Servidor pronto! 💞",
            description=(
                f"**{guild.name}** agora está no banco, com o pessoal daqui.\n"
                "quem entrar depois também é cadastrado sozinho."
            ),
            color=discord.Color.from_rgb(255, 120, 160),
        )
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        embed.add_field(name="🏠  Servidor", value=guild_status, inline=False)
        embed.add_field(name="👤  Membros", value=members_value, inline=False)
        embed.add_field(
            name="🤖  Bots",
            value=f"ignorei **{bots_skipped}** (eles não entram no ranking)",
            inline=False,
        )
        if incomplete:
            embed.add_field(
                name="⚠️  Cache",
                value=(
                    f"o Discord me mostrou **{len(guild.members)}** de "
                    f"**{guild.member_count}** membros. "
                    "liga a intent de Server Members no portal do bot e roda de novo."
                ),
                inline=False,
            )
        embed.set_footer(text=f"{guild.name}  ·  {result['total']} perfis no banco  ·  💕")
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Setup(bot))
