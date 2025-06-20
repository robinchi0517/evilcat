import discord, os, json
from discord.ext import commands
from discord import app_commands
from templates.rules_mh import SKIN_RULES

base_dir = os.path.dirname(__file__)
json_path = os.path.join(base_dir, "..", "data", "mhdict_skins.json")

with open(json_path, encoding="utf-8") as f:
    SKINS_DATA = json.load(f)["Skins"]

def normalize(text):
    return text.replace("\n", " ").replace("\r", " ").replace("\t", " ").strip()

def mhmove_embed(skin: dict, rule: dict, *, show_main=True, show_additional=False) -> discord.Embed:
    embed = discord.Embed(
        title=f"{normalize(skin['name'])}",
        color=discord.Color.dark_teal()
    )
    if show_main:
        if rule["fixedMoves"]:
            for move_title in rule["fixedMoves"]:
                move = next((m for m in skin["move"]["moveList"] if m["title"] == move_title), None)
                if move:
                    embed.add_field(name=f"🧷 {normalize(move['title'])}", value=move["content"], inline=False)
        
        embed.add_field(name="📚 可選模板動作", value="請依下方指示選擇指定數量動作", inline=False)
        for m in skin["move"]["moveList"]:
            if m["title"] not in rule["fixedMoves"]:
                embed.add_field(name=f"🔹 {normalize(m['title'])}", value=m["content"], inline=False)
    
    if show_additional and rule.get("allowAddMove"):
        custom_title = skin.get("moveAdd", {}).get("moveAddTitle", "附加動作")
        embed.add_field(name=f"📎 【{custom_title}】", value=f"請依下方指示選擇指定數量{custom_title}", inline=False)
        move_add_list = skin.get("moveAdd", {}).get("moveAddList", [])
        for m in move_add_list:
            embed.add_field(name=f"🔹 {normalize(m['title'])}", value=m["content"], inline=False)
    
    return embed

def generate_move_text(selected_titles, move_pool):
    text = ""
    for title in selected_titles:
        normalized_title = normalize(title)
        for move in move_pool:
            if normalize(move['title']) == normalized_title:
                formatted_title = ' '.join(move['title'].split())
                formatted_content = '\n'.join(
                    line.strip() for line in move['content'].split('\n')
                ) if move['content'] else ""
                text += f"◆ {formatted_title}\n{formatted_content}\n\n"
                break
    return text.strip()

class SkinSelectBuild(discord.ui.View):
    def __init__(self, skins_data: list):
        super().__init__(timeout=300)
        self.skins_data = skins_data

        self.skin_select = discord.ui.Select(
            placeholder="角色模板",
            options=[
                discord.SelectOption(
                    label=skin["name"].replace("\n", " "),
                    value=skin["ID"]
                ) for skin in skins_data
            ]
        )
        self.skin_select.callback = self.skin_selected
        self.add_item(self.skin_select)
    
    async def skin_selected(self, interaction: discord.Interaction):
        selected_id = self.skin_select.values[0]
        selected_skin = next(s for s in self.skins_data if s["ID"] == selected_id)
        rule = SKIN_RULES.get(selected_id.strip())

        summary_text = rule["summary"].replace("\\n", "\n") if rule and "summary" in rule else "（尚無簡介）"

        stat_select = StatSelectBuild(selected_skin)
        embed = discord.Embed(title=selected_skin["name"].replace("\n", " "), description=summary_text, color=discord.Color.dark_green())
        await interaction.response.edit_message(content="選擇屬性傾向", embed=embed, view=stat_select)

