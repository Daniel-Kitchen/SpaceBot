import discord, os, random
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
#SERVER = os.getenv('SERVER_TOKEN')

allImgs = os.listdir("SourceImages")
imgStore = allImgs.copy()
rollQueue = []
userDict = {}

client = discord.Client()

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    print(client.guilds)

@client.event
async def on_message(message):
    if message.content.lower() == '~help':
        await message.channel.send(msgHelp())
    elif message.content.lower() == "~random":
        imgName = randomImg()
        image = "SourceImages/" + imgName
        await message.channel.send("Your random space image is: " + os.path.splitext(imgName)[0])
        await message.channel.send(file=discord.File(image))
    elif message.content.lower() == "~roll":
        await roll(message)
    elif message.content.lower() == "~spacebase":
        await sendImgs(message)


@client.event
async def on_reaction_add(reaction, user):
    for obj in rollQueue:
        if obj[0].content == reaction.message.content and user.name != "Spaaaaaaaaaaaaaace":
            await addToSpaceBase(obj, reaction, user)


async def addToSpaceBase(obj, reaction, user):
    ogName = obj[1]
    if ogName == user.name:
        if ogName in userDict.keys():
            userDict[ogName].append(obj[3])
        else:
            userDict[ogName] = [obj[3]]
        rollQueue.remove(obj)


def msgHelp():
    helpText = "This bot is a work in progress, please be gentle\n" \
               "~help to see this message again\n" \
               "~random to see a random image of space\n" \
               "~roll to generate a random image. React to the image to claim it\n" \
               "~SpaceBase to see all of the images in your space base sent to your dms!"
    return helpText


def randomImg():
    rand = random.randint(0, len(allImgs)-1)
    image = allImgs[rand]
    return image


async def roll(message):
    msgId = await message.channel.send("Rolling images...")
    msgId = msgId.id
    result = await message.channel.fetch_message(msgId)
    if len(imgStore) < 1:
        await result.edit(content="I've run out of source images! Here's a random image, go yell at Kitch to add more")
        imgName = randomImg()
        image = "SourceImages/" + imgName
        await message.channel.send(file=discord.File(image))
    else:
        rand = random.randint(0, len(imgStore) - 1)
        imgName = imgStore[rand]
        image = "SourceImages/" + imgName
        imgStore.pop(rand)
        await result.edit(content="Your random space image is: " + os.path.splitext(imgName)[0])
        result = await message.channel.send(file=discord.File(image))
        result = result.id
        result = await message.channel.fetch_message(result)
        await result.add_reaction("👾")
        rollQueue.append([result, message.author.name, datetime.now(), image])


async def sendImgs(message):
    name = message.author.name
    if name in userDict.keys():
        for imgs in userDict.get(name):
            await message.author.send(file=discord.File(imgs))
    else:
        await message.author.send("You don't have any images in your Space Base!\n"
                                  "use ~roll to pick some out!")
    await message.channel.send("DM sent! If you didn't receive it, please open your dms to members from this server!")

client.run(TOKEN)
