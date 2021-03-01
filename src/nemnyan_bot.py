import discord
import settings
import subprocess
import sys

from datetime import datetime, timedelta
from discord.ext import tasks
from logger import Logger
from valheim_state import ValheimState

# よくわからんが、discordのクライアントらしいのでヨシ！
client = discord.Client()
# サーバー稼働状態のステートマシン
valheim = ValheimState('valheim')
# サーバー情報のチャンネル
channel = None
# Valheimサーバーの起動時刻
server_startup_time = None


async def update_channel_topic(topic):
    await channel.edit(topic=topic)


async def send_message(message):
    await channel.send(message)


@tasks.loop(minutes=5)
async def check_server_status():
    """
    pgrepでValheimサーバーが動いているか定期的に確認する
    """
    global server_startup_time
#    res = subprocess.run('pgrep -l valheim', shell=True, stdout=subprocess.PIPE, text=True)
#    isRunning = 'valheim' in res.stdout
    res = subprocess.run('dir', shell=True, stdout=subprocess.PIPE, text=True)
    isRunning = 'valheim-mock.txt' in res.stdout

    Logger.log(f'current state is {valheim.state}')

    if valheim.state == 'stopping':
        if isRunning:
            valheim.startup()
            server_startup_time = datetime.now()
            await send_message(':white_check_mark: **サーバーが立ち上がったぺこ**')
            await update_channel_topic(f'サーバーの稼働時間は 0 分ぺこ。起動時刻は {server_startup_time.strftime("%Y/%m/%d %H:%M:%S")} ですぺこ')
        else:
            await update_channel_topic('サーバーはオフラインぺこ')
    elif valheim.state == 'running':
        if isRunning:
            td = datetime.now() - server_startup_time
            minutes = int(td.seconds / 60)
            await update_channel_topic(f'サーバーの稼働時間は {minutes} 分ぺこ。起動時刻は {server_startup_time.strftime("%Y/%m/%d %H:%M:%S")} ですぺこ')
        else:
            valheim.shutdown()
            await send_message(':octagonal_sign: **サーバーを落としたぺこ**')
            await update_channel_topic('サーバーはオフラインぺこ')
    

@client.event
async def on_ready():
    global channel, server_startup_time
    channel = client.get_guild(settings.GUILD_ID).get_channel(settings.CHANNEL_ID)
    server_startup_time = datetime.now()  
    
    check_server_status.start()


def is_command(message, command):
    return message.content.startswith(command)


def is_admin(message):
    return message.author.id == settings.ADMIN_ID


@client.event
async def on_message(message):
    if is_command(message, '!shutdown_bot') and is_admin(message):
        await client.logout()
        await sys.exit()
    

client.run(settings.DISCORD_BOT_TOKEN)
