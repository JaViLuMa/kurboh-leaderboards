import os
import gspread
import discord
import requests

from dotenv import load_dotenv
from discord.ext import tasks, commands

load_dotenv()

API_URL            = "https://osu.ppy.sh/api/v2"
TOKEN_URL          = "https://osu.ppy.sh/oauth/token"
DISCORD_TOKEN      = os.getenv('DISCORD_TOKEN')
OSU_CLIENT_SECRET  = os.getenv('OSU_CLIENT_SECRET')
DISCORD_CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID_MAIN')
GOOGLE_SPREADS     = gspread.service_account(filename='./data.json')
SPECIFIC_SHEET     = GOOGLE_SPREADS.open("kurbohLeaderboard")
WORKSHEET          = SPECIFIC_SHEET.get_worksheet(0)

bot = commands.Bot(command_prefix="!!")


def get_token():
    data = {
        "client_id":     int(os.getenv('CLIENT_ID')),
        "client_secret": OSU_CLIENT_SECRET,
        "grant_type":    "client_credentials",
        "scope":         "public"
    }

    response = requests.post(TOKEN_URL, data=data)

    return response.json().get("access_token")


token = get_token()

headers = {
    "Content-Type":  "application/json",
    "Accept":        "application/json",
    "Authorization": f"Bearer {token}"
}


def osu_api_things():
    infos = []

    ID_s = WORKSHEET.col_values(1)
    ID_s.pop(0)

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


def nextAvailableRow(worksheet):
  filteredStringList = list(filter(None, worksheet.col_values(1)))

  return str(len(filteredStringList) + 1)


def playerChecker(id):
    if id.isdecimal() == False:
        return "Please enter a valid osu! ID."
    else:
        try:
            response     = requests.get(f"{API_URL}/users/{id}/osu", headers=headers)

            matchingCell = WORKSHEET.find(id)

            if matchingCell:
                return f"{id} is already in the leaderboard."

            pp      = response.json().get("statistics").get("pp")

            nextRow = nextAvailableRow(WORKSHEET)

            WORKSHEET.update_acell(f"A{nextRow}", id)

            return "Player has been successfully added"

        except:
            return "Please add a player that isn't restricted, deleted or doesn't exist. Also make sure you didn't make any typos!"


@bot.event
async def on_ready():
    print("I am ready!")
    
    auto_send.start()


@bot.command()
async def id(ctx, arg):
	await ctx.send(playerChecker(arg))


@tasks.loop(minutes=60.0)
async def auto_send():
    embed = discord.Embed()

    embed = discord.Embed(title="Kurb's Circular Boat leaderboard!")
    embed.set_author(name="JaViLuMa", url="https://github.com/JaViLuMa")

    infos = osu_api_things()
    
    for count, info in enumerate(infos):
        embed.add_field(name=count + 1, value=f'{info["username"]} - {info["pp"]}', inline=False)

    channel = await bot.fetch_channel(DISCORD_CHANNEL_ID)

    await channel.send(embed=embed, delete_after=3600.0)


bot.run(DISCORD_TOKEN)
