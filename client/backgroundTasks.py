import discord
import asyncio


checkAvailabilityLoop = 1


async def checkChannelAvailability(client):
    print("Availability background check started.")
    count = 1
    while checkAvailabilityLoop == 1:  
        from globalVariables import openGames, openLobbies
        #print(count)
        openLobbiesPruned = openLobbies.copy()  #Copy the dicts to new dicts for editing
        openGamesPruned = openGames.copy()
        for item in openLobbies.keys():
            try: 
                await client.fetch_channel(item)  #If this fails it is because the bot cannot find the channel
            except:
                print(f"Invalid channelID found: {item}. Deleting from directory...")
                for playerID in openLobbies[item].players:  
                    openLobbies[item].playerLeave(playerID)  #Kick all players
                    user = await client.fetch_user(playerID)  #Get the user object
                    await user.send(f"Lobby closed in channel <#{item}>. Either the bot lost permission to view that channel or the channel was deleted.")  #Send user a DM explaining what happened
                del(openLobbiesPruned[item])  #Delete entry from the copy of the list
        openLobbies = openLobbiesPruned.copy()  #Set the original list to the copy
        for item in openGames.keys():
            try:
                channel = await client.fetch_channel(item)
            except: 
                print(f"Invalid channelID found: {item}. Deleting from directory...")
                for playerID in openGames[item].players:
                    openGames[item].playerLeave(playerID)
                    user = await client.fetch_user(playerID)
                    await user.send(f"Game closed in channel <#{item}>. Either the bot lost permission to view that channel or the channel was deleted.")
                del(openGamesPruned[item])
        openGames = openGamesPruned.copy()
        count += 1
        await asyncio.sleep(5)

