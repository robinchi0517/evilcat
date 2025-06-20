import discord, os, json
from discord.ext import commands
from discord import app_commands

def clean_name(name: str) -> str:
    return name.replace("\n", " ")

def build_embed(skin: dict, page: int) -> discord.Embed:
    embed = discord.Embed(color=discord.Color.dark_purple())
    embed.set_author(name=skin["name"].replace("\n", " "))

    if page == 0:
        embed.description = skin["flavorText"] + "\n\u200b"
        embed.add_field(name="📖 **背景故事**", value=skin["backStory"], inline=False)

    elif page == 1:
        for i, stat in enumerate(skin["stats"], 1):
            stat_text = f"hot {stat['hot']}, cold {stat['cold']}, volatile {stat['vola']}, dark {stat['dark']}"
            if i == len(skin["stats"]):
                stat_text += "\n\u200b"
            embed.add_field(name=f"**屬性傾向 {i}**", value=stat_text, inline=False)
        embed.add_field(name="🌱 **發展選項**", value="\n".join(skin["advance"]) + "\n\u200b", inline=False)

    elif page == 2:
        embed.add_field(name="🌘 **黑暗面**", value=skin["darkSelf"] + "\n\u200b", inline=False)
        embed.add_field(name="❣️ **性動作**", value=skin["sexMove"] + "\n\u200b", inline=False)

    elif page == 3:
        embed.title = "📄 **模板動作**"
        embed.description = skin["moveInfo"]
        for move in skin["move"]["moveList"]:
            embed.add_field(name=move["title"], value=move["content"] + "\n\u200b", inline=False)

    elif page == 4:
        if not (skin.get("moveAdd") and skin["moveAdd"].get("moveAddList")):
            return build_embed(skin, 0 )
        embed.title = "📎 **附加動作**"
        embed.description = skin["moveAdd"]["moveAddTitle"]
        for move in skin["moveAdd"]["moveAddList"]:
            embed.add_field(name=move["title"], value=move["content"] + "\n\u200b", inline=False)

    return embed

class CategorySelect(discord.ui.Select):
    def __init__(self, skins_data: list, skin_select: discord.ui.Select):
        self.skins_data = skins_data
        self.skin_select = skin_select
        options = [
            discord.SelectOption(label="核心模板", value="core"),
            discord.SelectOption(label="擴充模板", value="add"),
            discord.SelectOption(label="創作模板", value="own"),
        ]
        super().__init__(
            placeholder="選擇分類",
            min_values=1,
            max_values=1,
            options=options
        )
    async def callback(self, interaction: discord.Interaction):
        selected_type = self.values[0]
        filtered = [s for s in self.skins_data if s.get("type") == selected_type]
        self.skin_select.options = [
            discord.SelectOption(label=clean_name(s["name"]), value=str(i))
            for i, s in enumerate(filtered)
        ]
        self.skin_select.filtered_skins = filtered
        self.skin_select.disabled = False

        LABELS = {
            "core": "核心模板",
            "add": "擴充模板",
            "own": "創作模板"
        }
        self.placeholder = LABELS.get(selected_type, "選擇分類")
        await interaction.response.edit_message(view=self.view)

class SkinSelect(discord.ui.Select):
    def __init__(self):
        super().__init__(
            placeholder="選擇模板", 
            min_values=1, 
            max_values=1, 
            options=[discord.SelectOption(label="請先選擇分類", value="none")],
            disabled=True
        )
        self.filtered_skins = []
        
    async def callback(self, interaction: discord.Interaction):
        index = int(self.values[0])
        skin = self.filtered_skins[index]

        await interaction.response.defer(ephemeral=True)

        await interaction.followup.send(
            embed=build_embed(skin, 0), 
            view=PageView(skin, 0),
            ephemeral=True
        )

class DualSelectView(discord.ui.View):
    def __init__(self, skin_data: list):
        super().__init__(timeout=None)

        skin_select = SkinSelect()
        category_select = CategorySelect(skin_data, skin_select)

        self.add_item(category_select)
        self.add_item(skin_select)

class PageButton(discord.ui.Button):
    def __init__(self, label, direction, skin, page_ref, total_pages):
        super().__init__(label=label, style=discord.ButtonStyle.primary)
        self.direction = direction
        self.skin = skin
        self.page_ref = page_ref
        self.total_pages = total_pages
    
    async def callback(self, interaction: discord.Interaction):
        self.page_ref[0] += self.direction
        self.page_ref[0] = max(0, min(self.page_ref[0], self.total_pages - 1))
        new_embed = build_embed(self.skin, self.page_ref[0])
        await interaction.response.edit_message(
            embed=new_embed, 
            view=PageView(self.skin, self.page_ref[0])
            )

class SkinSelectView(discord.ui.View):
    def __init__(self, skins_data):
        super().__init__(timeout=None)
        self.add_item(SkinSelect(skins_data))

class PageView(discord.ui.View):
    def __init__(self, skin: dict, page: int = 0):
        super().__init__(timeout=None)
        self.page = [page]
        self.skin = skin
        self.total_pages = 5 if skin.get("moveAdd") and skin["moveAdd"].get("moveAddList") else 4
        
        if page > 0:
            self.add_item(PageButton("⬅️", -1, skin, self.page, self.total_pages))
        self.add_item(SendToChannelButton(skin, self.page))
        if page < self.total_pages - 1:
            self.add_item(PageButton("➡️", 1, skin, self.page, self.total_pages))

class SendToChannelButton(discord.ui.Button):
    def __init__(self, skin, page_ref):
        super().__init__(label="📤", style=discord.ButtonStyle.secondary)
        self.skin = skin
        self.page_ref = page_ref

    async def callback(self, interaction: discord.Interaction):
        embed = build_embed(self.skin, self.page_ref[0])
        await interaction.channel.send(embed=embed)
        await interaction.response.send_message("已將此內容發送至頻道！", ephemeral=True)

class SkinViewer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="skins", description="選擇並檢視 Monster Hearts 模板")
    async def skin(self, interaction: discord.Interaction):
        base_dir = os.path.dirname(__file__)
        json_path = os.path.join(base_dir, "..", "data", "mhdict_skins.json")

        try:
            with open(json_path, "r", encoding="utf-8") as file:
                mh_data = json.load(file)
            
            skins_data = mh_data["Skins"]
            await interaction.response.send_message(
                content="請先選擇分類再選擇模板：", 
                view=DualSelectView(skins_data), 
                ephemeral=True
            )
        except Exception as e:
            print(f"[DEBUG] Skins command failed: {e}")

async def setup(bot: commands.Bot):
    await bot.add_cog(SkinViewer(bot))
