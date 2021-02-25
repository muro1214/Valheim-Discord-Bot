import os
from dotenv import load_dotenv

load_dotenv(override=True)

DISCORD_BOT_TOKEN = os.environ.get('DISCORD_BOT_TOKEN')
