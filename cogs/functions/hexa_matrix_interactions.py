import discord, datetime, math
import data.hexa_level as hexa_level
from discord.ui import InputText, Modal, View, Select
from data.content import hexa_matrix_progress
from data.time_parameters import tz

core_user = dict()

class Core():
    def __init__(self, ctx):
        self.user_id = ctx.author.id
        self.name = ctx.author.display_name
        self.origin = [1]           # 起源
        self.mastery = [0,0]        # 精通
        self.enhance = [0,0,0,0]    # 強化
        self.common = [0]           # 共通
        self.fragments = 0          # 背包碎片
        self.daily = 0              # 每日打怪獲得
        self.high_mountain = "0點"

    def update_core(self, children, attr, min_val=0, max_val=30):
        for i, child in enumerate(children):
            try:
                value = int(child.value)
                if min_val <= value <= max_val:
                    getattr(self, attr)[i] = value
            except ValueError:
                pass

    def update_origin(self, children):
        self.update_core(children, 'origin', 1, 30)
        
    def update_mastery(self, children):
        self.update_core(children, 'mastery')
    
    def update_enhance(self, children):
        self.update_core(children, 'enhance')
    
    def update_common(self, children):
        self.update_core(children, 'common')

    def update_integer(self, value, attr):
        try:
            value = int(value)
            if value >= 0:
                setattr(self, attr, value)
        except ValueError:
            pass

    def update_fragments(self, value):
        self.update_integer(value, 'fragments')

    def update_daily(self, value):
        self.update_integer(value, 'daily')
    
    def core_info(self):
        now = self.calculate_progress()  # [progress, used_fragments, remaining_fragments, total_fragments, days_to_complete, completion_date]
        description = f"目前進度為 **{now[0]}%**【{now[3]-now[2]}/{now[3]}】\n"
        description += f"已消耗碎片：{now[1]}"
        embed = discord.Embed(title=f"`{self.name}`的碎片進度", description=description, color=0x664499)

        
        core_types = {
            "origin": self.origin,
            "mastery": self.mastery,
            "enhance": self.enhance,
            "common": self.common
        }

        core_translate = {
            "origin": '技能核心',
            "mastery": '精通核心',
            "enhance": '強化核心',
            "common": '共通核心'
        }
        
        for type, levels in core_types.items():
            value = hexa_matrix_progress(type, levels)
            embed.add_field(name=f'__{core_translate[type]}__', value=value, inline=False)
        
        other_info = f'背包內剩餘碎片：{self.fragments}\n平均每日打怪獲得量：{self.daily}\n高山副本花費點數：{self.high_mountain}'
        embed.add_field(name="__其他資訊__", value=other_info, inline=False)
        embed.add_field(name="__含每日、每周任務後__", value=f'還需要**{now[4]}**天，預計完成時間:**{now[5]}**', inline=False)
        return embed
    
    # 計算進度
    def calculate_progress(self):
        # 碎片總量
        core_types = ['origin', 'mastery', 'enhance', 'common']
        total_fragments = sum(len(getattr(self, core)) * sum(getattr(hexa_level, f'{core}_fragments')) for core in core_types)
        now = self.fragments
        used_fragments = 0
        for types in core_types:
            for level in getattr(self, types):
                used_fragments += sum(getattr(hexa_level, f'{types}_fragments')[:level]) if type == 'origin' else sum(getattr(hexa_level, f'{types}_fragments')[:1+level])
        now += used_fragments
        
        # 算進度
        progress = round(now / total_fragments * 100, 3)
        # 算剩餘碎片量
        remaining_fragments = total_fragments - now
        # 算天數(每周、日任務、高山副本)
        daily_gain = 12 + self.daily
        weekly_tasks = 50 #每周三增加
        high_mountain = {"0點":30, "200點":90, "360點":150} #每周四增加
        high_mountain_value = high_mountain[self.high_mountain]
        # 計算剩餘天數
        # 計算到下一個周三與周四的天數
        today = datetime.datetime.now(tz).weekday()
        days_to_wednesday = (2 - today) % 7
        days_to_thursday = (3 - today) % 7
        
        # 計算總天數
        now_fragments = 0
        days = 0
        while now_fragments < remaining_fragments:
            now_fragments += daily_gain
            if (days+1) % 7 == days_to_wednesday:
                now_fragments += weekly_tasks
            if (days+1) % 7 == days_to_thursday:
                now_fragments += high_mountain_value
            days += 1
        
        days_to_complete = days
        
        # 計算預計完成日期
        completion_date = (datetime.datetime.now(tz) + datetime.timedelta(days=days_to_complete)).date()
        
        return [progress, used_fragments, remaining_fragments, total_fragments, days_to_complete, completion_date]





