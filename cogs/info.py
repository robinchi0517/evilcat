import discord
from discord.ext import commands
from discord import app_commands

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="info", description="查看可用指令與功能說明")
    async def info(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            content="📘 點擊查看黛西的指令說明頁：\nhttps://evilcat.onrender.com/", 
            ephemeral=True
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(Info(bot))