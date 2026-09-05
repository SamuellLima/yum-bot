import discord
from discord import app_commands
from discord.ext import commands

from App.services.roles import RolesManager
from App.utils.print import Print


def _emoji_key(emoji: discord.PartialEmoji | discord.Emoji) -> str:
    if emoji.id is None:
        return str(emoji)
    if emoji.animated:
        return f"<a:{emoji.name}:{emoji.id}>"
    return f"<:{emoji.name}:{emoji.id}>"


class Roles(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.roles = RolesManager()

    @commands.hybrid_command(
        name="sjoin_role",
        description="Define o cargo dado automaticamente quando alguém entra no servidor.",
    )
    @commands.has_guild_permissions(manage_guild=True, manage_roles=True)
    @commands.guild_only()
    @app_commands.guild_only()
    @app_commands.describe(role="Cargo dado na entrada do servidor")
    @app_commands.default_permissions(manage_guild=True)
    async def sjoin_role(self, ctx: commands.Context, role: discord.Role):
        if ctx.guild is None:
            await ctx.reply("Esse comando só funciona em um servidor.")
            return

        me = ctx.guild.me
        if me is None or role >= me.top_role:
            await ctx.reply("Não consigo gerenciar esse cargo. Ele precisa ficar abaixo do meu.")
            return
        if role.is_default() or role.managed:
            await ctx.reply("Esse cargo não pode ser usado como cargo de entrada.")
            return

        await self.roles.set_join_role(ctx.guild.id, role.id)
        await ctx.reply(f"Cargo {role.mention} definido como cargo de entrada.")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        join_role_id = await self.roles.get_join_role(member.guild.id)
        if join_role_id is None:
            return

        join_role = member.guild.get_role(int(join_role_id))
        if join_role is None:
            Print.info(f"Cargo de entrada não encontrado no servidor {member.guild.id}")
            return

        try:
            await member.add_roles(join_role, reason="Cargo de entrada")
        except discord.Forbidden:
            Print.error(f"Sem permissão para dar {join_role.name} em {member.guild.id}")

    @commands.hybrid_command(
        name="set_roles_message",
        description="Define the message for the roles select panel",
    )
    @app_commands.guild_only()
    @app_commands.describe(message="The message for the roles select panel")
    @app_commands.default_permissions(manage_guild=True)
    async def set_roles_message(self, ctx: commands.Context, *, message: str | None = None):
        """Define the message for the roles select panel"""
        if ctx.guild is None:
            await ctx.reply("Esse comando só funciona em um servidor.")
            return
        await self.roles.set_roles_select_message(ctx.guild.id, message)
        if message and message.strip():
            await ctx.reply("Mensagem do painel de comunidades atualizada.")
        else:
            await ctx.reply("Mensagem do painel voltou ao texto padrão.")

    @commands.hybrid_command(
        name="set_roles_title",
        description="Define o título do painel de comunidades. Sem texto, usa o padrão.",
    )
    @commands.has_guild_permissions(manage_guild=True)
    @commands.guild_only()
    @app_commands.guild_only()
    @app_commands.describe(title="Título do embed. Deixe vazio para voltar ao padrão.")
    @app_commands.default_permissions(manage_guild=True)
    async def set_roles_title(self, ctx: commands.Context, *, title: str | None = None):
        if ctx.guild is None:
            await ctx.reply("Esse comando só funciona em um servidor.")
            return
        await self.roles.set_roles_select_title(ctx.guild.id, title)
        if title and title.strip():
            await ctx.reply("Título do painel de comunidades atualizado.")
        else:
            await ctx.reply("Título do painel voltou ao padrão.")

    @commands.hybrid_command(
        name="set_role_emoji",
        description="Associa um emoji a um cargo. Quem reagir no painel recebe o cargo.",
    )
    @commands.has_guild_permissions(manage_guild=True, manage_roles=True)
    @commands.guild_only()
    @app_commands.guild_only()
    @app_commands.describe(role="Cargo que o membro recebe ao reagir", emoji="Emoji da reação")
    @app_commands.default_permissions(manage_guild=True)
    async def set_role_emoji(self, ctx: commands.Context, role: discord.Role, emoji: str):
        if ctx.guild is None:
            await ctx.reply("Esse comando só funciona em um servidor.")
            return

        me = ctx.guild.me
        if me is None or role >= me.top_role:
            await ctx.reply("Não consigo gerenciar esse cargo. Ele precisa ficar abaixo do meu.")
            return
        if role.is_default() or role.managed:
            await ctx.reply("Esse cargo não pode ser usado no painel.")
            return

        try:
            parsed = discord.PartialEmoji.from_str(emoji.strip())
        except ValueError:
            parsed = discord.PartialEmoji(name=emoji.strip())

        key = _emoji_key(parsed)
        await self.roles.set_role_reaction(ctx.guild.id, key, role.id)
        await ctx.reply(f"{key} agora dá o cargo {role.mention}.")

    @commands.hybrid_command(
        name="unset_role_emoji",
        description="Remove a associação de um emoji com cargo.",
    )
    @commands.has_guild_permissions(manage_guild=True)
    @commands.guild_only()
    @app_commands.guild_only()
    @app_commands.describe(emoji="Emoji a desvincular")
    @app_commands.default_permissions(manage_guild=True)
    async def unset_role_emoji(self, ctx: commands.Context, emoji: str):
        if ctx.guild is None:
            await ctx.reply("Esse comando só funciona em um servidor.")
            return

        try:
            parsed = discord.PartialEmoji.from_str(emoji.strip())
            key = _emoji_key(parsed)
        except ValueError:
            key = emoji.strip()

        removed = await self.roles.remove_role_reaction(ctx.guild.id, key)
        if not removed:
            await ctx.reply("Esse emoji não estava associado a nenhum cargo.")
            return
        await ctx.reply("Associação removida.")

    @commands.hybrid_command(
        name="post_roles",
        description="Publica o painel de comunidades neste canal e adiciona as reações.",
    )
    @commands.has_guild_permissions(manage_guild=True)
    @commands.guild_only()
    @app_commands.guild_only()
    @app_commands.default_permissions(manage_guild=True)
    async def post_roles(self, ctx: commands.Context):
        if ctx.guild is None:
            await ctx.reply("Esse comando só funciona em um servidor.")
            return
        if not isinstance(ctx.channel, discord.TextChannel):
            await ctx.reply("Usa isso num canal de texto.")
            return

        if ctx.interaction is not None:
            await ctx.defer(ephemeral=True)

        mappings = await self.roles.list_role_reactions(ctx.guild.id)
        if not mappings:
            await ctx.send(
                "Primeiro associa emojis aos cargos com `/set_role_emoji`.",
                ephemeral=ctx.interaction is not None,
            )
            return

        title = await self.roles.get_roles_select_title(ctx.guild.id)
        intro = await self.roles.get_roles_select_message(ctx.guild.id)
        lines = [intro, ""]
        for item in mappings:
            role = ctx.guild.get_role(int(item["role_id"]))
            label = role.mention if role else f"<@&{item['role_id']}>"
            lines.append(f"{item['emoji']} {label}")

        embed = discord.Embed(
            title=title,
            description="\n".join(lines),
            color=discord.Color.from_rgb(255, 120, 160),
        )
        panel = await ctx.channel.send(embed=embed)
        for item in mappings:
            await panel.add_reaction(item["emoji"])

        await self.roles.set_roles_select_panel(ctx.guild.id, ctx.channel.id, panel.id)
        await ctx.send(
            "Painel publicado. Os membros reagem para entrar na comunidade.",
            ephemeral=ctx.interaction is not None,
        )

    async def _toggle_role(self, payload: discord.RawReactionActionEvent, add: bool) -> None:
        if payload.guild_id is None or self.bot.user is None:
            return
        if payload.user_id == self.bot.user.id:
            return

        channel_id, message_id = await self.roles.get_roles_select_panel(payload.guild_id)
        if not channel_id or not message_id:
            return
        if str(payload.channel_id) != channel_id or str(payload.message_id) != message_id:
            return

        role_id = await self.roles.get_role_id_for_emoji(
            payload.guild_id, _emoji_key(payload.emoji)
        )
        if role_id is None:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if guild is None:
            return
        role = guild.get_role(int(role_id))
        member = guild.get_member(payload.user_id) or await guild.fetch_member(payload.user_id)
        if role is None or member is None or member.bot:
            return

        try:
            if add:
                await member.add_roles(role, reason="Painel de comunidades")
            else:
                await member.remove_roles(role, reason="Painel de comunidades")
        except discord.Forbidden:
            return

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent) -> None:
        await self._toggle_role(payload, add=True)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent) -> None:
        await self._toggle_role(payload, add=False)

    @commands.hybrid_command(
        name="rhelp",
        description="Mostra o que cada comando de cargos faz.",
    )
    @app_commands.guild_only()
    @app_commands.default_permissions(manage_guild=True)
    async def rhelp(self, ctx: commands.Context):
        embed = discord.Embed(
            title="Quer ajuda com os cargos? 💞",
            description=(
                "todos os comandos funcionam com **/** ou **!**\n"
                "ex: `/post_roles` e `!post_roles` são a mesma coisa\n"
                "somente quem gerencia o servidor consegue usar estes"
            ),
            color=discord.Color.from_rgb(255, 120, 160),
        )
        embed.add_field(
            name="🍪  Entrada",
            value=(
                "`/sjoin_role` `[cargo]` - cargo dado automaticamente quando alguém entra no servidor"
            ),
            inline=False,
        )
        embed.add_field(
            name="✨  Painel de comunidades",
            value=(
                "`/set_roles_title` `[título]` - título que você quer que apareça no embed.\n"
                "`/set_roles_message` `[mensagem]` - texto que você quer que apareça no painel.\n"
                "`/set_role_emoji` `[cargo]` `[emoji]` - serve para associar um emoji a um cargo, quem reagir com esse emoji recebe o cargo.\n"
                "`/unset_role_emoji` `[emoji]` - remove a associação emoji ↔ cargo.\n"
                "`/post_roles` - publica o painel no canal em que usar o comando e adiciona as reações."
            ),
            inline=False,
        )
        embed.add_field(
            name="💞  Ajuda",
            value="`/rhelp` - este traz a mensagem que você está vendo agora.",
            inline=False,
        )
        embed.set_footer(text="É isso, tenha um ótimo dia! 💕")
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Roles(bot))
