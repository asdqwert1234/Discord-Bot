'''
訊息管理相關
'''

import discord
from discord.ext import commands
from discord.commands import Option
from data.content import SET_MESSAGE

# 一般權限 (只有刪自己的時候才能用，管理者可刪他人的)
class MessageManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    # 清理特定用戶訊息
    @commands.slash_command(name = 'clear', description = '清除訊息')
    async def member_msg_clear(
        self, 
        ctx: discord.ApplicationContext, 
        num : Option(int, '訊息數量') = 1,                                       # type: ignore
        member : Option(discord.Member, "刪除訊息對象", required=False) = None   # type: ignore
    ):
        # num 為負或0 -> 預設為 1
        num = 1 if num <= 1 else num
        # 設定刪除對象
        member = ctx.user if member == None else member
        # 權限檢查
        if not (ctx.channel.permissions_for(ctx.user).manage_messages or member == ctx.user):
            await ctx.response.send_message('你沒有權限可以刪除其他人的訊息喔', ephemeral=True, delete_after = 1)
            return
        # 設定 counter
        flag = num
        async for msg in ctx.channel.history():
            if msg.author == member:
                await msg.delete()
                if flag != 0:
                    flag -= 1
                else:
                    break
        if member == ctx.user:
            await ctx.response.send_message(f'已經清除您最近的{num}則訊息。', delete_after = 1, ephemeral=True)
        else:
            await ctx.response.send_message(f'已經清除<@{member.id}>最近的{num}則訊息。', delete_after= 10)
    
    # 清理特定用戶在每個文字頻道訊息中的第一個訊息 (刪除病毒訊息)
    @commands.slash_command(name = 'no_nsfw', description = '有人不小心點到陌生訊息的色色連結用的')
    async def clear_user_last_msgs(
        self,
        ctx: discord.ApplicationContext,
        key_words : Option(str, "刪除訊息含有的關鍵字", required=False) = "",    # type: ignore
        member : Option(discord.Member, "刪除訊息對象", required=False) = None             # type: ignore
    ):
        # 設定刪除對象
        member = ctx.user if member == None else member
        # 權限檢查
        if not (ctx.channel.permissions_for(ctx.user).manage_messages or member == ctx.user):
            await ctx.response.send_message('你沒有權限可以刪除其他人的訊息喔', ephemeral=True, delete_after = 1)
            return
        re = list()
        re.append('正在清除您在每個頻道中最新' if member == ctx.user else f'正在清除{member}在每個頻道中最新')
        re.append('訊息。' if key_words == "" else f'包含「{key_words}」的訊息。')
        await ctx.response.send_message( re[0] + re[1] , delete_after = 10)
        for channel in ctx.guild.channels:
            if isinstance(channel, discord.TextChannel) or isinstance(channel, discord.VoiceChannel):
                async for message in channel.history(limit = 100):
                    if key_words in message.content and message.author==member and not "正在清除" in message.content:
                        await message.delete()
                        break

    @commands.slash_command(description = 'Test')
    async def message_edit(
        self,
        ctx: discord.ApplicationContext,
        id: Option(str, "目標訊息ID", required = True) # type: ignore
    ):
        #權限檢查

        await ctx.response.send_message(f"This is test message.{id}")


# 需有管理權限區域
class MessageAdministration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    # 編輯機器人訊息成其他指定訊息 (機器人擁有者限定使用)
    @commands.command()
    async def msg_edit(self, ctx, id : int):
        # 機器人擁有者檢查
        if ctx.author.id == self.bot.owner_id:
            if id == None:
                await ctx.author.send('需要「訊息ID」方可進行此指令。')
            try:
                msg = await ctx.channel.fetch_message(int(id))
                await msg.edit(SET_MESSAGE)
            except discord.Forbidden:
                await ctx.author.send('我不是這個訊息的作者，無法編輯。')
            except discord.NotFound:
                await ctx.author.send('找不到此訊息。')
            except discord.HTTPException as e:
                await ctx.author.send(f'編輯訊息時發生錯誤：{e}')
        
        #刪除指令訊息
        
        await ctx.channel.purge(limit=1)
    
    # 清理頻道訊息
    @commands.command()
    async def ch_clr(self, ctx, n : int = 1):
        # n 輸入值為負或0 -> 預設為 1
        n = 1 if n <= 1 else n
        # 刪除指令訊息
        await ctx.channel.purge(limit=1)
        # 訊息管理權限檢查
        if ctx.channel.permissions_for(ctx.author).manage_messages:
            # n = n//100*100 + n%100 可拆分成(n//100)個100+(n%100)則訊息
            # (n//100)個100個訊息
            for _ in range(n//100):
                await ctx.channel.purge(limit = 100)
            # 剩下的訊息
            await ctx.channel.purge(limit = n%100)
            await ctx.respond(f'{ctx.author} 已經清除最近 {n} 則訊息。', delete_after=3)

    #編輯訊息指令錯誤
    @msg_edit.error
    async def msg_edit_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.author.send('「訊息ID」的格式錯誤，請確保他是一個有效的數字。')
    
    #頻道清理指令錯誤
    @ch_clr.error
    async def ch_clr_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.author.send('「訊息數量」的格式錯誤，請確保他是一個有效的數字。')


def setup(bot: commands.Bot):
    bot.add_cog(MessageManagement(bot))
    bot.add_cog(MessageAdministration(bot))