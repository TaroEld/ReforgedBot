import discord
import os
import re
import requests
from dotenv import load_dotenv

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

mods = {
	'Reforged Mod': 'Battle-Modders/mod-reforged',
	'Modern Hooks': 'MSUTeam/Modern-Hooks',
	'Modding Standards & Utilities (MSU)': 'MSUTeam/MSU',
	'Modular Vanilla': 'Battle-Modders/mod_modular_vanilla',
	'Nested Tooltips Framework': 'MSUTeam/nested-tooltips',
	'Dynamic Perks Framework (DPF)': 'Battle-Modders/Dynamic-Perks-Framework',
	'Dynamic Spawns': 'Battle-Modders/Dynamic-Spawns-Framework',
	'Item Tables': 'Battle-Modders/Item-Tables-Framework',
	'Stack Based Skills': 'Battle-Modders/stack-based-skills',
	'Unified Perk Descriptions (UPD)': 'Battle-Modders/Unified-Perk-Descriptions',
}


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    print("\nRunning on the following guilds:")
    for guild in client.guilds:
        print('\t' + guild.name)


def parse_log(log: str) -> dict:
    embed = discord.Embed()
    newestBBversion = '1.5.0.15'
    allCurrent = True
    def compare_versions(installed: str, newest: str) -> str:
        nonlocal allCurrent
        if installed == newest:
            return f':white_check_mark: {installed}'
        else:
            allCurrent = False
            return f':x: {installed} < {newest}'

    installedBBversion = re.search(r"<html><head><title>Battle Brothers ([\d\.]*.?)</title>", log).group(1)
    embed.add_field(name='BB Version', value=compare_versions(installedBBversion, newestBBversion), inline=False)
    print(installedBBversion, newestBBversion)
    for name, repo in mods.items():
        installed = re.search(rf"<span style=\"color:#FFFFFF\">{re.escape(name)}</span> (?:.*?) version <span (?:.*?)>([\d\.]*.?)</span>", log).group(1)

        url = f'https://api.github.com/repos/{repo}/releases'
        headers = {'Accept': 'application/vnd.github+json'}
        r = requests.get(url, auth=('Osgboy', GITHUB_TOKEN), headers=headers)
        newest = r.json()[0]['tag_name']

        if installed is None:
            value = ':x: Not Installed'
            allCurrent = False
        else:
            value = compare_versions(installed, newest)
        embed.add_field(name=name, value=value)
        print(installed, newest)

    return {
        "AllCurrent" : allCurrent,
        "embed" : embed
    }

@client.event
async def on_message(message: discord.Message):
    print(message.content)
    for attachment in message.attachments:
        if attachment.filename == 'log.html' and attachment.content_type[:5] == 'text/':
            if attachment.size <= 10000000:
                log = await attachment.read()
                parse_result = parse_log(str(log, 'UTF-8'))
                if not parse_result["AllCurrent"]:
                    embed = parse_result["embed"]
                    embed.title = f"{message.author.display_name}'s Log Version Check"
                    embed.color = discord.color.red()
                    await message.channel.send(embed=embed)
            else:
                await message.channel.send("Log file exceeds 10 MB!")


client.run(DISCORD_TOKEN)
