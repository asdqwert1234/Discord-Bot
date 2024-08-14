import os,sys,traceback
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
from data.cogs_menu import cogs_menu
#讀取env資料
load_dotenv()

class helper(commands.AutoShardedBot):
    def __init__(self, intents, **options):
        super().__init__(intents = intents, **options)
        self.initial_extensions = cogs_menu
        self.load_extensions()
    
    def load_extensions(self):
        # 讀取函式庫
        for extension in self.initial_extensions:
            try:
                self.load_extension(extension)
            except Exception as e:
                print(f'Fail to load extension {extension}.', file = sys.stderr)
                traceback.print_exc()
    
    async def on_ready(self):
        
        print('-'*25)
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('-'*25)
    
    def run_bot(self):
        token = os.getenv("discord_bot_token")
        if not token:
            print('Error: discord_bot_token is not set in environment variables.', file=sys.stderr)
            return
        self.run(token)
    
intents = discord.Intents.all()
intents.message_content = True
intents.members = True 

bot = helper(
    intents=intents, 
    owner_id=int(os.getenv("bot_owner")), 
    command_prefix=os.getenv("bot_prefix")
)


if __name__ == '__main__':
    bot.run_bot()
