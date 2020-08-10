import discord, os, random, time
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')  # Bot's secret token

allImgs = os.listdir("SourceImages")  # List of source images
imgStore = allImgs.copy()  # Copy of list of source images, is a bank for the rolling game
rollQueue = []  # Stored rolls that have not been reacted to yet
userDict = {}  # List of all users and their Space Base's content

client = discord.Client()


@client.event
async def on_ready():
    """
    Built-in Discord.py client event.
    Displays to console on successful instantiation of the bot
    """
    print(f'{client.user} has connected to Discord!')


@client.event
async def on_message(message):
    """
    Built-in Discord.py client event.
    Handles all commands and user input.
    :param message: The user that sent a request to the bot
    """
    if message.content.lower() == 'sb!help':
        await message.channel.send("Check your dms for a list of all commands available! Have fun!")
        await message.author.send(msgHelp())
    elif message.content.lower() == "sb!random":
        imgName = randomImg()
        image = "SourceImages/" + imgName
        await message.channel.send(content="Your random space image is: " + os.path.splitext(imgName)[0],
                                   file=discord.File(image))
    elif message.content.lower() == "sb!roll":
        await roll(message)
    elif message.content.lower() == "sb!spacebase":
        await sendImgs(message)
    elif message.content.lower() == "sb!basetxt":
        await sendTxt(message)
    elif message.content.lower()[:6] == "sb!rem":
        await rem(message)
    elif message.content.lower() == "sb!credits":
        await message.author.send(botCredits())
    elif message.content.lower() == "good bot":
        await message.channel.send("Good {}".format(message.author.mention))
    elif message.content.lower()[:9] == "sb!showme":
        await showme(message)
    elif message.content.lower() == "bad bot":
        await message.channel.send("Bad {}".format(message.author.mention))
    elif message.content.lower()[:11] == "sb!peekbase":
        await peekBase(message)


async def showme(message):
    """
    Shows the user the specific image they are requesting, if available
    :param message: The image they are requesting
    """
    img = message.content[10:] + ".jpg"
    if img in allImgs:
        img = "SourceImages/" + img
        await message.channel.send(content="Here is {}, {}!".format(message.content[10:], message.author.mention),
                                   file=discord.File(img))
    else:
        await message.channel.send("Sorry, I don't know that image! Please make sure your request has proper casing!")

def botCredits():
    """
    All about me : )
    :return: returns a string to be dmed to the user
    """
    msg = "This bot is developed by Daniel \"Kitch\" Kitchen for the 2020 BAS Hackathon\n" \
          "Contact info: \n" \
          "Discord: Kitch#2846 \n" \
          "Twitter: https://twitter.com/Kitch_Bread\n" \
          "Buy me a coffee here :) https://paypal.me/danielkitchen58"
    return msg


async def sendTxt(message):
    """
    Sends the user a list of all of their Space Base's content in text form, so that they can see more easily what they
    have.
    :param message: The user making the request
    """
    name = message.author.name
    txtMsg = ""
    if name in userDict.keys():
        txtMsg += "Hello {}, here are all of the images you have in your space base!\n".format(message.author.mention)
        for imgs in userDict.get(name):
            txtMsg += str(imgs)[str(imgs).find("/") + 1:str(imgs).find(".")] + "\n"
    else:
        txtMsg += "{}, you don't have any images in your Space Base!\nUse sb!roll to pick some out!".format(
            message.author.mention)
    await message.channel.send(txtMsg)


async def peekBase(message):
    """
    View another user's Space Base in text form
    :param message: The user making the request, with the other user's name
    """
    requester = message.author
    try:
        requested = await client.fetch_user(message.content[message.content.find(" ")+4:len(message.content)-1])
        txtMsg = ""
        if requested.name in userDict.keys():
            txtMsg += "Hello {}, here are all of the images in {}'s Space Base!\n".format(requester.mention, requested.name)
            for imgs in userDict.get(requested.name):
                txtMsg += str(imgs)[str(imgs).find("/") + 1:str(imgs).find(".")] + "\n"
        else:
            txtMsg += "{}, {} doesn't have any images in their Space Base!\nTell them to use sb!roll to pick some out!"\
                .format(requester.mention, requested.name)
        await message.channel.send(txtMsg)
    except Exception:
        await message.channel.send("{}, there is no one in this server with that name! Please make sure you do\n"
                                   "sb!peekbase @[username]".format(requester.mention))


async def rem(message):
    """
    Removes an image from the user's Space Base
    :param message: The user making the request
    """
    name = message.author.name
    if name in userDict.keys():
        for imgs in userDict.get(name):
            imgsName = str(imgs)[str(imgs).find("/") + 1:str(imgs).find(".")]
            if imgsName.lower() == message.content.lower()[7:]:
                userDict[name].remove(imgs)
                await message.channel.send("{} has been removed from your space base and inserted back into the store!"
                                           .format(imgsName))
                imgStore.append(str(imgs[str(imgs).find("/") + 1:]))


@client.event
async def on_reaction_add(reaction, user):
    """
    Built-in Discord.py event
    When a reaction is added, find the image it is responding to, make sure it is a user and that the image is not too
    old, and then try to add it to their Space Base
    :param reaction: The message being reacted to
    :param user: The user reacting to it
    """
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
    """
    Takes an image and adds it to their space base if they satisfy the conditions of the game
    :param obj: The image in question
    :param user: The user in question
    :param reaction: The channel the reaction was made in
    """
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
    """
    Help message with a list of all commands
    :return: A text string to be dmed to the user
    """
    helpText = "***Developed for the BAS Hackathon 2020, sb!Credits for more info!***\n" \
               "**sb!help** to see this message again\n" \
               "**sb!random** to see a random image of space\n" \
               "**sb!roll** to generate a random image. React to the image to claim it\n" \
               "* Note: You have 10 seconds to claim this image for yourself before it opens to the whole server!\n" \
               "* Note: The opportunity for any user to claim an image expires after 60 seconds\n" \
               "**sb!SpaceBase** to see all of the images in your space base that you have claimed sent to your dms!\n" \
               "**sb!BaseTxt** to see the names of all of the images you have in your Space Base\n" \
               "**sb!Rem [\"imagename\"]** to remove an image from your Space Base and put it back in the pool\n" \
               "**sb!Credits** for information about the developer and this project\n" \
               "**good bot** no u"
    return helpText


def randomImg():
    """
    Generates a random image for the user from the SourceImages folder
    :return: random image
    """
    rand = random.randint(0, len(allImgs) - 1)
    image = allImgs[rand]
    return image


async def roll(message):
    """
    Rolls a random image from the currently available bank
    :param message: Allows the bot to recall where the message was sent, and who the message was sent by
    """
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
    """
    Sends all of a user's Space Base to them in dms
    :param message: The user that made the request
    """
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
