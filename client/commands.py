import discord
from storage.globalVariables import channelHasLobby, channelInGame, client, openGames, openLobbies, playerInGame, playerInLobby, playersInGame, playersInLobby

from client.game import Game, GameLobby
from client.messageClasses import HelpMessage

### Commands

async def fooTest(ctx) -> None:  #Foo command
    '''
    Parameters:
        - ctx: Discord context object for the command call.\n
    Sends ">>>bar" to the ctx object given.\n
    Returns: None
    '''
    await ctx.send(">>> bar")

async def help(ctx, argCommand: str) -> None:  #Help command
    '''
    Parameters:
        - ctx: Discord context object for the command call.\n
        - argCommand: str; The name of a command to get help for.\n
    Creates and sends an interactble help message as a response to being called. argCommand must be a valid choice from the list ["main", "join", "leave", "start", "rules", "ping"] or an exception will be thrown.\n
    Returns: None
    '''
    helpMessageObject = HelpMessage(ctx, argCommand)  #Creates a new help object for the message
    await helpMessageObject.sendMessage(ctx)  #Sends the message from the object

async def join(ctx) -> None:  #Join command
    '''
    Parameters:
        - ctx: Discord context object for the command call.\n
    Attempts to join the player to the lobby in the channel the command was called in.\n
    If it succeeds, the player is added to the lobby and a success message is sent to the channel. If it fails, nothing happens and the reason is sent to the channel.\n
    Returns: None
    '''
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

async def leave(ctx) -> None:
    '''
    Parameters:
        - ctx: Discord context object for the command call.\n
    Attempts to remove the player from any active games or lobbies they may be in.\n
    Responds with a single leave message if the command is used in the channel of the game/lobby.\n
    Responds in both the channel of the game/lobby and the channel where the command was used if the command is used in a channel different from the one of the game/lobby.\n
    Returns: None
    '''
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
        await openGames[playersInGame[ctx.author.id]].playerLeave(ctx.author.id)  #Gets the game object from the dictionary and calls playerLeave with the author ID
    else:
        ctx.send("You are not in a lobby or game.")

async def lobby(ctx) -> None:
    '''
    Parameters:
        - ctx: Discord context object for the command call.\n
    Responds with an embed representing the lobby in the channel the command was called in.\n
    Returns: None
    '''
    lobbyEmbed=discord.Embed(title="**Uno2 Lobby**", description=f"This is the lobby for <#{ctx.channel.id}>.", color=0xe32c22)  
    if channelHasLobby(ctx.channel.id):  #If there is a lobby, get all the players in it and list them. If not, then say the lobby is empty
        for playerID in openLobbies[ctx.channel.id].players:
            player = await client.fetch_user(playerID)
            lobbyEmbed.add_field(name=f"{player.name}", value="Work in progress", inline=True)
        lobbyEmbed.set_footer(text= f"{lobbyCount(ctx.channel.id).replace('now ', '')}")  #Uses the same function to get the count text as the leave command, but removes the word "now"
    elif channelInGame(ctx.channel.id):  #If the game has started, just leave the lobby embed empty TODO - Fix this to show the current game stats
        lobbyEmbed.add_field(name=f"The game in this channel has already started", value="Work in progress", inline=True)
    else:
        lobbyEmbed.add_field(name=f"Lobby is empty.", value=f"Type `/join` to join.", inline=True)
    await ctx.send(embed=lobbyEmbed)

async def ping(ctx) -> None:  #Ping command
    '''
    Parameters:
        - ctx: Discord context object for the command call.\n
    Sends "Pong! (latency)ms" as a response to being called.\n
    Returns: None
    '''
    await ctx.send(f"Pong! {round(client.latency*1000, 2)}ms")  #Calculates then sends the ping message with the client latency, rounding it to two decimal points
    
async def start(ctx) -> None:  #Starts the game in the current channel
    '''
    Parameters:
        - ctx: Discord context object for the command call.\n
    Attempts to start the game for the user of the command in the channel the command was called in.\n
    If the game cannot be started, the reason why is sent the channel.\n
    If the game can be started, the game object is created from the lobby in the channel the command was called from, and the lobby is closed.\n
    Returns: None
    '''
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
    elif len(openLobbies[ctx.channel.id].players) < 1:  #The above ifs prove that there is a lobby in this channel with only one player, the command user, so no checks are needed
        await ctx.send(f"There are not enough players in this lobby. Get at least one more to join with `/join`.")
        return
    else:
        game = Game(openLobbies[ctx.channel.id])  #Create new game object
        await game.startGame()  #Starts the newly created game
        del(openLobbies[ctx.channel.id])  #Deletes the lobby from the dictionary

### Other

def lobbyCount(channelID, offset: int = 0) -> str:  #Returns a formatted message of the amount of players in the lobby. "There are now __ player(s) in the lobby". Offset is for leave messages mostly
    '''
    Parameters:
        - ctx: Discord context object for the command call.\n
        - offset: int; Offset for the count in the returned message\n
    Returns: str; A short message about the lobby player count. 
    '''
    if len(openLobbies[channelID].players) + offset == 1:
        return f"There is now 1 player in the lobby."
    else:
        return f"There are now {len(openLobbies[channelID].players) + offset} players in the lobby."
        