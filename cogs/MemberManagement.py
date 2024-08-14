'''
會員管理
'''

import discord, json, os
from discord.commands import Option
from discord.ext import commands
from discord.ui import InputText, Modal
from dotenv import load_dotenv
from data.role_lists import guild_member, guild_officer
from cogs.functions.PostgreSQL import PostgreSQL, data_check

#讀取環境變數
load_dotenv()

# modal
class member_info(Modal):
    def __init__(self, ctx):
        super().__init__(title="你的資訊")
        SQL = os.getenv("postgresql")
        if SQL:
            SQL = json.loads(SQL)
        else:
            print("找不到 postgresql 環境變數")
            return
        
        self.cur = PostgreSQL(SQL)
        data = self.cur.search_data(ctx.author.id)
        self.first_time = (data == None)
        fields = [
            ("maplestory_id", "楓之谷遊戲ID", "填你的遊戲ID", 16),
            ("maplestory_job", "楓之谷職業", "填你的遊戲職業", 14),
            ("guild_roll_call", "點名進度", "填寫天數", 3),
            ("twitch", "Twitch頻道", "填URL", None),
            ("youtube", "Youtube頻道", "填URL", None)
        ]
        
        for field, label, placeholder, max_length in fields:
            kwargs = {
                "label": label,
                "required": False,
                "max_length": max_length
            }
            
            if self.first_time:
                kwargs["placeholder"] = placeholder
            else:
                kwargs["placeholder"] = placeholder if data[field] is None else None
                kwargs["value"] = data[field] if data[field] is not None else None
            
            if field in ["twitch", "youtube"]:
                kwargs["style"] = discord.InputTextStyle.long
            
            self.add_item(InputText(**kwargs))
        self.ctx = ctx
    
    async def callback(self, interaction: discord.Interaction):
        data={
            'user_id':self.ctx.author.id,
            "maplestory_id":self.children[0].value,
            "maplestory_job":self.children[1].value,
            "guild_roll_call":self.children[2].value,
            "twitch":self.children[3].value,
            "youtube":self.children[4].value
        }
        if self.first_time:
            #用save_data
            self.cur.save_data(data_check(data))
        else:
            #用update_data
            self.cur.update_data(data_check(data), self.ctx.author.id)
        del self.cur
        await interaction.response.send_message("資料已儲存", delete_after=1, ephemeral=True)

