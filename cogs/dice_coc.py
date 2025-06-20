import discord, random, re
from discord.ext import commands

def handle_cc_command(content: str) -> str:
    pattern = r"^!cc\s+(\d+)$"
    match = re.match(pattern, content.strip(), re.IGNORECASE)
    if not match:
        return "⚠️ 是想要做CoC判定嗎？請用 `!cc 80` 喔！"
    
    target = int(match.group(1))
    rolls = random.randint(1, 100)
    result = f"🎲 CoC判定目標{target} 1d100={rolls} → "

    if rolls == 1:
        result += f"✔️大成功 Critical"
    elif rolls == 100 or (target < 50 and rolls >= 96):
        result += f"❌大失敗 Fumble"
    elif rolls > target:
        result += f"❌失敗 Failure"
    elif rolls <= target//5:
        result += f"✔️極限成功 Extreme"
    elif rolls <= target//2:
        result += f"✔️艱難成功 Hard"
    else:
        result += f"✔️一般成功 Regular"
    
    return result

def handle_growth_command(content: str) -> str:
    pattern = r"^!cc\s+([^\d\s]+)\s+(\d+)$"
    match = re.match(pattern, content.strip(), re.IGNORECASE)
    if not match:
        return "⚠️ 是想要做CoC成長判定嗎？請用 `!cc 教育 80` 的格式。"
    
    skill_name = match.group(1)
    target = int(match.group(2))
    rolls = random.randint(1, 100)

    result = f"🎲 {skill_name}成長判定目標{target} 1d100={rolls} → "

    if rolls > target or rolls == 100:
        gain = random.randint(1, 10)
        result += f"✔️成功！\n🎓 {skill_name}提升{gain}點，目前為{target+gain}點。"
    else:
        result += "❌失敗，沒有成長。"
    
    return result

def handle_sanc_command(content: str) -> str:
    pattern = r"^!(sancheck|sanc|sc)\s+(\d+)(?:\s+([0-9d]+)\/([0-9d]+))?$"
    match = re.match(pattern, content.strip(), re.IGNORECASE)
    if not match:
        return "⚠️ 是想要進行SAN CHECK嗎？請用 `!sc 60 1/1d6` 或 `!sancheck 60`喔！"
    
    san_value = int(match.group(2))
    success_loss = match.group(3)
    failure_loss = match.group(4)

    rolls = random.randint(1, 100)
    result = f"🎲 SAN CHECK (目前SAN值為{san_value}) 1d100={rolls} → "

    if rolls == 100:
        result += f"❌大失敗 Fumble"
        loss = failure_loss
    elif rolls <= san_value:
        result += f"✔️成功"
        loss = success_loss
    else:
        result += f"❌失敗"
        loss = failure_loss
    
    if loss:
        if "d" in loss:
            count, sides = map(int, loss.lower().split("d"))
            loss_value = sum(random.randint(1, sides) for _ in range(count))
            if rolls == 100:
                loss_value = int(sides)
        else:
            loss_value = int(loss)
        result += f"\n🧠 SAN 減少 {loss_value} 點"
    
        if loss_value >= 5:
            result += f"，請進行智力 (INT) 檢定！"

    return result

class DiceCOC(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        content = message.content.strip().lower()
        if content.startswith("!cc"):
            tokens = content.split()

            if len(tokens) == 2 and tokens[1].isdigit():
                response = handle_cc_command(content)
            elif len(tokens) == 3 and tokens[2].isdigit():
                response = handle_growth_command(content)
            else:
                response = "⚠️ 指令格式錯誤，請使用 `!cc 80` 或 `!cc 技能 80`。"
            
            await message.channel.send(response)
        
        elif any(content.startswith(x) for x in ["!sancheck", "!sanc", "!sc"]):
            response = handle_sanc_command(content)

            await message.channel.send(response)

async def setup(bot: commands.Bot):
    await bot.add_cog(DiceCOC(bot))