'''
每日事項
'''

import os, asyncio, discord, random, datetime, data.emoji
from dotenv import load_dotenv
from discord.ext import commands, tasks
from cogs.functions.time_functions import check_times_up
from data.content import ROLL_CALL_MESSAGE, ROLL_CALL_GIF, RECOVERY_RULE
from data.role_lists import guild_officer
from data.time_parameters import tz

load_dotenv()

class Alarm(commands.Cog):
    def __init__(self, bot):
        self.bot = bot     
        self.bot.loop.create_task(self.check_time_and_start_task()) 
      
    # task loop time的方法 一直出問題 很不穩定 改採用hour
    # 每分鐘檢查一次時間
    async def check_time_and_start_task(self):
        while True:
            if check_times_up():
                self.daily_clock.start()
                break
            await asyncio.sleep(60) # 每分鐘檢查一次


    @tasks.loop(hours = 24)
    async def daily_clock(self):
        print('時間到了')
        guild = self.bot.get_guild(int(os.getenv("guild_id")))
        
        # 點名通知
        role = discord.utils.get(guild.roles, name = data.emoji.reaction_role_maplestory["pepe_mention"])
        channel = self.bot.get_channel(int(os.getenv("mention_channel_id")))
        # 刪除昨天的訊息
        await channel.purge(limit=1)
        # 發送訊息
        embed = discord.Embed(color=discord.Color.random())
        embed.set_image(url=random.choice(ROLL_CALL_GIF))
        await channel.send(f'{role.mention}\n' + ROLL_CALL_MESSAGE, embed=embed)

        # 公會幹部遺漏事項檢查
        restore_permission_channel = self.bot.get_channel(int(os.getenv("restore_permission_channel_id")))  #還技能頻道
        admin_channel = self.bot.get_channel(int(os.getenv("admin_channel_id")))                            #管理頻道
        one_week_ago = datetime.datetime.utcnow() - datetime.timedelta(days=7)                              #一星期前時間
        target_emoji = '✅'                                                                                 # 偵測該訊息是否有 Emoji
        messages = await restore_permission_channel.history(after = one_week_ago).flatten()                 # 取得一星期內的訊息
        supervise_id = int(os.getenv("supervise_id"))                                                       # 監督ID  
        # 篩選未處理的訊息
        not_processed_messages = []
        for message in messages:
            no_react_flag = True
            if any(reaction.emoji == target_emoji for reaction in message.reactions):
                reactors = [user for reaction in message.reactions if reaction.emoji == target_emoji for user in await reaction.users().flatten()]
                if any(any(role.name in guild_officer for role in reactor.roles) for reactor in reactors):
                    no_react_flag = False
            if no_react_flag and f'<@&{supervise_id}>' in message.content:
                not_processed_messages.append(message.jump_url)
        if len(not_processed_messages):
            await admin_channel.send(f'<@&{supervise_id}> 有還沒有處理的訊息:\n'+'\n'.join(not_processed_messages))
        not_processed_messages.clear()
                
        now = datetime.datetime.now(tz)
        # 每週四幹部事務提醒通知
        if now.weekday() == 3:
            guild_master = discord.utils.get(guild.roles, name="玩具團長")
            await admin_channel.send(f"{guild_master.mention} 跨週了！記得\n1.小兵檢查\n2.公會技能")

        # 每月一日還技能、練分身次數刷新，留言規則提醒
        if now.day == 1:
            await restore_permission_channel.send(embeds=RECOVERY_RULE)
        


def setup(bot: commands.Bot):
    bot.add_cog(Alarm(bot))