#!/usr/bin/python3.8

import asyncio
import discord
import settings
import subprocess

from datetime import datetime
from discord.ext import tasks
from logger import Logger
from nemnyan_github import NemnyanGithub
from tsunomaki_zyanken import TsunomakiZyanken
from valheim_state import ValheimState

# よくわからんが、discordのクライアントらしいのでヨシ！
intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)
# サーバー稼働状態のステートマシン
valheim = ValheimState('valheim')
# サーバー情報のチャンネル
server_info_channel = None
# Valheimサーバーの起動時刻
server_startup_time = None
# 現在の最新バージョン
latest_version = None
# メンテモード
is_maintenance = False


async def edit_channel_topic(topic):
    await server_info_channel.edit(topic=topic)


async def send_message(dest_channel, message):
    await dest_channel.send(message)


@tasks.loop(minutes=10)
async def update_channel_topic():
    """
    チャンネルのトピックを定期的に更新する
    """
    global server_startup_time, is_maintenance

    if is_maintenance:
        await edit_channel_topic(f'サーバーメンテ中ぺこ')
        return

    res = subprocess.run('pgrep -l valheim', shell=True, stdout=subprocess.PIPE, text=True)
    isRunning = 'valheim' in res.stdout

    if valheim.state == 'stopping':
        if isRunning:
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
            await edit_channel_topic('サーバーはオフラインぺこ')


@tasks.loop(minutes=1)
async def check_server_status():
    """
    pgrepでValheimサーバーが動いているか定期的に確認する
    """
    global server_startup_time, is_maintenance

    if is_maintenance:
        return

    res = subprocess.run('pgrep -l valheim', shell=True, stdout=subprocess.PIPE, text=True)
    isRunning = 'valheim' in res.stdout

    Logger.log(f'current state is {valheim.state}')

    if valheim.state == 'stopping':
        if isRunning:
            valheim.startup()
            server_startup_time = datetime.now()
            await send_message(server_info_channel, ':white_check_mark: **サーバーが立ち上がったぺこ**')
    elif valheim.state == 'running':
        if not isRunning:
            valheim.shutdown()
            await send_message(server_info_channel, ':octagonal_sign: **サーバーを落としたぺこ**')


@tasks.loop(minutes=1)
async def notify_latest_release():
    global latest_version

    current_version = NemnyanGithub().get_latest_release_tag()
    print(latest_version)
    print(current_version)
    if latest_version == current_version:
        return

    latest_version = current_version
    release_url = NemnyanGithub().get_latest_release_url()

    common_channel = client.get_guild(settings.GUILD_ID).get_channel(settings.COMMON_CHANNEL_ID)
    await send_message(common_channel, f"MODの最新バージョンがリリースされたから、更新するぺこよ～\n{release_url}")


@client.event
async def on_ready():
    global server_info_channel, server_startup_time, latest_version
    server_info_channel = client.get_guild(settings.GUILD_ID).get_channel(settings.SERVER_INFO_CHANNEL_ID)
    server_startup_time = datetime.now()
    latest_version = NemnyanGithub().get_latest_release_tag()
    
    check_server_status.start()
    update_channel_topic.start()
    notify_latest_release.start()

    await send_message(server_info_channel, ':rabbit: こんぺこ！こんぺこ！こんぺこー！兎田ぺこらぺこ！')


@client.event
async def on_message(message):
    global is_maintenance
    message_channel = message.channel


    def is_command(message, command):
        return message.content.startswith(command)


    def is_admin(message):
        return message.author.id == settings.ADMIN_ID


    if is_command(message, '!shutdown_bot') and is_admin(message):
        await send_message(message_channel, 'じゃあのぺこ')
        await client.logout()
    elif is_command(message, '!つのまきじゃんけん'):
        await send_message(message_channel, ':fist:, :v:, :hand_splayed: のどれかでリアクションを付けてね')


        def check(reaction, user):
            hands = ['✊', '✌️', '🖐️']
            return user == message.author and str(reaction.emoji) in hands


        try:
            reaction, user = await client.wait_for('reaction_add', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await send_message(message_channel, '時間切れだよ')
        else:
            zyanken = TsunomakiZyanken()
            url, result = zyanken.play_game(str(reaction.emoji))
            await send_message(message_channel, url)
            await send_message(message_channel, result)
    elif is_command(message, '!maintenance'):
        if is_maintenance:
            is_maintenance = False
            await send_message(message_channel, 'サーバーメンテが終わったぺこ')
        else:
            is_maintenance = True
            await send_message(message_channel, 'サーバーメンテが始まったぺこ')



@client.event
async def on_member_join(member):
    await member.send('#サーバー情報 のピン留めメッセージにマルチサーバーの情報が書いてあるぺこ')


client.run(settings.DISCORD_BOT_TOKEN)