# 起源 origin
class OriginCoreModal(Modal):
    def __init__(self, ctx, message) -> None:
        super().__init__(title = "技能核心")
        self.ctx = ctx
        self.message = message

        global core_user
        for i in range(len(core_user[self.ctx.author.id].origin)):
            self.add_item(InputText(label = f"技能核心{i+1}", placeholder = "請輸入技能核心等級(1~30)", max_length=2))
    
    async def callback(self, interaction: discord.Interaction):
        global core_user
        core_user[self.ctx.author.id].update_origin(self.children)
        await self.message.edit(content='你目前所設定的核心等級',embed=core_user[self.ctx.author.id].core_info())
        await interaction.response.send_message("技能核心資訊已收集完畢。", ephemeral=True,delete_after=0.1)
        pass



# 精通 mastery
class MasteryCoreModal(Modal):
    def __init__(self, ctx, message) -> None:
        super().__init__(title = "精通核心")
        self.ctx = ctx
        self.message = message

        global core_user
        for i in range(len(core_user[self.ctx.author.id].mastery)):
            self.add_item(InputText(label = f"精通核心{i+1}", placeholder = "請輸入精通核心等級(0~30)", max_length=2))
    
    async def callback(self, interaction: discord.Interaction):
        global core_user
        core_user[self.ctx.author.id].update_mastery(self.children)
        await self.message.edit(content='你目前所設定的核心等級',embed=core_user[self.ctx.author.id].core_info())
        await interaction.response.send_message("技能核心資訊已收集完畢。", ephemeral=True,delete_after=0.1)
        pass

# 強化 enhance
class EnhanceCoreModal(Modal):
    def __init__(self, ctx, message) -> None:
        super().__init__(title = "強化核心")
        self.ctx = ctx
        self.message = message

        global core_user
        for i in range(len(core_user[self.ctx.author.id].enhance)):
            self.add_item(InputText(label = f"強化核心{i+1}", placeholder = "請輸入強化核心等級(0~30)", max_length=2))
    
    async def callback(self, interaction: discord.Interaction):
        global core_user
        core_user[self.ctx.author.id].update_enhance(self.children)
        await self.message.edit(content='你目前所設定的核心等級',embed=core_user[self.ctx.author.id].core_info())
        await interaction.response.send_message("技能核心資訊已收集完畢。", ephemeral=True,delete_after=0.1)
        pass

# 共通 common
class CommonCoreModal(Modal):
    def __init__(self, ctx, message) -> None:
        super().__init__(title = "共通核心")
        self.ctx = ctx
        self.message = message

        global core_user
        for i in range(len(core_user[self.ctx.author.id].common)):
            self.add_item(InputText(label = f"共通核心{i+1}", placeholder = "請輸入共通核心等級(0~30)", max_length=2))
    
    async def callback(self, interaction: discord.Interaction):
        global core_user
        core_user[self.ctx.author.id].update_common(self.children)
        await self.message.edit(content='你目前所設定的核心等級',embed=core_user[self.ctx.author.id].core_info())
        await interaction.response.send_message("技能核心資訊已收集完畢。", ephemeral=True,delete_after=0.1)
        pass

