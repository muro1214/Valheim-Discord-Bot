import asyncio
import discord
import settings
import subprocess
import sys

from datetime import datetime, timedelta
from discord.ext import tasks
from logger import Logger
from tsunomaki_zyanken import TsunomakiZyanken
from valheim_state import ValheimState

# よくわからんが、discordのクライアントらしいのでヨシ！
client = discord.Client()
# サーバー稼働状態のステートマシン
valheim = ValheimState('valheim')
# サーバー情報のチャンネル
channel = None
# Valheimサーバーの起動時刻
server_startup_time = None


async def edit_channel_topic(topic):
    await channel.edit(topic=topic)


async def send_message(message):
    await channel.send(message)


@tasks.loop(minutes=10)
async def update_channel_topic():
    """
    チャンネルのトピックを定期的に更新する
    """
    global server_startup_time
    res = subprocess.run('pgrep -l valheim', shell=True, stdout=subprocess.PIPE, text=True)
    isRunning = 'valheim' in res.stdout

    if valheim.state == 'stopping':
        if isRunning:
            valheim.startup()
            server_startup_time = datetime.now()
            await edit_channel_topic(f'サーバーの稼働時間は 0 分ぺこ。起動時刻は {server_startup_time.strftime("%Y/%m/%d %H:%M:%S")} ですぺこ')
        else:
            await edit_channel_topic('サーバーはオフラインぺこ')
    elif valheim.state == 'running':
        if isRunning:
            td = datetime.now() - server_startup_time
            minutes = int(td.seconds / 60)
            await edit_channel_topic(f'サーバーの稼働時間は {minutes} 分ぺこ。起動時刻は {server_startup_time.strftime("%Y/%m/%d %H:%M:%S")} ですぺこ')
        else:
            valheim.shutdown()
            await edit_channel_topic('サーバーはオフラインぺこ')


@tasks.loop(minutes=1)
async def check_server_status():
    """
    pgrepでValheimサーバーが動いているか定期的に確認する
    """
    global server_startup_time
    res = subprocess.run('pgrep -l valheim', shell=True, stdout=subprocess.PIPE, text=True)
    isRunning = 'valheim' in res.stdout

    Logger.log(f'current state is {valheim.state}')

    if valheim.state == 'stopping':
        if isRunning:
            valheim.startup()
            server_startup_time = datetime.now()
            await send_message(':white_check_mark: **サーバーが立ち上がったぺこ**')
    elif valheim.state == 'running':
        if not isRunning:
            valheim.shutdown()
            await send_message(':octagonal_sign: **サーバーを落としたぺこ**')


@client.event
async def on_ready():
    global channel, server_startup_time
    channel = client.get_guild(settings.GUILD_ID).get_channel(settings.CHANNEL_ID)
    server_startup_time = datetime.now()  
    
    check_server_status.start()
    update_channel_topic.start()


@client.event
async def on_message(message):
    message_channel = message.channel


    def is_command(message, command):
        return message.content.startswith(command)


    def is_admin(message):
        return message.author.id == settings.ADMIN_ID


    if is_command(message, '!shutdown_bot') and is_admin(message):
        await message_channel.send('じゃあのぺこ')
        await client.logout()
    elif is_command(message, '!つのまきじゃんけん'):
        await message_channel.send(':fist:, :v:, :hand_splayed: のどれかでリアクションを付けてね')


        def check(reaction, user):
            hands = ['✊', '✌️', '🖐️']
            return user == message.author and str(reaction.emoji) in hands


        try:
            reaction, user = await client.wait_for('reaction_add', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await message_channel.send('時間切れだよ')
        else:
            zyanken = TsunomakiZyanken()
            result = zyanken.play_game(str(reaction.emoji))
            await message_channel.send(result[0])
            await message_channel.send(result[1])
    

client.run(settings.DISCORD_BOT_TOKEN)
