
import discord, os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
#SERVER = os.getenv('SERVER_TOKEN')

client = discord.Client()

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    print(client.guilds)

@client.event
async def on_message(message):
    if message.content.lower() == '~help':
        await message.channel.send(msgHelp(message))
    elif message.content.lower() == "~random":
        await message.channel.send(file=randomImg(message))

def msgHelp(message):
    helpText = "This bot is a work in progress, please be gentle\n" \
               "~help to see this message again\n"
    return helpText

def randomImg(message):
    with open('SourceImages/The Pillars of Creation.jpg', 'rb') as f:
        picture = discord.File(f)
        return picture


client.run(TOKEN)