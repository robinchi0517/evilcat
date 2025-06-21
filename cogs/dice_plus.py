import discord, random, re
from discord.ext import commands

def handle_pool_command(content: str) -> str:
    pattern = r"^!pool\s+(\d+)d(\d+)(?:\s*(>=|<=|=|>|<)\s*(\d+))?$"
    match = re.match(pattern, content, re.IGNORECASE)

    if not match:
        return "⚠️ 是要用骰池嗎？請用 `!pool XdY` 或 `!pool XdY>=N` 喔！"
    
    dice_x = int(match.group(1))
    dice_y = int(match.group(2))
    operator = match.group(3)
    target = int(match.group(4)) if match.group(4) else None

    rolls = [random.randint(1, dice_y) for _ in range(dice_x)]
    marked = []
    success_count = 0

    for roll in rolls:
        if operator and target is not None:
            expr = f"{roll}{operator}{target}"
            if eval(expr):
                marked.append(f"**{roll}**")
                success_count += 1
            else:
                marked.append(str(roll))
        else:
            marked.append(str(roll))
    
    result = f"🎲 骰池 {dice_x}d{dice_y}"
    if operator:
        result += f"{operator}{target}"
    
    result += f"\n💬 結果 {', '.join(marked)}"
    if operator:
        result += f"\n🏷️ 有 {success_count} 個符合條件"
    
    return result

def handle_reroll_command(content: str, max_rounds=10) -> str:
    pattern = r"^!(reroll|rr)\s+(\d*)d(\d+)\s*(>=|<=|=|>|<)\s*(\d+)$"
    match = re.match(pattern, content.strip(), re.IGNORECASE)
    if not match:
        return "⚠️ 是要用重骰嗎？請用 `!reroll XdY>=Z` 喔！"
    
    dice_x_str = match.group(2)
    dice_y = int(match.group(3))
    operator = match.group(4)
    target = int(match.group(5))
    dice_x = int(dice_x_str) if dice_x_str else 1

    results = []
    current_dice = dice_x
    round_num = 1
    total_success = 0
    hit_limit = False

    while current_dice > 0 and round_num <= max_rounds:
        rolls = [random.randint(1, dice_y) for _ in range(current_dice)]
        marked = []
        next_dice = 0

        for roll in rolls:
            expr = f"{roll}{operator}{target}"
            if eval(expr):
                marked.append(f"**{roll}**")
                next_dice += 1
                total_success += 1
            else:
                marked.append(str(roll))
        
        results.append(f"第{round_num}輪 {', '.join(marked)}")
        current_dice = next_dice
        round_num += 1

        if round_num > max_rounds and current_dice > 0:
            hit_limit = True
    
    summary = f"🎲 重骰 {dice_x}d{dice_y}{operator}{target}\n" + "\n".join(results)
    summary += f"\n✔️ 成功 {total_success} 次"
    if hit_limit:
        summary += f"\n⚠️ 重骰達 {max_rounds} 輪，強制中止。"

    return summary

def select_dice(rolls, count, mode):
    """
    mode: keep-high, keep-low, drop-high, drop-low
    return: list of bool, True for selected, False for nonselected
    """
    if count >= len(rolls):
        return [True] * len(rolls)
    
    indexed = list(enumerate(rolls))
    reverse = mode.endswith("high")
    sorted_idx = sorted(indexed, key=lambda x: x[1], reverse=reverse)

    if mode.startswith("keep"):
        selected = set(i for i, _ in sorted_idx[:count])
    else:
        selected = set(i for i, _ in sorted_idx[count:])

    return [i in selected for i in range(len(rolls))]

