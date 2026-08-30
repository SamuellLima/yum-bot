import os

import discord
from App.database.session import dispose_engine
from App.utils.print import Print
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("YUM_BOT_TOKEN")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)


# for testing purposes
@bot.command()
async def ping(ctx: commands.Context):
    await ctx.reply("Pong!")


async def carry_cogs():
    for file in os.listdir("App/cogs"):
        if file.endswith(".py") and not file.startswith("_"):
            await bot.load_extension(f"App.cogs.{file[:-3]}")
            Print.success(f"Loaded cog: {file[:-3]}")


@bot.event
async def setup_hook():
    await carry_cogs()
    Print.success("Cogs loaded")


try:
    bot.run(TOKEN)
finally:
    dispose_engine()
