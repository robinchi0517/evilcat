import discord
from discord.ext import commands
from discord import app_commands

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="info", description="查看可用指令與功能說明")
    async def info(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="MyLittleMonster TRPG《怪物心》小助手",
            description="🐱 以下是目前可使用的斜線功能與指令喵。",
            color=discord.Color.purple()
        )
        embed.add_field(
            name="/info",
            value="顯示這個說明畫面！",
            inline=False
        )
        embed.add_field(
            name=" `/skins` ",
            value="檢視《怪物心》的模板資料。",
            inline=False
        )
        embed.add_field(
            name=" `/build_mh` ",
            value="開始建立一個可以貼到ccfolia房間使用的《怪物心》角色卡，建議先看過模板資料再來使用。",
            inline=False
        )
        embed.add_field(
            name=" `XdY+N>=T 備註` ",
            value="基本擲骰指令，直接於頻道內輸入即可進行XdY擲骰，可以加減值、設定目標跟做備註。",
            inline=False
        )
        embed.add_field(
            name=" `!pool XdY>=T` ",
            value="骰池指令，進行XdY擲骰後個別顯示結果，可以設定目標，會特別標示符合目標的骰子。",
            inline=False
        )
        embed.add_field(
            name=" `!reroll XdY>=T` 、 `!rr XdY>=T` ",
            value="重骰指令，進行XdY擲骰後，符合目標的骰子進行重骰，最多重骰10次（不然會爆掉）。",
            inline=False
        )
        embed.add_field(
            name=" `!keep XdY` 、 `!keepT XdY` ",
            value="取高/低指令，keep、kh取高，kl取低，可指定要取幾顆，未指定的話取一顆。",
            inline=False
        )
        embed.add_field(
            name=" `!drop XdY` 、 `!dropT XdY` ",
            value="去高/低指令，dh去高，drop、dl去低，可指定要去幾顆，未指定的話去一顆。",
            inline=False
        )
        embed.add_field(
            name=" `!build XdY*N` 、 `!build keep XdY*N` ",
            value="創角骰，骰N組XdY，可搭配keep、kh使用。",
            inline=False
        )
        embed.set_footer(text="有問題可以向製作者提出反饋！")

        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Info(bot))