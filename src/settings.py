import os
from dotenv import load_dotenv

load_dotenv(override=True)

DISCORD_BOT_TOKEN = os.environ.get('DISCORD_BOT_TOKEN')
GUILD_ID = int(os.environ.get('GUILD_ID'))
SERVER_INFO_CHANNEL_ID = int(os.environ.get('SERVER_INFO_CHANNEL_ID'))
COMMON_CHANNEL_ID = int(os.environ.get('COMMON_CHANNEL_ID'))
ADMIN_ID = int(os.environ.get('ADMIN_ID'))
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
