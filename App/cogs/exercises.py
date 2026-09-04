# TODO: Exercises cog in development wait for AI models to be ready

import discord
from discord import app_commands
from discord.ext import commands

class Exercises(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="exercises", description="Mostra informações sobre os exercícios.")
    async def exercises(self, ctx: commands.Context):
        await ctx.send(f"A funcionalidade de exercícios está em desenvolvimento 🐞, {ctx.author.mention}... Espere mais um pouco por favor! 💞")

async def setup(bot: commands.Bot):
    await bot.add_cog(Exercises(bot))