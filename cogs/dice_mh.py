import discord, random, re
from discord.ext import commands

# 定義所有行動的別名與回應內容
MH_ACTIONS = {
    "turn_on": {
        "aliases": ["引起悸動", "撩", "turnon", "turn"],
        "responses": [
            "獲得1條心弦，對方從以下反應擇一：\n✦ 我獻出自己。\n✦ 我向你承諾我認為你想要的。\n✦ 我感到心慌意亂且表現的手足無措。",
            "對方從以下反應擇一：\n✦ 我獻出自己。\n✦ 我向你承諾我認為你想要的。\n✦ 我感到心慌意亂且表現的手足無措。",
        ]
    },
    "shut_down": {
        "aliases": ["使人難堪", "洗", "shutdown", "shut"],
        "responses": [
            "從以下結果擇一：\n✦ 他失去1條你的心弦。\n✦ 如果他沒有你的心弦，你獲得1條他的心弦。\n✦ 他陷入1種處境。\n✦ 你獲得1點推進。",
            "你遭受1種處境，並以下結果擇一：\n✦ 他失去1條你的心弦。\n✦ 如果他沒有你的心弦，你獲得1條他的心弦。\n✦ 他陷入1種處境。\n✦ 你獲得1點推進。",
        ]
    },
    "keep_cool": {
        "aliases": ["保持冷靜", "冷靜", "keepcool", "keep"],
        "responses": [
            "向MC問一個關於當下的問題並就這個資訊獲得1點推進。",
            "MC將告訴你此行動可能遭受的危險，你可選擇退縮或繼續前進。",
        ]
    },
    "lash_out": {
        "aliases": ["肢體衝突", "衝突", "lashout", "lash"],
        "responses": [
            "你對他造成傷害，他將暫時哽住並失去反應能力。",
            "你對他造成傷害，但從以下結果擇一：\n✦ 他了解了你真實的本性並取得1條你的心弦。\n✦ 由MC決定傷害的嚴重程度。\n✦ 你陷入黑暗面。",
        ]
    },
    "run_away": {
        "aliases": ["逃跑", "逃走", "runaway", "run"],
        "responses": [
            "你逃到安全的地方。",
            "你逃走了，但從以下擇一：\n✦ 你遇到更糟糕的情況。\n✦ 你把場面鬧得很大。\n✦ 你遺漏了某個東西。",
        ]
    },
    "gaze_abyss": {
        "aliases": ["凝視深淵", "深淵", "gazeinto", "gazein", "gaze", "abyss"],
        "responses": [
            "深淵向你展示了清晰的願景，你在相對的應對上獲得1點推進。",
            "深淵向你展示了令人困惑和驚恐的景象，儘管如此你仍得到答案。",
        ]
    },
}

def monster_heart_roll(name: str, v: int, responses: list[str], description: str = ""):
    rolls = [random.randint(1, 6) for _ in range(2)]
    total = sum(rolls) + v

    formula = f"🎲 {name}"
    if v > 0:
        formula += f"+{v}"
    elif v < 0:
        formula += f"{v}"
    result = f"{formula} = {rolls}"
    if v != 0:
        result += f" {'+' if v > 0 else '-'} {abs(v)}"
    result += f" → {total}"

    if total >= 10:
        result += f"\n💬 大成功！{responses[0]}"
    elif total >= 7:
        result += f"\n💬 成功！{responses[1]}"
    else:
        result += f"\n💬 失敗，MC進行反應。"

    if description:
        result += f"\n🏷️ {description.strip()}"

    return result

# 定義名為 DiceMH 的 Cog
class DiceMH(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 關鍵字觸發
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):

        if message.author == self.bot.user:
            return

        for action_data in MH_ACTIONS.values():
            # print(f"[DEBUG] MH骰第一層：MH_ACTIONS判斷")
            for alias in action_data["aliases"]:
                # print(f"[DEBUG] MH骰第二層：alias → {alias}")
                if message.content.lower().startswith(alias.lower()):
                    # 嘗試解析修正值與說明
                    # print(f"[DEBUG] MH骰第三層：解析值跟說明")
                    match = re.match(rf"^{re.escape(alias)}(?:\s+([+-]?\d+(?:[+-]\d+)*))?(?:\s+(.*))?$", message.content.strip(), re.IGNORECASE)

                    if match:
                        modifier_str = match.group(1) or ""
                        description = match.group(2) or ""
                        modifier = sum(map(int, re.findall(r"[+-]?\d+", modifier_str)))
                        result = monster_heart_roll(alias, modifier, action_data["responses"], description)
                        await message.channel.send(result)
                        return

# Cog 載入 Bot 中
async def setup(bot: commands.Bot):
    await bot.add_cog(DiceMH(bot))
