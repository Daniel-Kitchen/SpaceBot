import discord, os, random, time
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')

allImgs = os.listdir("SourceImages")
imgStore = allImgs.copy()
rollQueue = []
userDict = {}

client = discord.Client()


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')


@client.event
async def on_message(message):
    if message.content.lower() == '~help':
        await message.channel.send("Check your dms for a list of all commands available! Have fun!")
        await message.author.send(msgHelp())
    elif message.content.lower() == "~random":
        imgName = randomImg()
        image = "SourceImages/" + imgName
        await message.channel.send(content="Your random space image is: " + os.path.splitext(imgName)[0],
                                   file=discord.File(image))
    elif message.content.lower() == "~roll":
        await roll(message)
    elif message.content.lower() == "~spacebase":
        await sendImgs(message)
    elif message.content.lower() == "~basetxt":
        await sendTxt(message)
    elif message.content.lower()[:4] == "~rem":
        await rem(message)
    elif message.content.lower() == "~credits":
        await message.author.send(botCredits())
    elif message.content.lower() == "good bot":
        await message.channel.send("Good {}".format(message.author.mention))


def botCredits():
    msg = "This bot is developed by Daniel \"Kitch\" Kitchen for the 2020 BAS Hackathon\n" \
          "Contact info: \n" \
          "Discord: Kitch#2846 \n" \
          "Twitter: https://twitter.com/Kitch_Bread\n" \
          "Buy me a coffee here :) https://paypal.me/danielkitchen58"
    return msg


async def sendTxt(message):
    name = message.author.name
    txtMsg = ""
    if name in userDict.keys():
        txtMsg += "Hello {}, here are all of the images you have in your space base!\n".format(message.author.mention)
        for imgs in userDict.get(name):
            txtMsg += str(imgs)[str(imgs).find("/") + 1:str(imgs).find(".")] + "\n"
    else:
        txtMsg += "{}, you don't have any images in your Space Base!\nUse ~roll to pick some out!".format(
            message.author.mention)
    await message.channel.send(txtMsg)


async def rem(message):
    name = message.author.name
    if name in userDict.keys():
        for imgs in userDict.get(name):
            imgsName = str(imgs)[str(imgs).find("/") + 1:str(imgs).find(".")]
            if imgsName.lower() == message.content.lower()[5:]:
                print(imgStore)
                userDict[name].remove(imgs)
                await message.channel.send("{} has been removed from your space base and inserted back into the store!"
                                           .format(imgsName))
                imgStore.append(str(imgs[str(imgs).find("/") + 1:]))


@client.event
async def on_reaction_add(reaction, user):
    for obj in rollQueue:
        if obj[0].id == reaction.message.id and user.name != "Spaaaaaaaaaaaaaace" and not \
                time.time() - obj[2] > 60:
            await addToSpaceBase(obj, user, reaction)

        elif time.time() - obj[2] > 60 and user.name != "Spaaaaaaaaaaaaaace":
            img = obj[4]
            await obj[0].edit(content="{} has been returned to the queue due to inactivity!".format(img))
            imgStore.append(img)
            rollQueue.remove(obj)


async def addToSpaceBase(obj, user, reaction):
    ogName = obj[1].name
    if ogName == user.name:
        if ogName in userDict.keys():
            userDict[ogName].append(obj[3])
        else:
            userDict[ogName] = [obj[3]]
        rollQueue.remove(obj)
        await reaction.message.channel.send("*{}* has been claimed by: {}".format(str(obj[3])[str(obj[3]).find("/") + 1:
                                                                                              str(obj[3]).find(".")],
                                                                                  user.mention))
    elif time.time() - obj[2] > 10:
        if user.name in userDict.keys():
            userDict[user.name].append(obj[3])
        else:
            userDict[user.name] = [obj[3]]
        rollQueue.remove(obj)
        await reaction.message.channel.send("*{}* has been claimed by: {}".format(str(obj[3])[str(obj[3]).find("/") + 1:
                                                                                              str(obj[3]).find(".")],
                                                                                  user.mention))
    else:
        await reaction.message.channel.send("{}, please give {} 10 seconds to claim the image!".format(user.mention,
                                                                                                       obj[1].mention))
        await reaction.remove(user)


def msgHelp():
    helpText = "***This bot is a work in progress, please be gentle***\n" \
               "**~help** to see this message again\n" \
               "**~random** to see a random image of space\n" \
               "**~roll** to generate a random image. React to the image to claim it\n" \
               "* Note: You have 10 seconds to claim this image for yourself before it opens to the whole server!\n" \
               "* Note: The opportunity for any user to claim an image expires after 60 seconds\n" \
               "**~SpaceBase** to see all of the images in your space base sent to your dms!\n" \
               "**~BaseTxt** to see the names of all of the images you have in your Space Base\n" \
               "**~Rem [\"imagename\"]** to remove an image from your Space Base and put it back in the pool\n" \
               "**~Credits** for information about the developer and this project"
    return helpText


def randomImg():
    rand = random.randint(0, len(allImgs) - 1)
    image = allImgs[rand]
    return image


async def roll(message):
    msgId = await message.channel.send("Rolling images...")
    msgId = msgId.id
    result = await message.channel.fetch_message(msgId)
    if len(imgStore) < 1:
        imgName = randomImg()
        image = "SourceImages/" + imgName
        await result.delete()
        await message.channel.send(
            content="I've run out of source images! Here's a random image, go yell at Kitch to add more.",
            file=discord.File(image))
    else:
        rand = random.randint(0, len(imgStore) - 1)
        imgName = imgStore[rand]
        image = "SourceImages/" + imgName
        imgStore.pop(rand)
        await result.delete()
        result = await message.channel.send(content="Your random space image is: " + os.path.splitext(imgName)[0],
                                            file=discord.File(image))
        result = result.id
        result = await message.channel.fetch_message(result)
        await result.add_reaction("👾")
        rollQueue.append([result, message.author, time.time(), image, imgName])


async def sendImgs(message):
    name = message.author.name
    if name in userDict.keys():
        for imgs in userDict.get(name):
            await message.author.send(content=str(imgs)[str(imgs).find("/") + 1:str(imgs).find(".")],
                                      file=discord.File(imgs))
    else:
        await message.author.send("You don't have any images in your Space Base!\n"
                                  "use ~roll to pick some out!")
    await message.channel.send("DM sent! If you didn't receive it, please open your dms to members from this server!")


client.run(TOKEN)
