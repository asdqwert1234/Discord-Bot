'''
Hexa 矩陣
'''

import discord
from discord.ext import commands
from cogs.functions.hexa_matrix_interactions import MatrixView

class HexaMatrix(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.slash_command(name="hexa碎片進度",description="看看你hexa矩陣的進度如何了")
    async def hexa_process(self, ctx):
        await ctx.respond("正在讀取中", ephemeral=True,delete_after=1)
        message = await ctx.send("選擇一個類別來開始")
        view = MatrixView(ctx, message)
        await message.edit("選擇一個類別來開始", view=view)
    
def setup(bot: commands.Bot):
    bot.add_cog(HexaMatrix(bot))
