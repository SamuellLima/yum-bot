import os

import discord
from App.database.session import dispose_engine
from App.utils.print import Print
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("YUM_BOT_TOKEN")

intents = discord.Intents.all()


class YumBot(commands.Bot):
    async def setup_hook(self) -> None:
        for file in os.listdir("App/cogs"):
            if file.endswith(".py") and not file.startswith("_"):
                await self.load_extension(f"App.cogs.{file[:-3]}")
                Print.success(f"Loaded cog: {file[:-3]}")
        Print.success("Cogs loaded")
        synced = await self.tree.sync()
        Print.success(f"Slash commands sincronizados: {len(synced)}")

    async def close(self) -> None:
        await dispose_engine()
        await super().close()


bot = YumBot(command_prefix="!", intents=intents, help_command=None)


# for testing purposes
@bot.hybrid_command(name="ping", description="Responde com Pong!")
async def ping(ctx: commands.Context):
    await ctx.reply("Pong!")


@bot.event
async def on_ready():
    if getattr(bot, "_synced_guild_commands", False):
        return
    bot._synced_guild_commands = True

    for guild in bot.guilds:
        bot.tree.copy_global_to(guild=guild)
        await bot.tree.sync(guild=guild)
        Print.success(f"Slash commands atualizados em {guild.name}")


bot.run(TOKEN)