# slash command
class MemberManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.slash_command(name="登記資料", description="填寫資料")
    async def member_info_set(self, ctx):
        modal = member_info(ctx)
        await ctx.interaction.response.send_modal(modal)
    
    @commands.slash_command(name="查詢遊戲角色", description="輸入Discord成員，輸出遊戲ID")
    async def member_game_id_search(self, ctx, member: Option(discord.Member, "你想知道誰", required=True)):
        SQL = os.getenv("postgresql")
        if SQL:
            SQL = json.loads(SQL)
        else:
            print("找不到 postgresql 環境變數")
            return
        
        cur = PostgreSQL(SQL)
        target = cur.search_data(member.id)
        if target:
            await ctx.respond(f'{member.display_name} 是 {target["maplestory_id"]}')
        else:
            await ctx.respond(f'他似乎沒有登記資料喔')
        del cur

    @commands.slash_command(name="查詢成員", description="輸入遊戲ID，輸出Discord成員")
    async def member_discord_search(self, ctx, id: Option(str, "你想找誰的遊戲ID?", required=True)):
        SQL = os.getenv("postgresql")
        if SQL:
            SQL = json.loads(SQL)
        else:
            print("找不到 postgresql 環境變數")
            return
        
        cur = PostgreSQL(SQL)
        target = cur.search_data_id(id)
        if target:
            await ctx.respond(f'你要找的人是 <@{target["user_id"]}>', ephemeral=True)
        else:
            await ctx.respond(f'{id} 似乎還沒有登記資料喔', ephemeral=True)
        del cur
    
    @commands.slash_command(name = '資訊卡', description = "顯示會員的資訊卡")
    async def member_info_card(self, ctx, member: Option(discord.Member, "你想查詢誰的資訊?",required=False)=None):
        def role_str_generator(roles):
            if len(roles) == 1:
                return "這個人還沒有任何身分組"
            else:
                final_str = ""
                for role in roles:
                    if not role.name == "@everyone":
                        final_str = final_str + f'<@&{role.id}>' if role == roles[-1] else final_str + f'<@&{role.id}>\n'
                return final_str
        SQL = os.getenv("postgresql")
        if SQL:
            SQL = json.loads(SQL)
        else:
            print("找不到 postgresql 環境變數")
            return

        cur = PostgreSQL(SQL)
        target = member if member else ctx.author
        data = cur.search_data(target.id)
        if data:
            embed = discord.Embed(
                title=f"{target.name}#{target.discriminator}的資訊卡",
                color=discord.Color.random()
            )
            
            embed_fields = [
                ("用戶ID", str(target.id), False),
                ("伺服器暱稱", target.display_name, True),
                ("楓之谷ID", data.get('maplestory_id', '未設定'), True),
                ("楓之谷職業", data.get('maplestory_job', '未設定'), True),
                ("點名成就進度", f"{data.get('guild_roll_call', '0')}/365", True),
            ]
            
            if any(role.name in guild_member for role in target.roles):
                embed_fields.append(("苯甲記點", str(data.get('violates', 0)), True))
            
            embed_fields.extend([
                ("擁有身分組", role_str_generator(target.roles), False),
                ("Twitch頻道", data.get('twitch', '未設定'), False),
                ("Youtube頻道", data.get('youtube', '未設定'), False),
            ])
            
            for name, value, inline in embed_fields:
                if value != '未設定':
                    embed.add_field(name=name, value=value, inline=inline)
            
            usr = await self.bot.fetch_user(target.id)
            if usr.banner:
                embed.set_image(url=usr.banner.url)
            if target.display_avatar:
                embed.set_thumbnail(url=target.display_avatar.url)
            
            await ctx.respond(embed=embed)
        else:
            await ctx.channel.send(f'{target.display_name}還沒登記喔')
        del cur

#Admin commands
class MemberAdministration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def violations(self, ctx, member: discord.Member):
        await ctx.channel.purge(limit=1)
        if any(role.name in guild_officer for role in ctx.author.roles):
            SQL = os.getenv("postgresql")
            if SQL:
                SQL = json.loads(SQL)
            else:
                print("找不到 postgresql 環境變數")
                return
            cur = PostgreSQL(SQL)
            target = cur.search_data(member.id)
            if target == None:
                data = {'user_id':member.id, 'violates':1}
                cur.save_data(data)
            else:
                target['violates'] = target['violates'] + 1
                cur.update_data(data_check(target),member.id)
            del cur
            await ctx.respond('登記完畢',ephemeral=True)

    @commands.command()
    async def change_nick(self, ctx):
        await ctx.channel.purge(limit=1)
        if ctx.author.guild_permissions.manage_nicknames:
            SQL = os.getenv("postgresql")
            if SQL:
                SQL = json.loads(SQL)
            else:
                print("找不到 postgresql 環境變數")
                return
            cur = PostgreSQL(SQL)
            guild = self.bot.get_guild(os.getenv("guild_id"))
            target_list = cur.get_nick_list()
            for user_id, maplestory_id in target_list:
                member = guild.get_member(user_id)
                if member:
                    try:
                        if not member.nick == maplestory_id:
                            await member.edit(nick = maplestory_id)
                    except discord.errors.Forbidden:
                        print(f'修改 {user_id} : {maplestory_id} 的資料失敗')
            del cur
        
    

def setup(bot: commands.Bot):
    bot.add_cog(MemberManagement(bot))
    bot.add_cog(MemberAdministration(bot))