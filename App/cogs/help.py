import discord
from discord.ext import commands


class Help(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="help", description="Mostra o que cada comando faz.")
    async def help(self, ctx: commands.Context):
        embed = discord.Embed(
            title="Precisa de ajuda? 💞",
            description=(
                "todos os comandos funcionam com **/** ou **!**\n"
                "ex: `/profile` e `!profile` são a mesma coisa"
            ),
            color=discord.Color.from_rgb(255, 120, 160),
        )
        embed.add_field(
            name="👤  Comandos para você:",
            value=(
                "`/profile` `[user]` - mostra o perfil (XP, ranks, mensagens e tempo em call). "
                "sem menção, mostra o seu; com `@alguem`, mostra o da pessoa\n"
                "`/ping` - testa se eu estou online\n"
                "`/help` - esta mensagem"
            ),
            inline=False,
        )
        embed.add_field(
            name="🏆  XP e ranking:",
            value=(
                "`/xp` - explica como ganhar XP no servidor\n"
                "`/rank` - ranking de XP deste servidor\n"
                "`/grank` - ranking de XP global 🌍"
            ),
            inline=False,
        )
        embed.add_field(
            name="📚  Estudos:",
            value="`/exercises` - exercícios do servidor (ainda em desenvolvimento 🐞)",
            inline=False,
        )
        embed.add_field(
            name="🔧  Administração:",
            value=(
                "somente quem gerencia o servidor consegue usar estes:\n"
                "`/sjoin_role` `[cargo]` - cargo dado automaticamente na entrada\n"
                "`/set_welcome_goodbye_channel` `[canal]` — canal de boas-vindas e despedida\n"
                "`/set_roles_title` `[título]` - título do painel de comunidades\n"
                "`/set_roles_message` `[mensagem]` - texto do painel de comunidades\n"
                "`/set_role_emoji` `[cargo]` `[emoji]` - reação do painel que entrega o cargo\n"
                "`/unset_role_emoji` `[emoji]` - remove a associação emoji ↔ cargo\n"
                "`/post_roles` - publica o painel de comunidades neste canal\n"
                "`/rhelp` - ajuda detalhada só dos comandos de cargos"
            ),
            inline=False,
        )
        embed.set_footer(text="É isso, tenha um ótimo dia! 💕")
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Help(bot))
