'''
表情符號身分組
'''

import discord, os, json
from discord.ext import commands
from dotenv import load_dotenv
from data.emoji import reaction_role_maplestory, reaction_role_other

load_dotenv()

class ReactionRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.messages = json.loads(os.getenv('reaction_role_message_id'))
        self.channel = os.getenv('role_channel_id')

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        #身分組
        if payload.message_id in self.messages.values():
            emoji_name = payload.emoji.name
            if payload.message_id == self.messages["maplestory"]:
                role_name = reaction_role_maplestory.get(emoji_name)
            elif payload.message_id == self.messages["others"]:
                role_name = reaction_role_other.get(emoji_name)
        
        if role_name:
            guild = self.bot.get_guild(payload.guild_id)
            role = discord.utils.get(guild.roles, name=role_name)
            member = guild.get_member(payload.user_id)
            if role and member:
                await member.add_roles(role)


    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.message_id in self.messages.values():
            emoji_name = payload.emoji.name
            if payload.message_id == self.messages["maplestory"]:
                role_name = reaction_role_maplestory.get(emoji_name)
            elif payload.message_id == self.messages["others"]:
                role_name = reaction_role_other.get(emoji_name)
        
        if role_name:
            guild = self.bot.get_guild(payload.guild_id)
            role = discord.utils.get(guild.roles, name=role_name)
            member = guild.get_member(payload.user_id)
            if role and member:
                await member.remove_roles(role)

def setup(bot: commands.Bot):
    bot.add_cog(ReactionRoles(bot))