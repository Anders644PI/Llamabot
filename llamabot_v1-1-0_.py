#!/usr/bin/env python

# Llamabot.py: Discord bot for High Llama Gaming.
#
# __author__      = "Anders 'A7ELEVEN' Severinsen"
# __copyright__   = "Copyright 2022, Denmark, Planet Earth"
# __version__     = "1.1.0_"

version = "1.1.0_"

import discord
from discord.utils import get
import asyncio
import time
import random
import re   # Used for spliting strings
from datetime import datetime   # Used to get the time and date
import twitter  # Used to get tweets
#import os

intents = discord.Intents.all()
client = discord.Client(intents=intents)

# Admin Configs
rankToGetRoleLlamazing = 50     # <--- Change this to change the number of messages a user needs to type, in order to get the exclusive role
rankToGetRoleLlamember = 15     # <--- Change this to change the number of messages a user needs to type, in order to get the exclusive role

intents = discord.Intents.default()
intents.members = True  # Subscribe to the privileged members intent.
attachedvideo = ["https://"]
listOfBotUserIds = []

pathToRanksFile = "ranks.txt" #"/home/pi/ranks.txt"
pathToListOfBotUserIdsFile = "listofbotuserids.txt" #"/home/pi/listofbotuserids.txt" # (v1.1.0)

# Start up the MusicBot, to run alongside the main program (v1.0.24)
# https://just-some-bots.github.io/MusicBot/
#os.system("sudo /home/pi/MusicBot/./run.sh &")

# Twitter (v1.0.10)
CONSUMER_KEY = 'CONSUMER_KEY'
CONSUMER_SECRET = 'CONSUMER_SECRET'
OAUTH_TOKEN = 'OAUTH_TOKEN'
OAUTH_TOKEN_SECRET = 'OAUTH_TOKEN_SECRET'

auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET,
                           CONSUMER_KEY, CONSUMER_SECRET)

twitter_api = twitter.Twitter(auth=auth)

# https://developer.twitter.com/en/docs/tweets/timelines/api-reference/get-statuses-user_timeline
tweets_data = twitter_api.statuses.user_timeline(count='10',
                                                 screen_name='elonmusk')

# Rank Decrease (v1.0.11)
begin = time.time()
decreaseFactor = 1
secondsBeforeRankDecrease = 60 * 60 * 12

def coolDownCheck(cooldowntime):
    cooldownMin = 2                         # <-- Change cooldown threshold (in minutes) here
    now = datetime.now().strftime("%d:%H:%M")
    timeNow = re.split('[:\n]', now)
    #print(timeNow, end=" }{ ")
    #print(cooldowntime)
    # Date
    if int(timeNow[0]) - int(cooldowntime[0]) > 2:
        return True
    # Hour
    elif int(timeNow[1]) - int(cooldowntime[1]) > 2:
        return True
    # Minute
    else:
        if int(timeNow[2]) - int(cooldowntime[2]) >= 0:
            if int(timeNow[2]) - int(cooldowntime[2]) > cooldownMin:
                return True
        else:
            if int(timeNow[2]) - int(cooldowntime[2]) > -59+cooldownMin:
                return True
    return False

@client.event
async def on_ready():
    # Setting `Watching ` status
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="!llama"))
    print("[bot ready]")

async def react(message):
    custom_emojis = [
    "<:upvote:869268974007881739>",                          # emoji ids need the quotations ie. "" keep them                                          
    "<:downvote:869269286185734254>"
    ]
    guild_emoji_names = [str(guild_emoji) for guild_emoji in message.guild.emojis]
    for emoji in custom_emojis:
        #print(emoji, guild_emoji_names)                # debugging your shite remove the "#" if you wanna see print in cmd console
        #print(emoji in guild_emoji_names)
        if emoji in guild_emoji_names:
            await message.add_reaction(emoji)

# (v1.0.13)
async def getguild(guild_id):
    guild = client.get_guild(guild_id)

    if not guild:
        guild = await client.fetch_guild(guild_id)

    return guild

