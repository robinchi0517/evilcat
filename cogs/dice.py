import discord, random, re
from discord.ext import commands

# 定義名為 DiceRoller 的 Cog
class DiceRoller(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # 基本骰def：XdY、XdY+Z、XdY+Z>=T
    def parse_dice_input(self, user_input):
        match = re.match(r"^(\d*)d(\d+)(?:([+-]\d+))?(?:(>=|<=|>|<)(\d+))?(?:\s+(.*))?$", user_input)
        if match:
            try:
                dice_a_str = match.group(1)
                dice_b = int(match.group(2))
                bonus_str = match.group(3)
                operator = match.group(4)
                target_str = match.group(5)
                description = match.group(6)
                dice_a = int(dice_a_str) if dice_a_str else 1
                bonus = int(bonus_str) if bonus_str else 0
                target = int(target_str) if target_str else None

                rolls = [random.randint(1, dice_b) for _ in range(dice_a)]
                total = sum(rolls) + bonus

                dice_formula = f"🎲 {dice_a}d{dice_b}"
                if bonus > 0:
                    dice_formula += f"+{bonus}"
                elif bonus < 0:
                    dice_formula += f"{bonus}"
                dice_result = f"{dice_formula} = {rolls}"
                if bonus != 0:
                    dice_result += f" {'+' if bonus > 0 else '-'} {abs(bonus)}"
                dice_result += f" = {total}"

                if operator and target is not None:
                    success = False
                    if operator == '>=':
                        success = total >= target
                    elif operator == '>':
                        success = total > target
                    elif operator == '<=':
                        success = total <= target
                    elif operator == '<':
                        success = total < target
                    dice_result += f" {operator}{target} → {'✔️成功' if success else '❌失敗'}"
                if description:
                    dice_result += f" 🏷️ {description.strip()}"
                return dice_result
            except ValueError as ve:
                print("parse_dice_input發生錯誤：%s" %(ve))
                return

    # 關鍵字觸發
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # print(f"[DEBUG] {message.content}")  # 這是測試用的 log

        if message.author == self.bot.user:
            return
        
        if message.content == "喵":
            await message.channel.send("喵？")

        if re.match(r"^\d*d\d+", message.content):  # 快速篩選可能是擲骰指令的訊息
            # print("🎯 擲骰指令被偵測到了！")
            response = self.parse_dice_input(message.content.strip().lower())
            await message.channel.send(response)

# Cog 載入 Bot 中
async def setup(bot: commands.Bot):
    await bot.add_cog(DiceRoller(bot))