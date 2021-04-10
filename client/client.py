# client.py

import asyncio
import discord
import discord.ext
import client.commands as commands
import client.reactions as reactions
from client.globalVariables import reactionMessageIDs, openLobbies
from client.prefix import getPrefix
import client.backgroundTasks as backgroundTasks
from discord_slash import SlashCommand
from discord_slash.utils import manage_commands
import logging



logging.basicConfig(level=logging.INFO)

TOKEN = "NzM2NDE4MDkwNjI3MjM1OTUx.Xxugyg.9SN5blnqxFDBnre2lqgjZUFDrGk"

client = discord.ext.commands.Bot(command_prefix = getPrefix)

client.remove_command('help')  #Remove the deafult help command

####Slash commands####


slash = SlashCommand(client, sync_commands=True) # Declares slash commands through the client.

guild_ids = [764385563289452545, 766488291934470184]


@slash.slash(name="ping", guild_ids=guild_ids)
async def ping(ctx): # Defines a new "context" (ctx) command called "ping."
    await commands.ping(ctx, client.latency)

@slash.slash(name="help", 
    guild_ids=guild_ids, 
    description="Displays an interactive help message.",
    options=[manage_commands.create_option(
        name = "Command",   
        description = "Command to get help for",
        option_type = 3,
        required = False,
        choices = [
            {"name" : "Help for the join command", "value" : "join"}, 
            {"name" : "Help for the leave command", "value" : "leave"}, 
            {"name" : "Help for the start command", "value" : "start"}, 
            {"name" : "Help for the rules command", "value" : "rules"}, 
            {"name" : "Help for the ping command", "value" : "ping"} 
            ]
        )   
    ]
)

async def help(ctx, argCommand="main"): # Defines a new "context" (ctx) command called "help."
    await commands.help(ctx, argCommand, client)

@slash.slash(name="foo", 
    guild_ids=guild_ids, 
    description="A development command."
)

async def foo(ctx): # Defines a new "context" (ctx) command called "foo."
    await commands.fooTest(ctx)

@slash.slash(name="join", 
    guild_ids=guild_ids, 
    description="Join a game lobby",
)
async def join(ctx): # Defines a new "context" (ctx) command called "ping."
    await commands.join(ctx)

@slash.slash(name="leave", 
    guild_ids=guild_ids, 
    description="Leave a game lobby",
)
async def leave(ctx): # Defines a new "context" (ctx) command called "ping."
    await commands.leave(ctx, client)

@slash.slash(name="lobby", 
    guild_ids=guild_ids, 
    description="View a game lobby",
)
async def lobby(ctx): # Defines a new "context" (ctx) command called "ping."
    await commands.lobby(ctx, client)

@slash.slash(name="start", 
    guild_ids=guild_ids, 
    description="Start a game",
)
async def start(ctx): # Defines a new "context" (ctx) command called "ping."
    await commands.start(ctx, client)
    








####End slash commands####

#@client.event
async def on_message(message):
    if message.content.startswith(f"<@!{client.user.id}>"):  #Starts an interactive help command
        await commands.help(message, client)      

#@client.command(name="foo")
async def foo(ctx):
    await commands.fooTest(ctx.message)

#@client.command(name="prefix")
async def prefix(ctx):
    await commands.prefixCommand(ctx.message)

#@client.command(name="help", aliases=["h"])
async def help(ctx):
    await commands.help(ctx.message, client)

#@client.event

#Responds to message

@client.event
async def on_raw_reaction_add(payload):  #When reaction added
    emoji = payload.emoji  #Get emoji from the reaction payload
    channel = await client.fetch_channel(payload.channel_id)  #Get channel from the reaction payload
    message = await channel.fetch_message(payload.message_id)  #Get message from the reaction payload
    user = await client.fetch_user(payload.user_id)  #Get user from the reaction payload
    await reactionUpdate(emoji, message, user)  #Call the reaction function

@client.event  #When reaction removed
async def on_raw_reaction_remove(payload):
    emoji = payload.emoji  #Get emoji from the reaction payload
    channel = await client.fetch_channel(payload.channel_id)  #Get channel from the reaction payload
    message = await channel.fetch_message(payload.message_id)  #Get message from the reaction payload
    user = await client.fetch_user(payload.user_id)  #Get user from the reaction payload
    await reactionUpdate(emoji, message, user)  #Call the reaction function

async def reactionUpdate(emoji, message, user):  #Function called on every reaction event
    if user.bot or user == client.user:  #If user is bot cancel or self cancel
        return
    if not message.id in reactionMessageIDs.keys():  #If the message isn't in the dictionary of reaction event messages
        return
    elif reactionMessageIDs[message.id].type == "help":
        await reactions.help(emoji, message, user, client)
    elif reactionMessageIDs[message.id].type == "hand":
        await reactions.hand(emoji, message, user, client)
    elif reactionMessageIDs[message.id].type == "wild":
        await reactions.wild(emoji, message, user, client)

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