@client.event
async def on_message(message):
    # Make sure the message is not from Llamabot
    notBotMessage = True
    for i in listOfBotUserIds:
        if str(message.author.id) == i:
            notBotMessage = False
            #print("Bot message detected")

    if notBotMessage:
        user_message = str(message.content)

        # Print out the received message
        #print("[Message content]\n" + user_message)
        #print("[Message content End]")

        # Check if the message is an image
        if user_message == None or user_message == "":    # message.channel.id == 769578695026802729 and 
            # React to the message, by calling the react() function
            await react(message)
        else:
            # Check if the message is an image or video link
            for i in attachedvideo:
                if i in user_message:
                    # React to the message, by calling the react() function
                    await react(message)

        # Variables
        userrank = 0
        userfound = False

        # Open the file containing the current user ranks
        f = open(pathToRanksFile, "r")

        ranks = list(f)

        # Not needed, but good for Debug
        #print("[User ranks:]")
        #for i in ranks:
        #    print(i, end='')
        #print("\n[User ranks End]")
        #print("[Message Author Id]: " + str(message.author.id))

        newRank = False
        j = 0
        for i in ranks:
            if i.find(str(message.author.id)) != -1:
                #print("[Message user found! Checking Cooldown]")
                userCooldowntime = ranks[j+2]
                cooldowntime = re.split('[:\n]', userCooldowntime)
                userrank = int(ranks[j+1])
                if coolDownCheck(cooldowntime):
                    #print("[Rank Cooldown over! Adding _+1_ to rank]")
                    newRank = True
                    userrank +=1
                    ranks[j+1] = str(userrank) + "\n"
                    #print("New user rank: " + str(ranks[j+1]), end="")

                    # v1.0.6 Rank Cooldown
                    now = datetime.now()
                    #print("[Adding New Rank Cooldown. Time now: "+now.strftime("%d:%H:%M:%S")+"]")
                    ranks[j+2] = now.strftime("%d:%H:%M\n")
                userfound = True
            j +=1
        f.close()

        if userfound == False:
            #print("[Message user not found! Adding new rank]")
            ranks.append(str(message.author.id)+"\n")
            ranks.append("1\n")
            now = datetime.now()
            ranks.append(now.strftime("%d:%H:%M")+"\n")

        if newRank:
            #print("[New User ranks:]")
            #for i in ranks:
            #    print(i, end='')
            #print("\n[New User ranks End]")

            # If the user reaches the decided rank
            if userrank == rankToGetRoleLlamember:
                #print("[User earned Llamember!]")
                member = message.author
                role = get(member.guild.roles, name='Llamember')
                await member.add_roles(role)
                await message.channel.send(f"You did it {member.mention}! :partying_face: You have now earned the **Llamember** role, to show that you are an active member on the server!")

            # If the user reaches the decided rank
            if userrank == rankToGetRoleLlamazing:
                #print("[User earned Llamazing!]")
                member = message.author
                role = get(member.guild.roles, name='Llamazing')
                await member.add_roles(role)
                await message.channel.send(f"You did it {member.mention}! :heart_eyes: You have now earned the **Llamazing** role, because you help make this server better 4 everyone!")

        # Opdating user ranks file with new ranks
        f = open(pathToRanksFile, "w")
        f.writelines(ranks)
        f.close()

        # User command to get current rank
        if user_message == "!rank":
            async with message.channel.typing():
                await asyncio.sleep(1)
                member = message.author
                if userrank >= rankToGetRoleLlamazing:
                    await message.channel.send(f"{member.mention} your current rank is **{userrank}** :exploding_head:")
                elif userrank >= rankToGetRoleLlamember:
                    await message.channel.send(f"{member.mention} your current rank is **{userrank}** :pleading_face:\nYou need to reach rank **{rankToGetRoleLlamazing}**, to get the exclusive **Llamazing** role. Be more active on the server!")
                else:
                    await message.channel.send(f"{member.mention} your current rank is **{userrank}** :grin:\nYou need to reach rank **{rankToGetRoleLlamember}**, to get the exclusive **Llamember** role. Type some more!")

        # User command to get current rank
        elif user_message == "!ping":
            async with message.channel.typing():
                member = message.author
                await asyncio.sleep(1)
                await message.channel.send("pong :ping_pong:")
        
        # User command to get current rank
        elif user_message == "!version":
            member = message.author
            await message.channel.send(f"v{version}")

        # User command to get current rank
        elif user_message == "!elon":
            async with message.channel.typing():
                await asyncio.sleep(1)
                tweetNotFound = True
                member = message.author
                try:
                    for trending in tweets_data:
                        if tweetNotFound:
                            tweetText = trending['text']
                            tweetDate = trending['created_at']
                            if tweetText.find("@") != -1:
                                pass
                            else:
                                #print(f"'{tweetText}' - Liked by {trending['favorite_count']} people")
                                tweetNotFound = False
                    em = discord.Embed(title = f"{tweetText}", color = discord.Color(0x510580))
                    em.add_field(name = f"*- Elon Musk, {tweetDate}*" , value = f"{trending['favorite_count']} likes",  inline = False) # tweetDate[0:10]
                    await message.channel.send(embed = em)
                except:
                    await message.channel.send(f"ERROR :cold_sweat: Could not process tweet")

        # User command to get current leaderboard (v1.0.7)
        elif user_message == "!leaderboard":
            async with message.channel.typing():
                await asyncio.sleep(1)
                leaderboardTopX = 5
                # Open the file containing the current user ranks
                f = open(pathToRanksFile, "r")
                ranks = list(f)
                leaderboard = []
                ranksList = []
                for i in ranks:
                    ranksList.append(i.replace('\n', ''))

                for i in range(int(len(ranksList)/3)):
                    user_id = ranksList[0+i*3]
                    userName = await client.fetch_user(user_id)
                    #print(userName)
                    if i == 0:
                        new_list = [int(ranksList[1+i*3]), userName]
                        leaderboard.append(new_list)
                    else:
                        for j in range(len(leaderboard)):
                            #print(int(leaderboard[j][0]))
                            if int(ranksList[1+i*3]) >= int(leaderboard[j][0]):
                                new_list = [int(ranksList[1+i*3]), userName]
                                leaderboard.insert(j, new_list)
                                break
                            elif j == len(leaderboard)-1:
                                new_list = [int(ranksList[1+i*3]), userName]
                                leaderboard.append(new_list)
                emoteList = [":first_place:", ":second_place:", ":third_place:", ":four:", ":five:"]
                em = discord.Embed(title = f"Current Top {leaderboardTopX}" , description = f"List of the current Top {leaderboardTopX} from the leaderboard",color = discord.Color(0x3b96ff))
                for i in range(leaderboardTopX):
                    em.add_field(name = f"{emoteList[i]} {leaderboard[i][1]}" , value = f"{leaderboard[i][0]}",  inline = False)
                await message.channel.send(embed = em)
                f.close()

        # BotUserIds (v1.1.0)
        elif "!addbotuser" in user_message:
            async with message.channel.typing():
                await asyncio.sleep(1)
                um = list(user_message.split(" "))
                if len(um) > 1:
                    f = open(pathToListOfBotUserIdsFile, "a")
                    for i in range(len(um)-1):
                        f.write(f"{um[i+1]}\n")
                    f.close()
                    botUserIds()
                    if len(um) > 2:
                        await message.channel.send(f"Succesfully added {len(um)-1} bots")
                    else:
                        await message.channel.send(f"Succesfully added {len(um)-1} bot")
                else:
                    await message.channel.send(f"No bot ids found :face_with_monocle:")

        # User commands list (v1.0.8)
        elif user_message == "!llama":
            async with message.channel.typing():
                await asyncio.sleep(1)
                # Open the file containing the current user ranks
                commandsList = ["!rank", "!leaderboard", "!elon", "!8ball", "!llama"]
                commandsListDesc = ["Lists the available commands for Llamabot", "Prints out your current rank", "Lists the current leaderboard", "Posts the most recent tweet from Elon Musk", "Ask a Yes or No question. Like this '!yesorno Do you like ice cream?'"]

                em = discord.Embed(title = f"Llamabot available commands :triangular_flag_on_post:" ,color = discord.Color(0x3b96ff))
                for i in range(len(commandsList)):
                    em.add_field(name = f"{commandsList[i]}" , value = f"{commandsListDesc[i]}",  inline = False)
                await message.channel.send(embed = em)

        # Magic 8 Ball (v1.0.12)
        if len(user_message) >= 8:
            if user_message.startswith("!8ball"):
                async with message.channel.typing():
                    await asyncio.sleep(1)
                    if user_message[9:] != "":
                        answers = ["It is Certain", " It is decidedly so", "Without a doubt","Yes definitely", "You may rely on it", "As I see it, yes", "Most likely", "Outlook good", "Yes", "Signs point to yes", "Reply hazy, try again", "Ask again later", "Better not tell you now", "Cannot predict now", "Concentrate and ask again", "Don't count on it", "My reply is no", "My sources say no", "Outlook not so good", "Very doubtful", "Are you seriously asking a computer that question?!"]
                        n = random.randint(0, len(answers))
                        await message.reply(f"{answers[n]}")
                    else:
                        await message.reply(f"Ask a Yes or No question. Like this: '!8ball Do you like ice cream?'")