def handle_select_command(content: str) -> str:
    pattern = r"^!(keep|kh|kl|drop|dh|dl)(\d*)\s+(\d*)d(\d+)$"
    match = re.match(pattern, content.strip(), re.IGNORECASE)
    if not match:
        return "⚠️ 是想要取高/低嗎？請用 `!keep2 4d10` 或 `!drop3 6d6`喔！"
    
    mode_raw = match.group(1)
    count = int(match.group(2)) if match.group(2) else 1
    dice_x = int(match.group(3)) if match.group(3) else 2
    dice_y = int(match.group(4))

    if mode_raw in ["keep", "kh"]:
        mode = "keep-high"
    elif mode_raw == "kl":
        mode = "keep-low"
    elif mode_raw == "dh":
        mode = "drop-high"
    elif mode_raw in ["drop", "dl"]:
        mode = "drop-low"
    else:
        return "❌ 無效模式"
    
    rolls = [random.randint(1, dice_y) for _ in range(dice_x)]
    selections = select_dice(rolls, count, mode)

    if mode.startswith("keep"):
        marked = [f"[{r}]" if sel else str(r) for r, sel in zip(rolls, selections)]
    else:
        marked = [f"-{r}-" if not sel else str(r) for r, sel in zip(rolls, selections)]
    
    return f"🎲 {mode} {count} in {dice_x}d{dice_y}\n💬 結果 {', '.join(marked)}"

def handle_build_command(content: str) -> str:
    pattern = r"^!build(?:\s+(keep\d*|kh\d*))?\s+(\d+)d(\d+)\*(\d+)$"
    match = re.match(pattern, content.strip(), re.IGNORECASE)
    if not match:
        return "⚠️ 是想要骰創角嗎？請用 `!build 4d6*6` 或 `!build keep3 4d6*6`喔！"

    keep_part = match.group(1)
    dice_x = int(match.group(2))
    dice_y = int(match.group(3))
    group_n = int(match.group(4))

    use_keep = False
    keep_count = dice_x - 1

    if keep_part:
        use_keep = True
        num_match = re.match(r"(keep|kh)(\d*)", keep_part)
        if num_match:
            keep_count = int(num_match.group(2)) if num_match.group(2) else dice_x - 1
        if keep_count >= dice_x:
            return f"⚠️ 每組只骰 {dice_x} 顆骰，無法保留 {keep_count} 顆骰。"
    
    results = []
    for i in range(group_n):
        rolls = [random.randint(1, dice_y) for _ in range(dice_x)]
        sorted_rolls = sorted(rolls, reverse=True)
        if use_keep:
            kept = sorted_rolls[:keep_count]
            dropped = sorted_rolls[keep_count:]
            marked = [f"[{r}]" for r in kept] + [str(r) for r in dropped]
            total = sum(kept)
        else:
            marked = [str(r) for r in rolls]
            total = sum(rolls)
        results.append(f"第{i+1}組 {', '.join(marked)} → 總和 {total}")

    title = f"🎲 創角擲骰 {group_n}組{dice_x}d{dice_y}"
    if use_keep:
        title += f"保留最高{keep_count}顆"
    
    return f"{title}\n" + "\n".join(results)

def handle_choice_command(content: str) -> str:
    pattern = re.compile(r"^!choice(\d*)\s+(.+)", re.IGNORECASE)
    match = pattern.match(content)
    if not match:
        return "⚠️ 是要選擇嗎？請用 `!choice 選項1 選項2 ...` 或 `!choiceN 選項1 選項2 ...` 喔！"
    
    num_str, options_str = match.groups()
    n = int(num_str) if num_str else 1

    raw_options = re.split(r"[,\s]+", options_str.strip())
    options = [opt for opt in raw_options if opt]

    if len(options) < n:
        return f"⚠️ 至少需要 {n+1} 個選項才能挑選 {1} 個結果。"
    
    selected = random.sample(options, n)
    
    return f"🎲 選擇結果為 {', '.join(selected)}"

class DicePLUS(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        content = message.content.strip().lower()
        if content.startswith("!pool"):
            response = handle_pool_command(content)
            await message.channel.send(response)
        elif content.startswith("!reroll") or content.startswith("!rr"):
            response = handle_reroll_command(content)
            await message.channel.send(response)
        elif any(content.startswith(x) for x in ["!keep", "!kh", "!kl", "!drop", "!dh", "!dl"]):
            response = handle_select_command(content)
            await message.channel.send(response)
        elif  content.startswith("!build"):
            response = handle_build_command(content)
            await message.channel.send(response)
        elif content.startswith("!choice"):
            response = handle_choice_command(content)
            await message.channel.send(response)

async def setup(bot: commands.Bot):
    await bot.add_cog(DicePLUS(bot))