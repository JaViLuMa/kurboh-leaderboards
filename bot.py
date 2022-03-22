import os
import discord
import requests

from dotenv import load_dotenv
from discord.ext import tasks, commands

load_dotenv()

API_URL           = "https://osu.ppy.sh/api/v2"
TOKEN_URL         = "https://osu.ppy.sh/oauth/token"
DISCORD_TOKEN     = os.getenv('DISCORD_TOKEN')
OSU_CLIENT_SECRET = os.getenv('OSU_CLIENT_SECRET')
ID_s = [
        933020,
        14268402,
        15601511,
        19713229,
        8778784,
        15565433,
        24069825,
        17440873,
        22730236,
        18688996,
        28674381,
        3832576,
        15243233,
        23303765
]

bot = discord.Client()


def get_token():
    data = {
        "client_id":     int(os.getenv('CLIENT_ID')),
        "client_secret": OSU_CLIENT_SECRET,
        "grant_type":    "client_credentials",
        "scope":         "public"
    }

    response = requests.post(TOKEN_URL, data=data)

    return response.json().get("access_token")


def osu_api_things():
    infos = []

    token = get_token()

    headers = {
        "Content-Type":  "application/json",
        "Accept":        "application/json",
        "Authorization": f"Bearer {token}"
    }


    for id in ID_s:
        response = requests.get(f"{API_URL}/users/{id}/osu", headers=headers)

        pp       = response.json().get("statistics").get("pp")
        username = response.json().get("username")

        infos.append({
            "username": username,
            "pp": pp,
        })

    infos = sorted(infos, key=lambda d: d['pp'], reverse=True) 

    return infos


@bot.event
async def on_ready():
    print("I am ready!")
    
    auto_send.start()


@tasks.loop(minutes=60.0)
async def auto_send():
    embed = discord.Embed()

    embed = discord.Embed(title="Kurb's Circular Boat leaderboard!")
    embed.set_author(name="JaViLuMa", url="https://github.com/JaViLuMa")

    infos = osu_api_things()
    
    for count, info in enumerate(infos):
        embed.add_field(name=count + 1, value=f'{info["username"]} - {info["pp"]}', inline=False)

    channel = await bot.fetch_channel('954512449040678932')

    await channel.send(embed=embed, delete_after=3600.0)


bot.run(DISCORD_TOKEN)