# 其他資訊
class OtherInfoModal(Modal):
    def __init__(self, ctx, message) -> None:
        super().__init__(title = "其他資訊")
        self.ctx = ctx
        self.message = message
        self.add_item(InputText(label="背包內剩餘碎片", placeholder="輸入數量", required=True))
        self.add_item(InputText(label="平均每日打怪獲得量", placeholder="輸入數量(不含每日任務12個，不輸入預設為0)",required=False))
    
    async def callback(self, interaction: discord.Interaction):
        global core_user
        core_user[self.ctx.author.id].update_fragments(self.children[0].value)
        core_user[self.ctx.author.id].update_daily(self.children[1].value)
        await self.message.edit(content='你目前所設定的核心等級', embed=core_user[self.ctx.author.id].core_info())
        await interaction.response.send_message("資訊已收集完畢。", ephemeral=True , delete_after=0.1)


# 控制台按鈕
class MatrixButton(discord.ui.Button):
    def __init__(self, label, ctx, message, style = discord.ButtonStyle.primary):
        super().__init__(label = label, style = style)
        self.ctx = ctx
        self.message = message

    async def callback(self, interaction: discord.Interaction):
        global core_user
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("這不是你的喔!", ephemeral=True)
            return
        if self.ctx.author.id not in core_user:
            core_user[self.ctx.author.id] = Core(self.ctx)
        selected = self.label
        modal = None

        # 根據按鈕標籤來決定要打開的 Modal
        if selected == "技能核心":
            modal = OriginCoreModal(self.ctx, self.message)
        elif selected == "精通核心":
            modal = MasteryCoreModal(self.ctx, self.message)
        elif selected == "強化核心":
            modal = EnhanceCoreModal(self.ctx, self.message)
        elif selected == "共通核心":
            modal = CommonCoreModal(self.ctx, self.message)
        elif selected == "其他資訊":
            modal = OtherInfoModal(self.ctx, self.message)
        elif selected == "結算進度":
            await self.message.edit(content='以下為計算結果', view=None)
        if modal:
            await interaction.response.send_modal(modal)
        pass

class HighMountainSelect(Select):
    def __init__(self, ctx, message):
        options = [
            discord.SelectOption(label="0點", description="30個碎片"),
            discord.SelectOption(label="200點", description="90個碎片"),
            discord.SelectOption(label="360點", description="150個碎片")
        ]
        super().__init__(placeholder="高山副本花費點數", min_values=0, max_values=1, options=options)
        self.ctx = ctx
        self.message = message
    
    async def callback(self, interaction: discord.Interaction):
        global core_user
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("這不是你的喔!", ephemeral=True)
            return
        if self.ctx.author.id not in core_user:
            core_user[self.ctx.author.id] = Core(self.ctx)
        core_user[self.ctx.author.id].high_mountain = self.values[0]
        await self.message.edit(content='你目前所設定的核心等級',embed=core_user[self.ctx.author.id].core_info())
        await interaction.response.send_message("資訊已收集完畢。", ephemeral=True , delete_after=0.1)

class MatrixView(View):
    def __init__(self, ctx, message):
        super().__init__()
        self.ctx = ctx
        self.message = message
        self.add_item(MatrixButton("技能核心", self.ctx, self.message))
        self.add_item(MatrixButton("精通核心", self.ctx, self.message))
        self.add_item(MatrixButton("強化核心", self.ctx, self.message))
        self.add_item(MatrixButton("共通核心", self.ctx, self.message))
        self.add_item(MatrixButton("其他資訊", self.ctx, self.message))
        self.add_item(HighMountainSelect(self.ctx, self.message))
        self.add_item(MatrixButton("結算進度", self.ctx, self.message, discord.ButtonStyle.danger))
    
    async def on_timeout(self):
        await self.message.edit(view=None)



