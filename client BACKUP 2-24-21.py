# client.py BACKUP from 3:14PM 2-24-21 before using bot.command(). 

import asyncio
import discord
from prefix import getPrefix, changePrefix
import commands
import reactions
import asyncioTest
from globalVariables import reactionMessageIDs, openLobbies
import backgroundTasks
from discord_slash import SlashCommand



#logging.basicConfig(level=logging.INFO)

TOKEN = "NzM2NDE4MDkwNjI3MjM1OTUx.Xxugyg.9SN5blnqxFDBnre2lqgjZUFDrGk"

client = discord.Client()



####Slash command testing####


slash = SlashCommand(client, sync_commands=True) # Declares slash commands through the client.

guild_ids = [764385563289452545]


@slash.slash(name="ping", guild_ids=guild_ids)
async def _ping(ctx): # Defines a new "context" (ctx) command called "ping."
    print(ctx.author.name)
    await ctx.respond()
    await ctx.send(f"Pong! ({client.latency*1000}ms)")








####End slash command testing####


@client.event

#Responds to message
async def on_message(message):

    def command(name):  #Checks if the message contains a command with the given name
        prefix = getPrefix(message.guild.id)  #Gets the prefix for the server
        if message.content.lower().startswith(prefix + name):  #If the lowercase version of the message starts with the prefix and the command, then return true. Else return false
            return True
        else: 
            return False

    if message.author == client.user:  #Bot will not respond to its own messages
        return
    elif message.author.bot:  #Bot will not respond to other bots
        return
    elif command("foo"):  #Accepts 'foo', returns 'bar'
        await commands.fooTest(message)
    elif command("help") or command("h") or f"<@!{client.user.id}>" in message.content:  #Starts an interactive help command
        await commands.help(message, client)      
    elif command("prefix"):
        await commands.prefixCommand(message)
    elif command("ping"):
        await commands.ping(message, client.latency)
    elif command("join"):
        await commands.join(message)
    elif command("leave"):
        await commands.leave(message, client)
    elif command("lobby"):
        await commands.lobby(message, client)
    elif command("start"):
        await commands.start(message)
    #print(message.content) 

@client.event
async def on_raw_reaction_add(payload):  #When reaction added
    emoji = payload.emoji  #Get emoji from the reaction payload
    message = await client.fetch_channel(payload.channel_id).fetch_message(payload.message_id)  #Get message from the reaction payload
    user = await client.fetch_user(payload.user_id)  #Get user from the reaction payload
    await reactionUpdate(emoji, message, user)  #Call the reaction function

@client.event  #When reaction removed
async def on_raw_reaction_remove(payload):
    emoji = payload.emoji  #Get emoji from the reaction payload
    message = await client.fetch_channel(payload.channel_id).fetch_message(payload.message_id)  #Get emoji from the reaction payload
    user = await client.fetch_user(payload.user_id)  #Get user from the reaction payload
    await reactionUpdate(emoji, message, user)  #Call the reaction function

async def reactionUpdate(emoji, message, user):  #Function called on every reaction event
    if user.bot or user == client.user:  #If user is bot cancel or self cancel
        return
    if not message.id in reactionMessageIDs.keys():  #If the message isn't in the dictionary of reaction event messages
        return
    elif reactionMessageIDs[message.id].type == "help":
        await reactions.help(emoji, message, user, client)

@client.event
#Bot has joined, says which servers/guilds
async def on_ready():
    await client.change_presence(activity=discord.Game(name='Uno! - @Uno2'))
    print(f'{client.user} is connected to the following guilds:')
    async for guild in client.fetch_guilds(limit=150):
        print(guild.name)
    client.availabilityCheck = client.loop.create_task(backgroundTasks.checkChannelAvailability(client))
    

async def my_background_task():
        counter = 0
        channel = client.get_channel(764386772658028605) # channel ID goes here
        while not client.is_closed():
            counter += 1
            await channel.send(counter)
            await asyncio.sleep(1) # task runs every 1 second



client.run(TOKEN)