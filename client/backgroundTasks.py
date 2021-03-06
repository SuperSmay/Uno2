import discord
import asyncio
from storage.globalVariables import openLobbies, openGames, reactionMessageIDs, client

timeInterval = 5  #Time in seconds between each run through of the loop

async def checkChannelAvailability():
    '''
    Starts the background process to check for deleted or unaccessible channels. 
    '''
    print(f"Channel availability background check started. Cycle time is {timeInterval} seconds.")
    while True:  
        for item in openLobbies.keys():  #For each key (channelID) in the open lobbies list
            try: 
                await client.fetch_channel(item)  #If this fails it is because the bot cannot find the channel, as fetch_channel throws an exception when the bot does not have access to/cannot find the channel
            except:
                print(f"Invalid channelID found: {item}. Deleting from directory...")
                for playerID in openLobbies[item].players:  #For each playerID in the lobby
                    openLobbies[item].playerLeave(playerID)  #Kick all players
                    user = await client.fetch_user(playerID)  #Get the user object
                    await user.send(f"Lobby closed in channel <#{item}>. Either the bot lost permission to view that channel or the channel was deleted.")  #Send user a DM explaining what happened
                openLobbiesPruned = openLobbies.copy()  #Copy the dicts to new dicts for editing
                del(openLobbiesPruned[item])  #Delete entry from the copy of the list
                openLobbies = openLobbiesPruned.copy()  #Set the original list to the copy
        for item in openGames.keys():  #Similar to above loop, but with games instead of lobbies
            try:
                await client.fetch_channel(item)
            except: 
                print(f"Invalid channelID found: {item}. Deleting from directory...")
                for playerID in openGames[item].players:
                    openGames[item].playerLeave(playerID)
                    user = await client.fetch_user(playerID)
                    await user.send(f"Game closed in channel <#{item}>. Either the bot lost permission to view that channel or the channel was deleted.")
                    openGamesPruned = openGames.copy()
                del(openGamesPruned[item])
                openGames = openGamesPruned.copy()
        await asyncio.sleep(timeInterval)  #Async sleep doesn't block, and simply just waits in the background
        