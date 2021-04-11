import discord
import asyncio
import storage.globalVariables as globalVariables
class HelpMessage:  #Class for help command
    
    def __init__(self, ctx, argCommand): 
        self.guildID = ctx.guild.id
        self.channelID = ctx.channel.id
        self.userID = ctx.author.id
        self.helpPages = ["main", "join", "leave", "start", "rules", "ping"]  #List of help pages
        self.type = "help"  #Type for reaction reference dictionary
        self.index = self.helpPages.index(argCommand)

    async def updateMessage(self, client):
        self.sentMessage = await self.getSentMessage(client)  #Gets the message itself
        await self.sentMessage.edit(embed=await self.currentEmbed())  #Updates the message with a newly generated embed

    async def currentEmbed(self):  
        if self.helpPages[self.index] == "join":
            helpEmbed=discord.Embed(title="**Uno2 Help**", description="Join lobby command", color=0xe32c22)
            helpEmbed.add_field(name=f"Usage: /join", value=f"Joins a lobby in the current channel.", inline=True)
        elif self.helpPages[self.index] == "leave":
            helpEmbed=discord.Embed(title="**Uno2 Help**", description="Leave game command", color=0xe32c22)
            helpEmbed.add_field(name=f"Usage: /leave", value=f"Leaves the current game or lobby. This command works on any server where the bot can see it.", inline=True)
        elif self.helpPages[self.index] == "start":
            helpEmbed=discord.Embed(title="**Uno2 Help**", description="Start game command", color=0xe32c22)
            helpEmbed.add_field(name=f"Usage: /start", value=f"Starts a game in the current channel. New players will no longer be able to join while the game is running.", inline=True)
        elif self.helpPages[self.index] == "rules":
            helpEmbed=discord.Embed(title="**Uno2 Help**", description="Game rules command", color=0xe32c22)
            helpEmbed.add_field(name=f"Usage: /rules", value=f"Work in progress, will be added later.", inline=True)
        elif self.helpPages[self.index] == "ping":
            helpEmbed=discord.Embed(title="**Uno2 Help**", description="Ping command", color=0xe32c22)
            helpEmbed.add_field(name=f"Usage: /ping", value=f"Displays the current bot ping to Discord.", inline=True)
        else:  #Main embed page (Last just in case the index somehow gets messed up, because its the most helpful page)
            helpEmbed=discord.Embed(title="**Uno2 Help**", description="Uno2 is an Uno game bot for Discord", color=0xe32c22)
            helpEmbed.add_field(name="**Commands**", value=f"(Tip - You can use /help `command` to get help for a specific command or use the arrows at the bottom of this message)", inline=False)
            helpEmbed.add_field(name=f"/help", value="Open the help menu", inline=True)
            helpEmbed.add_field(name=f"/join", value="Joins the lobby in the current channel", inline=True)
            helpEmbed.add_field(name=f"/leave", value="Leaves the current game/lobby (can be used anywhere!)", inline=True)
            helpEmbed.add_field(name=f"/start", value="Starts the game of Uno in the current channel", inline=True)
            helpEmbed.add_field(name=f"/rules", value="Changes the rules for future games of Uno in the current channel", inline=True)
            helpEmbed.add_field(name=f"/ping", value="Current ping from the bot to Discord", inline=True)
            helpEmbed.add_field(name=f"/prefix", value="Change the prefix for the current server", inline=True)
        helpEmbed.set_footer(text=f"Page {self.index + 1}/{len(self.helpPages)}")  #Gets index and adds one for page number; gets length and for total number
        return helpEmbed

    async def sendMessage(self, ctx, client):
        embedToSend = await self.currentEmbed()  #Generated embed
        self.sentMessage = await ctx.send(embed=embedToSend)
        self.sentMessageID = self.sentMessage.id
        globalVariables.reactionMessageIDs[self.sentMessage.id] = self  #Adds this object to reactionMessageIDs
        await self.sentMessage.add_reaction("◀️")  #Add control buttons
        await self.sentMessage.add_reaction("▶️")
        client.loop.create_task(self.delete(client))   #Creates a task to delete this message from the reaction message dictionary

    async def getSentMessage(self, client):  #Get the message object from discord
        return await client.get_channel(self.channelID).fetch_message(self.sentMessageID)  
    
    async def delete(self, client):  #This is run as a background task once the message is sent 
        await asyncio.sleep(300)  #Waiting for 300 seconds
        self.sentMessage = await self.getSentMessage(client)  #Get the message object
        await self.sentMessage.edit(embed=await self.currentEmbed(), content="This message is now inactive")  #Edit the message
        del(globalVariables.reactionMessageIDs[self.sentMessage.id])  #Delete the message from the reaction dictionary