# BotUserIds (v1.1.0)
def botUserIds():
    global listOfBotUserIds

    f = open(pathToListOfBotUserIdsFile, "r")
    listOfBotUserIds = []
    for i in f:
        listOfBotUserIds.append(i.replace('\n', ''))

# RankDecrease (v1.0.14)
async def rankDecrease():
    while True:
        await client.wait_until_ready()
        global begin
        TimeRunning = time.time() - begin
        if TimeRunning / secondsBeforeRankDecrease > 1:
            #print(f"[Ranks are being decreased]")
            begin = time.time()

            # Open the file containing the current user ranks
            f = open(pathToRanksFile, "r")
            ranks = list(f)
            ranksList = []
            for i in ranks:
                ranksList.append(i.replace('\n', ''))

            for i in range(int(len(ranksList)/3)):
                if int(ranksList[1+i*3]) >= rankToGetRoleLlamember + decreaseFactor:
                    ranks[1+i*3] = f"{int(ranksList[1+i*3])-decreaseFactor}\n"
                    if int(ranksList[1+i*3]) == rankToGetRoleLlamazing:
                        #print("[User lost Llamazing]")
                        user_id = ranksList[i*3]
                        userName = await client.fetch_user(user_id)
                        #print(userName)
                        #member = message.author
                        guild_id = 482069891990421514
                        guild = client.get_guild(guild_id)
                        #print(guild)
                        #user = client.get_member(user_id)
                        #print(user)
                        member = await guild.fetch_member(user_id)
                        #print(member)
                        role = get(guild.roles, name='Llamazing')
                        #role = "Llamazing"
                        await member.remove_roles(role)
                        channel = client.get_channel(768475825347493928)

                        llamoderator = get(guild.roles, name='Llamoderator')
                        await channel.send(f"{member.mention} lost Llamazing :sob:")
                elif int(ranksList[1+i*3]) == rankToGetRoleLlamember or int(ranksList[1+i*3]) == rankToGetRoleLlamember+1:
                    ranks[1+i*3] = f"15\n"
            f.close()

            # Opdating user ranks file with new ranks
            f = open(pathToRanksFile, "w")
            f.writelines(ranks)
            f.close()
        await asyncio.sleep(1)


while True:
    try:
        botUserIds()
        client.run("TOKEN")

        # RankDecrease (v1.0.14)
        client.loop.create_task(rankDecrease())
    except:
        time.sleep(5)