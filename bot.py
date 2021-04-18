# client.py

import asyncio
import logging

import discord
import discord
from discord_slash import SlashCommand
from discord_slash.utils import manage_commands

import client.backgroundTasks as backgroundTasks
import client.commands as commands
import client.reactions as reactions
from storage.globalVariables import openLobbies, reactionMessageIDs, client

TOKEN = open("storage\TOKEN.token", "r").readline()

logging.basicConfig(level=logging.INFO)

client.remove_command('help')  #Remove the deafult help command

####Slash commands####


slash = SlashCommand(client, sync_commands=True) # Declares slash commands through the client.

guild_ids = [764385563289452545, 766488291934470184]


@client.command()
async def start(ctx):
    await commands.start(ctx)



@client.event
async def on_slash_command_error(ctx, ex):
    print(f"Exception:\n {ex} \nin channel {ctx.channel.name}")

@slash.slash(name="ping")
async def ping(ctx): # Defines a new "context" (ctx) command called "ping."
    await commands.ping(ctx, client.latency)

@slash.slash(name="help", 
    description="Displays an interactive help message.",
    options=[manage_commands.create_option(
        name = "Command",   
        description = "Command to get help for",
        option_type = 3,
        required = False,
        choices = [
            {"name" : "join", "value" : "join"}, 
            {"name" : "leave", "value" : "leave"}, 
            {"name" : "start", "value" : "start"}, 
            {"name" : " rules", "value" : "rules"}, 
            {"name" : "ping", "value" : "ping"} 
            ]
        )   
    ]
)

async def help(ctx, argCommand="main"): # Defines a new "context" (ctx) command called "help."
    await commands.help(ctx, argCommand, client)

@slash.slash(name="foo", 
    description="A development command."
)

async def foo(ctx): # Defines a new "context" (ctx) command called "foo."
    await commands.fooTest(ctx)

@slash.slash(name="join",  
    description="Join a game lobby",
)
async def join(ctx): # Defines a new "context" (ctx) command called "ping."
    await commands.join(ctx)

@slash.slash(name="leave", 
    description="Leave a game lobby",
)
async def leave(ctx): # Defines a new "context" (ctx) command called "ping."
    await commands.leave(ctx)

@slash.slash(name="lobby", 
    description="View a game lobby",
)
async def lobby(ctx): # Defines a new "context" (ctx) command called "ping."
    await commands.lobby(ctx)

@slash.slash(name="start", 
    description="Start a game",
)
async def start(ctx): # Defines a new "context" (ctx) command called "ping."
    await commands.start(ctx)
    



####End slash commands####

@client.event
async def on_message(message):
    if message.content.startswith(f"<@!{client.user.id}>"):  #Starts an interactive help command
        await commands.help(message)   
    if message.content.startswith("u!start"):
        await commands.start(message)

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
        await reactions.help(emoji, message, user)
    elif reactionMessageIDs[message.id].type == "hand":
        await reactions.hand(emoji, message, user)
    elif reactionMessageIDs[message.id].type == "wild":
        await reactions.wild(emoji, message, user)
    elif reactionMessageIDs[message.id].type == "stack":
        await reactions.stack(emoji, message, user)
    elif reactionMessageIDs[message.id].type == "draw":
        await reactions.draw(emoji, message, user)

@client.event
#Bot has joined, says which servers/guilds
async def on_ready():
    await client.change_presence(activity=discord.Game(name='Uno! - @Uno2'))
    print(f'{client.user} is connected to the following guilds:')
    async for guild in client.fetch_guilds(limit=150):
        print(guild.name)
    client.availabilityCheck = client.loop.create_task(backgroundTasks.checkChannelAvailability())
    

async def my_background_task():
        counter = 0
        channel = client.get_channel(764386772658028605) # channel ID goes here
        while not client.is_closed():
            counter += 1
            await channel.send(counter)
            await asyncio.sleep(1) # task runs every 1 second

client.run(TOKEN)
