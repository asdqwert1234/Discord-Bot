'''
測試指令
'''

import discord, datetime
from data.content import hexa_matrix_progress
from discord.ext import commands
from data.time_parameters import tz

class TestCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.slash_command(description = 'Test')
    async def test(self, ctx):
        await ctx.respond(hexa_matrix_progress(1,[1]))

    @commands.slash_command(description = 'To tell you what time is it.')
    async def clock(self, ctx):
        await ctx.respond(f"我這裡的時間是{datetime.datetime.now(tz).hour}點{datetime.datetime.now(tz).minute}分{datetime.datetime.now(tz).second}秒")
    
    @commands.command
    async def shutdown(self, ctx):
        await ctx.channel.purge(limit=1)
        if ctx.author.id == self.bot.owner_id:
            await ctx.send("正在從Discord端關閉機器人...")
            await self.bot.close()
        
    
def setup(bot: commands.Bot):
    bot.add_cog(TestCommand(bot))
