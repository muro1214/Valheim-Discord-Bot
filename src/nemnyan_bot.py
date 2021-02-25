import discord
import settings
import subprocess


# TODO: はよ実装しろ
async def check_server_status():
    """
    pgrepでValheimサーバーが動いているか定期的に確認する
    """
    subprocess.check_output('pgrep -l valheim')
    

client = discord.Client()

@client.event
async def on_ready():
    client.change_presence(activity=discord.Game(name='Bot稼働中'))
    client.loop.create_task(check_server_status())
    

client.run(settings.DISCORD_BOT_TOKEN)
