import discord
from storage.globalVariables import openGames, openLobbies, playersInGame, playersInLobby, channelInGame, channelHasLobby, playerInGame, playerInLobby
from client.messageClasses import HelpMessage
from client.game import GameLobby, Game
    
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
    elif not channelHasLobby(ctx.channel.id):  #If the channel doesn't have a lobby, make one
        openLobbies[ctx.channel.id] = GameLobby(ctx)
    openLobbies[ctx.channel.id].playerJoin(ctx.author.id)  #Gets the lobby object from the dictionary and calls playerJoin with the author ID
    await ctx.send(f"{ctx.author.name} has joined the lobby. {lobbyCount(ctx.channel.id)}")  #Send join message

async def leave(ctx, client):
    if playerInLobby(ctx.author.id):  #If player in lobby
        if playersInLobby[ctx.author.id] == ctx.channel.id:  #If the channelID the message was sent in matches the ID of the lobby
            await ctx.send(f"You left the lobby. {lobbyCount(ctx.channel.id, - 1)}")  #Prints lobby leave message and the count message minus 1. Count is minus one because it runs before the user is actually removed
        else: 
            await ctx.send("You left the lobby.")  #If the channelID the message was sent in does not match the ID of the lobby, send a message in both channels.
            await client.get_channel(playersInLobby[ctx.author.id]).send(f"{ctx.author.name} left the lobby. {lobbyCount(playersInLobby[ctx.author.id], - 1)}")
        openLobbies[playersInLobby[ctx.author.id]].playerLeave(ctx.author.id)  #Gets the lobby object from the dictionary and calls playerLeave with the author ID
    elif playerInGame(ctx.author.id):  #Similar to above but for games instead
        if playersInGame[ctx.author.id] == ctx.channel.id:
            await ctx.send(f"You left the game.")  #Prints game leave message and the count minus 1. Count is minus one because it runs before the user is actually removed
        else: 
            await ctx.send("You left the game.")
            await client.get_channel(playersInLobby[ctx.author.id]).send(f"{ctx.author.name} left the game.")
        await openGames[playersInGame[ctx.author.id]].playerLeave(ctx.author.id, client)  #Gets the game object from the dictionary and calls playerLeave with the author ID
    else:
        ctx.send("You are not in a lobby or game.")

async def lobby(ctx, client):
    lobbyEmbed=discord.Embed(title="**Uno2 Lobby**", description=f"This is the lobby for <#{ctx.channel.id}>.", color=0xe32c22)  
    if channelHasLobby(ctx.channel.id):  #If there is a lobby, get all the players in it and list them. If not, then say the lobby is empty
        for playerID in openLobbies[ctx.channel.id].players:
            player = await client.fetch_user(playerID)
            lobbyEmbed.add_field(name=f"{player.name}", value="Work in progress", inline=True)
        lobbyEmbed.set_footer(text= f"{lobbyCount(ctx.channel.id).replace('now ', '')}")  #Uses the same function to get the count text, but removes the word "now"
    else:
        lobbyEmbed.add_field(name=f"Lobby is empty.", value=f"Type `/join` to join.", inline=True)
    await ctx.send(embed=lobbyEmbed)

def lobbyCount(channelID, offset=0):  #Returns a formatted message of the amount of players in the lobby. "There are now __ player(s) in the lobby". Offset is for leave messages mostly
    if len(openLobbies[channelID].players) + offset == 1:
        return f"There is now 1 player in the lobby."
    else:
        return f"There are now {len(openLobbies[channelID].players) + offset} players in the lobby."

async def start(ctx, client):  #Starts the game in the current channel
    if channelInGame(ctx.channel.id):
        await ctx.send("The game in this channel is already in progress. Switch to a different channel or wait for this game to end.")
        return 
    elif playerInGame(ctx.author.id):
        await ctx.send(f"You are already in a game in <#{playersInGame[ctx.author.id]}>. Type `/leave` to leave that game to join a new one.")
        return 
    elif not channelHasLobby(ctx.channel.id):
        await ctx.send(f"There is not a lobby in this channel. Join one with `/join`.")
        return
    elif not playerInLobby(ctx.author.id):
        await ctx.send(f"You are not in the lobby. Type `/join` to join the lobby.")
        return
    elif playersInLobby[ctx.author.id] != ctx.channel.id:  #The above if shows that the player is in a lobby, so no check for that is needed
        await ctx.send(f"You are already in a lobby in <#{playersInLobby[ctx.author.id]}>. Type `/leave` to leave that lobby to join a new one.")
        return
    elif len(openLobbies[ctx.channel.id].players) < 2:  #The above ifs prove that there is a lobby in this channel with only one player, the command user, so no checks are needed
        await ctx.send(f"There are not enough players in this lobby. Get at least one more to join with `/join`.")
        return
    game = Game(openLobbies[ctx.channel.id])
    openGames[ctx.channel.id] = game
    await game.startGame(client)
    del(openLobbies[ctx.channel.id])