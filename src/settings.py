import os
from dotenv import load_dotenv

load_dotenv(override=True)

DISCORD_BOT_TOKEN = os.environ.get('DISCORD_BOT_TOKEN')
GUILD_ID = int(os.environ.get('GUILD_ID'))
CHANNEL_ID = int(os.environ.get('CHANNEL_ID'))
ADMIN_ID = int(os.environ.get('ADMIN_ID'))