class StatSelectBuild(discord.ui.View):
    def __init__(self, skin: dict):
        super().__init__(timeout=300)
        self.skin = skin
        self.stat_select = discord.ui.Select(
            placeholder="屬性傾向",
            options=[
                discord.SelectOption(
                    label=f"hot {s['hot']}, cold {s['cold']}, vola {s['vola']}, dark {s['dark']}",
                    value=str(i)
                ) for i, s in enumerate(skin["stats"])
            ]
        )
        self.stat_select.callback = self.stat_selected
        self.add_item(self.stat_select)
    
    async def stat_selected(self, interaction: discord.Interaction):
        index = int(self.stat_select.values[0])
        selected_stat = self.skin["stats"][index]
        selected_id = self.skin["ID"]
        rule = SKIN_RULES.get(selected_id.strip())
        self.stat_choice=selected_stat

        await interaction.response.edit_message(
            content=None,
            embed=mhmove_embed(self.skin, rule, show_main=True, show_additional=False),
            view=MoveSelectBuild(
                skin=self.skin,
                rule=rule,
                stat_choice=selected_stat
            )
        )

class MoveSelectBuild(discord.ui.View):
    def __init__(self, skin: dict, rule: dict, stat_choice: dict):
        super().__init__(timeout=300)
        self.skin = skin
        self.rule = rule
        self.stat_choice = stat_choice

        self.fixed_moves = [normalize(m) for m in rule.get("fixedMoves", [])]
        self.selected_moves = self.fixed_moves.copy()

        if rule["moveCount"] > 0:
            options = [
                discord.SelectOption(label=m["title"], value=m["title"])
                for m in skin["move"]["moveList"]
                if normalize(m["title"]) not in self.fixed_moves
            ]

            select = discord.ui.Select(
                placeholder=f"請選擇 {rule['moveCount']} 個模板動作",
                min_values=rule["moveCount"],
                max_values=rule["moveCount"],
                options=options
            )
            select.callback = self.on_main_move_selected
            self.add_item(select)
        else:
            next_button = discord.ui.Button(label="沒有可選模板動作", style=discord.ButtonStyle.primary)
            next_button.callback = self.goto_add_move
            self.add_item(next_button)

    async def on_main_move_selected(self, interaction: discord.Interaction):
        dropdown: discord.ui.Select = self.children[0]
        self.selected_moves = self.fixed_moves + dropdown.values
        await self.proceed_to_next(interaction)
            
    async def goto_add_move(self, interaction: discord.Interaction):
        await self.proceed_to_next(interaction)

    async def proceed_to_next(self, interaction: discord.Interaction):
        if not self.selected_moves:
            self.selected_moves = self.fixed_moves.copy()

        try:
            if self.rule.get("allowAddMove", False):
                move_add = self.skin.get("moveAdd", {})
                move_add_list = move_add.get("moveAddList", [])

                if not move_add_list:
                    await interaction.response.send_modal(
                        FinalCharaBuild(
                            skin=self.skin,
                            stat=self.stat_choice,
                            selected_moves=self.selected_moves
                        )
                    )
                    return
                
                await interaction.response.edit_message(
                    content=None,
                    embed=mhmove_embed(self.skin, self.rule, show_main=False, show_additional=True),
                    view=AddMoveSelectBuild(
                        skin=self.skin,
                        rule=self.rule,
                        stat=self.stat_choice,
                        selected_moves=self.selected_moves
                    )
                )
            else:
                await interaction.response.send_modal(
                    FinalCharaBuild(
                        skin=self.skin,
                        stat=self.stat_choice,
                        selected_moves=self.selected_moves
                    )
                )
        except Exception as e:
            await interaction.response.send_message(
                "🐱 發生錯誤，請通知管理員喵。",
                ephemeral=True
            )
            raise

