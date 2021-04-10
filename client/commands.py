import discord
from discord import channel
from prefix import getPrefix, changePrefix
import time
from globalVariables import openGames, openLobbies, playersInGame, playersInLobby
from classes import HelpMessage
from gameClass import channelInGame, channelHasLobby, playerInGame, playerInLobby, GameLobby, Game

async def prefixCommand(ctx):
    await ctx.send.changePrefix(ctx)
    
async def fooTest(ctx):
    await ctx.send(">>> bar")

async def help(ctx, argCommand, client):  #Help command
    helpMessageObject = HelpMessage(ctx, argCommand)  #Creates a new help object for the message
    await helpMessageObject.sendMessage(ctx, client)  #Sends the message from the object

async def ping(ctx, latency):
    await ctx.send(f"Pong! {round(latency*1000, 2)}ms")  #Calculates the client ping     

async def join(ctx):
    if channelInGame(ctx.channel.id):
        await ctx.send("The game in this channel is already in progress. Switch to a different channel or wait for this game to end.")
        return 
    elif playerInLobby(ctx.author.id):
        await ctx.send(f"You are already in a lobby in <#{playersInLobby[ctx.author.id]}>. Type `/leave` to leave that lobby to join a new one.")
        return 
    elif playerInGame(ctx.author.id):
        await ctx.send(f"You are already in a game in <#{playersInGame[ctx.author.id]}>. Type `/leave` to leave that game to join a new one.")
        return 
    elif not channelHasLobby(ctx.channel.id): 
        openLobbies[ctx.channel.id] = GameLobby(ctx)
    openLobbies[ctx.channel.id].playerJoin(ctx.author.id)  #Gets the lobby object from the dictionary and calls playerJoin with the author ID
    await ctx.send(f"{ctx.author.name} has joined the lobby. {lobbyCount(ctx.channel.id)}")

async def leave(ctx, client):
    if playerInLobby(ctx.author.id):
        if playersInLobby[ctx.author.id] == ctx.channel.id:
            await ctx.send(f"You left the lobby. {lobbyCount(ctx.channel.id, - 1)}")  #Prints lobby leave message and the count minus 1. Count is minus one because it runs before the user is actually removed
        else: 
            await ctx.send("You left the lobby.")
            await client.get_channel(playersInLobby[ctx.author.id]).send(f"{ctx.author.name} left the lobby. {lobbyCount(playersInLobby[ctx.author.id], - 1)}")
        openLobbies[playersInLobby[ctx.author.id]].playerLeave(ctx.author.id)  #Gets the lobby object from the dictionary and calls playerLeave with the author ID
    elif playerInGame(ctx.author.id):
        if playersInGame[ctx.author.id] == ctx.channel.id:
            await ctx.send(f"You left the game.")  #Prints lobby leave message and the count minus 1. Count is minus one because it runs before the user is actually removed
        else: 
            await ctx.send("You left the game.")
            await client.get_channel(playersInLobby[ctx.author.id]).send(f"{ctx.author.name} left the game.")
        await openGames[playersInGame[ctx.author.id]].playerLeave(ctx.author.id, client)  #Gets the lobby object from the dictionary and calls playerLeave with the author ID
    else:
        ctx.send("You are not in a lobby or game.")

async def lobby(ctx, client):
    lobbyEmbed=discord.Embed(title="**Uno2 Lobby**", description=f"This is the lobby for <#{ctx.channel.id}>.", color=0xe32c22)
    if channelHasLobby(ctx.channel.id):
        for item in openLobbies[ctx.channel.id].players:
            player = await client.fetch_user(item)
            lobbyEmbed.add_field(name=f"{player.name}", value="Work in progress", inline=True)
        lobbyEmbed.set_footer(text= f"{lobbyCount(ctx.channel.id).replace('now ', '')}")  #Uses the same function to get the count text, but removes the word "now"
    else:
        lobbyEmbed.add_field(name=f"Lobby is empty.", value=f"Type `/join` to join.", inline=True)
    await ctx.send(embed=lobbyEmbed)

def lobbyCount(channelID, offset=0):
    if len(openLobbies[channelID].players) + offset == 1:
        return f"There is now 1 player in the lobby."
    else:
        return f"There are now {len(openLobbies[channelID].players) + offset} players in the lobby."

async def start(ctx, client):

    await ctx.send("Game starting...")
    if channelInGame(ctx.channel.id):
        await ctx.send("The game in this channel is already in progress. Switch to a different channel or wait for this game to end.")
        return 
    elif playerInGame(ctx.author.id):
        await ctx.send(f"You are already in a game in <#{playersInGame[ctx.author.id]}>. Type `/leave` to leave that game to join a new one.")
        return 
    elif not channelHasLobby(ctx.channel.id):
        await ctx.send(f"There is not a lobby in this channel. Type `/join` to create one.")
        return
    elif not playerInLobby(ctx.author.id):
        await ctx.send(f"You are not in the lobby. Type `/join` to join the lobby.")
        return
    else: #playerInLobby(ctx.author.id):

        if playersInLobby[ctx.author.id] == ctx.channel.id:
            
            game = Game(openLobbies[ctx.channel.id])
            openGames[ctx.channel.id] = game
            await game.startGame(client)
            del(openLobbies[ctx.channel.id])
        else: 
            await ctx.send(f"You are already in a lobby in <#{playersInLobby[ctx.author.id]}>. Type `/leave` to leave that lobby to join a new one.")
            return
    