import os, discord
from dotenv import load_dotenv
import data.hexa_level as hexa_level

load_dotenv()


# 機器人預設訊息
SET_MESSAGE = 'This is set message.'

#點名通知
ROLL_CALL_MESSAGE = '早安！你好\n記得 **點名**\n～認同請分享～'

#點名用GIF
ROLL_CALL_GIF = [
    "https://media.discordapp.net/attachments/1043187561901850674/1061702653484224674/8bfee70b337fb82d.gif",
    "https://media.discordapp.net/attachments/1043187561901850674/1061702653802983474/e7ead4ea906bfb6d.gif"
]

#還技能規則
supervise_id = int(os.getenv("supervise_id"))
RECOVERY_RULE = list()
affiliated_guilds_rule = discord.Embed(
    title = "分身公會留言格式",
    description = f"<@&{supervise_id}> **ID 職業 等級退**\n\n範例 : <@&{supervise_id}> `玩具小幫手 機甲戰神 250退`",
    color = discord.Color.random()
)
restore_skill_rule = discord.Embed(
    title = "歸還技能留言格式",
    description = f"'<@&{supervise_id}> ID 技能++\n\n範例 :  <@&{supervise_id}>  `玩具小幫手 技能++`",
    color = discord.Color.random()
)

affiliated_guilds_rule.add_field(name='**【注意】**',value="分身公會這個月起改為玩具肝坊\n分身公會是給大家方便提升戰力來練等\n請麻煩練完一定要記得退公會！別增加幹部的負擔\n請自己檢查一下有沒有還沒退的\n太多次被我們檢查到會記違規\n超過三次就不准再加入瞜" ,inline=False)
restore_skill_rule.add_field(name='**【注意】**',value="請記得檢查你是否已經完成本周的任務\n要有紀錄才會歸還技能\n一個月只有一次還技能的機會喔" ,inline=False)

RECOVERY_RULE.append(affiliated_guilds_rule)
RECOVERY_RULE.append(restore_skill_rule)

def welcome_msg(member : discord.Member, guided_channel, role_channel):
    msg = f'你好阿！{member.mention} ，歡迎來到【玩具工坊】！\n'
    msg += f'目前<#{guided_channel.id}>在準備中，\n'
    msg += f'未來如果有要查看頻道功能，可以到這裡查看。\n'
    msg += f'可以根據你的需求到<#{role_channel.id}>領取你需要的身分組！'
    return msg

def hexa_matrix_progress(type, levels): # name = core_type , levels = list of level
    result = '```ansi\n'

    core_translate = {
            "origin": '技能核心',
            "mastery": '精通核心',
            "enhance": '強化核心',
            "common": '共通核心'
        }

    total_fragments_of_type =  sum(getattr(hexa_level, f'{type}_fragments'))

    for i, level in enumerate(levels):
        result += f'[2;35m{core_translate[type]}{i+1}：[0m'
        result += f'[2;34m{level}[0m'
        now = sum(getattr(hexa_level, f'{type}_fragments')[:level]) if type == 'origin' else sum(getattr(hexa_level, f'{type}_fragments')[:1+level])
        result += f'[2;31m[2;36m【{now}/{total_fragments_of_type}】[0m[2;31m[0m\n'
    result += '\n```'
    return result
    
