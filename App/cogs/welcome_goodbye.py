import discord
from discord.ext import commands

from App.services.servers_config import ServersConfigManager


class WelcomeGoodbye(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command()
    async def set_welcome_goodbye_channel(
        self, ctx: commands.Context, channel: discord.TextChannel | None = None
    ):
        if channel is None:
            await ctx.reply(
                "Informe o canal (menção ou ID). Exemplo: `!set_welcome_goodbye_channel #geral`"
            )
            return

        if ctx.guild is None:
            await ctx.reply("Esse comando só funciona em um servidor.")
            return

        await ServersConfigManager().set_welcome_channel_id(ctx.guild.id, channel.id)
        await ctx.reply(f"Canal de welcome/goodbye definido para {channel.mention}")

    async def _welcome_channel(self, guild: discord.Guild) -> discord.TextChannel | None:
        channel_id = await ServersConfigManager().get_welcome_channel_id(guild.id)
        if not channel_id:
            return None
        channel = guild.get_channel(int(channel_id)) or self.bot.get_channel(int(channel_id))
        return channel if isinstance(channel, discord.TextChannel) else None

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        channel = await self._welcome_channel(member.guild)
        if channel is None:
            return

        welcome_message = await ServersConfigManager().get_welcome_message(member.guild.id)
        if welcome_message:
            await channel.send(welcome_message.replace("{member}", member.mention))
        else:
            await channel.send(f"Welcome {member.mention} to the server! 💞")

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        channel = await self._welcome_channel(member.guild)
        if channel is None:
            return

        await channel.send(f"Goodbye {member.mention} from the server! 💔")


async def setup(bot: commands.Bot):
    await bot.add_cog(WelcomeGoodbye(bot))