class AddMoveSelectBuild(discord.ui.View):
    def __init__(self, skin: dict, rule: dict, stat: dict, selected_moves: list[str]):
        super().__init__(timeout=300)
        self.skin = skin
        self.rule = rule
        self.stat = stat
        self.selected_moves=selected_moves
        self.selected_add_moves=[]

        move_add = skin.get("moveAdd", {})
        move_add_list = move_add.get("moveAddList", [])

        if move_add_list:
            add_options = [
                discord.SelectOption(label=m["title"], value=m["title"])
                for m in move_add_list
            ]
            select = discord.ui.Select(
                placeholder=f"請選擇 {rule['addMoveCount']} 個附加動作",
                min_values=rule["addMoveCount"],
                max_values=rule["addMoveCount"],
                options=add_options
            )
            select.callback = self.on_add_move_selected
            self.add_item(select)
        else:
            self.add_item(discord.ui.Button(
                label="完成",
                style=discord.ButtonStyle.primary,
                callback=self.skip_to_final
            ))
    
    async def on_add_move_selected(self, interaction: discord.Interaction):
        self.selected_add_moves = self.children[0].values
        await interaction.response.send_modal(
            FinalCharaBuild(
                skin=self.skin,
                stat=self.stat,
                selected_moves=self.selected_moves,
                selected_add_moves=self.selected_add_moves
            )
        )

    async def skip_to_final(self, interaction: discord.Interaction):
        await interaction.response.send_modal(
            FinalCharaBuild(
                skin=self.skin,
                stat=self.stat,
                selected_moves=self.selected_moves
            )
        )

class FinalCharaBuild(discord.ui.Modal, title="角色名稱與介紹"):
    def __init__(self, *, skin, stat, selected_moves, selected_add_moves=None):
        super().__init__(timeout=300)

        self.skin = skin
        self.stat = stat
        self.selected_moves = selected_moves
        self.selected_add_moves = selected_add_moves or []

        self.name_input = discord.ui.TextInput(
            label="角色名稱",
            placeholder="輸入角色名稱",
            max_length=30
        )
        self.add_item(self.name_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        name = self.name_input.value.strip()

        palette_lines = [
            f"2d6+{{HOT}}>=7 【HOT判定】",
            f"2d6+{{COLD}}>=7 【COLD判定】",
            f"2d6+{{VOLATILE}}>=7 【VOLATILE判定】",
            f"2d6+{{DARK}}>=7 【DARK判定】",
        ]

        all_moves = []
        if "move" in self.skin and "moveList" in self.skin["move"]:
            all_moves.extend(self.skin["move"]["moveList"])
        if "moveAdd" in self.skin and "moveAddList" in self.skin["moveAdd"]:
            all_moves.extend(self.skin["moveAdd"]["moveAddList"])

        main_move_text = generate_move_text(self.selected_moves, all_moves)
        add_move_text = generate_move_text(self.selected_add_moves, all_moves)
        
        custom_title = self.skin.get("moveAdd", {}).get("moveAddTitle", "附加動作")

        memo_text = ""
        if main_move_text:
            memo_text += "【模板動作】\n\n" + main_move_text + "\n"
        if add_move_text:
            memo_text += f"\n【{custom_title}】\n\n" + add_move_text + "\n"

        json_data = {
            "kind": "character",
            "data": {
                "name": name,
                "memo": memo_text.strip(),
                "initiative": -1,
                "externalUrl": "",
                "status": [
                    {"label": "Harm", "value": 4, "max": 4},
                    {"label": "Exp", "value": 0, "max": 5}
                ],
                "params": [
                    {"label": "HOT", "value": str(self.stat["hot"])},
                    {"label": "COLD", "value": str(self.stat["cold"])},
                    {"label": "VOLATILE", "value": str(self.stat["vola"])},
                    {"label": "DARK", "value": str(self.stat["dark"])}
                ],
                "commands": "\n".join(palette_lines)
            }
        }

        try:
            await interaction.message.edit(view=None)
        except:
            pass

        json_str = json.dumps(json_data, ensure_ascii=False, indent=2)
        await interaction.response.send_message(
            content=f"🐱 完成～複製以下 JSON 去 CCFOLIA 房間直接貼上即可生成角色喵！\n```json\n{json_str}\n```",
            ephemeral=True
        )

class ccfoliaMH(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="build_mh", description="建立 Monsterhearts 角色卡")
    async def build_mh(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            content="選擇模板來建立角色卡",
            view=SkinSelectBuild(SKINS_DATA),
            ephemeral=True
        )
        
async def setup(bot: commands.Bot):
    await bot.add_cog(ccfoliaMH(bot))

