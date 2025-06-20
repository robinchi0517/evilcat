import os, asyncio, discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True  # 開啟讀取訊息內容權限
bot = commands.Bot(command_prefix="", intents=intents)

@bot.event
async def on_ready():
    print(f"🐱 黛西已上線：{bot.user}")
    print("✔️ 斜線指令同步中...")
    await bot.tree.sync()
    print("✔️ 載入完成！")

async def load_extensions():
    cogs_path = os.path.join(os.path.dirname(__file__), "cogs")
    if not os.path.exists(cogs_path):
        print("❌ 找不到 cogs 資料夾，請確認結構是否正確。")
        return

    for filename in os.listdir(cogs_path):
        if filename.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"✔️ 已載入模組：{filename}")
            except Exception as e:
                print(f"❌ 載入 {filename} 失敗：{e}")

async def main():
    async with bot:
        await load_extensions()
        await bot.start("MTM0MTAxODYyNjI5MTEzODU5Mg.GJIwaI.X-FQD4UvgFPF-LUlp4oHHOvzqshTcIJcbn8pTk")

if __name__ == "__main__":
    asyncio.run(main())
