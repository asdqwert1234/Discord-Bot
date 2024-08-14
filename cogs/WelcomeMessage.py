'''
歡迎訊息
'''
import os
from cogs.functions.image_processing import drawRect, imgRoundFunc
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from discord import File
from discord.ext import commands
from dotenv import load_dotenv
from data.images.images import background
from data.fonts.fonts import Font
from data.content import welcome_msg

load_dotenv()

class WelcomeMessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild_id = int(os.getenv('guild_id'))
        if member.guild.id == guild_id:
            guild = self.bot.get_guild(guild_id)
            welcome_channel = guild.get_channel(int(os.getenv('welcome_channel_id'))) #歡迎頻道
            role_channel = guild.get_channel(int(os.getenv('role_channel_id')))        #身分組頻道
            guided_channel = guild.get_channel(int(os.getenv('guided_channel_id')))    #引導頻道
            target = member
            bk_offset = 50
            drawRect(background, (bk_offset,bk_offset,background.size[0]-bk_offset,background.size[1]-bk_offset), fill=(0,0,0,150))
            asset = target.display_avatar
            data = BytesIO(await asset.read())
            pfp = Image.open(data)
            pfp = imgRoundFunc(pfp).resize((400,400))
            x,y = pfp.size
            pos = [int((background.size[0]-x)/2),230]
            offset = 10
            draw = ImageDraw.Draw(background) #create a draw object
            draw.pieslice([pos[0]-offset,pos[1]-offset,pos[0]+offset+x,pos[1]+offset+y], 0, 360, fill = "white", outline= 'white')
            background.paste(pfp,(pos[0],pos[1],pos[0]+x,pos[1]+y),pfp.convert('RGBA'))
            color = 'rgb(255, 255, 255)'
            Text = f'歡迎{target.name}來到【玩具工坊】！'
            TextSize = int(draw.textlength(Text,Font))
            TextPos = (int((background.size[0]-TextSize)/2),750)
            draw.text(TextPos,Text,fill=color,font=Font)
            with BytesIO() as image_binary:
                background.save(image_binary,'PNG')
                image_binary.seek(0)
                await welcome_channel.send(welcome_msg(member, guided_channel, role_channel),
                                           file=File(fp=image_binary,filename=f'welcome_{target.name}-{target.discriminator}.png')
                                           )


def setup(bot: commands.Bot):
    bot.add_cog(WelcomeMessage(bot))
