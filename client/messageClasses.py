import discord
import asyncio
import storage.globalVariables as globalVariables
import storage.cardDictionaries as cardDictionaries
from storage.globalVariables import reactionMessageIDs, getRules
from client.cardClass import Card

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
        client.loop.create_task(self.close(client))   #Creates a task to delete this message from the reaction message dictionary

    async def getSentMessage(self, client):  #Get the message object from discord
        return await client.get_channel(self.channelID).fetch_message(self.sentMessageID)  
    
    async def close(self, client):  #This is run as a background task once the message is sent 
        await asyncio.sleep(300)  #Waiting for 300 seconds
        self.sentMessage = await self.getSentMessage(client)  #Get the message object
        await self.sentMessage.edit(embed=await self.currentEmbed(), content="This message is now inactive")  #Edit the message
        del(globalVariables.reactionMessageIDs[self.sentMessage.id])  #Delete the message from the reaction dictionary

class StackMessage:
    def __init__(self, player, game):
        self.userID = player.playerID
        self.type = "stack"
        self.player = player
        self.game = game
        self.stackHand = [card for card in player.hand if (card.face == "plus2" and card.color == game.currentCard.color) or card.face == "plus4"]
        self.index = 0

    async def sendMessage(self, client):
        user = await client.fetch_user(self.userID)
        message = await user.send(embed = await self.stackEmbed())
        await message.add_reaction(cardDictionaries.cardEmoji("back"))
        await message.add_reaction("◀️")
        await message.add_reaction("⏺️")
        await message.add_reaction("▶️")
        self.messageID = message.id  
        reactionMessageIDs[self.messageID] = self

    async def stackEmbed(self):
        selectedCard = self.stackHand[self.index]
        embed = discord.Embed(title = f"<@{self.userID}>'s stackable cards", description = "Choose a card to stack (or draw cards instead)", color = selectedCard.colorCode)
        embed.set_image(url=selectedCard.image)
        cardListSelected = [card.emoji for card in self.stackHand]
        cardListSelected[self.index] = "[" + cardListSelected[self.index]
        cardListSelected[self.index] = cardListSelected[self.index] + "]"
        embed.add_field(name = "Cards:", value = " ".join(cardListSelected))
        return embed

    async def updateMessage(self, amount, client):
        self.stackHand = [card for card in self.player.hand if (card.face == "plus2" and card.color == self.game.currentCard.color) or card.face == "plus4"]
        self.index += amount
        if self.index >= len(self.stackHand):
            self.index -= (len(self.stackHand))
        if self.index < 0:
            self.index += len(self.stackHand)
        user = await client.fetch_user(self.userID)
        message = await user.fetch_message(self.messageID)
        await message.edit(embed = await self.stackEmbed())

    async def playStackCard(self, client):
        if not self.game.players[self.game.turnIndex].playerID == self.player.playerID:
            await GenericMessage("It's not your turn.", self.player).sendMessage(client)
            return
        elif not self.game.validCard(self.stackHand[self.index]):
            await GenericMessage("You can't play that card.", self.player).sendMessage(client)
            return
        await self.game.playCard(self.player, client)
        await self.deleteMessage()

    async def deleteMessage(self, client):
        user = await client.fetch_user(self.userID)
        message = await user.fetch_message(self.messageID)
        await message.delete()

class WildMessage:
    def __init__(self, card, player, game):
        self.userID = player.playerID
        self.type = "wild"  #Type for reaction message dictionary
        self.game = game
        self.card = card
        self.player = player

    async def sendMessage(self, client):
        self.player.state = "wild"  #Sets the player state to wild
        user = await client.fetch_user(self.userID)  #Gets user
        message = await user.send(embed = self.wildEmbed())  #Sends the embed to the user
        await message.add_reaction("🟥")  #Add color reactions
        await message.add_reaction("🟨")
        await message.add_reaction("🟩")
        await message.add_reaction("🟦")    
        self.messageID = message.id
        reactionMessageIDs[self.messageID] = self

    def wildEmbed(self):
        embed = discord.Embed(title = f"Choose a color", description = self.card.face, color = self.card.colorCode)  
        embed.set_thumbnail(url=self.card.image)
        return embed

    async def deleteMessage(self, client):
        user = await client.fetch_user(self.userID)
        message = await user.fetch_message(self.messageID)
        await message.delete()

    async def pickColor(self, color, client):
        card = Card(color = color, face = self.card.face, isColorChoice = False, returnable = False)
        print(vars(card))
        await self.game.playCard(self.player, client, source = "wild", card = card)
        await self.deleteMessage(client)
        self.player.state = "card"

class HandMessage:
    def __init__(self, player, game):
        self.userID = player.playerID
        self.type = "hand"
        self.player = player
        self.game = game

    async def sendMessage(self, client):
        user = await client.fetch_user(self.userID)
        message = await user.send(embed = await self.handEmbed())
        await message.add_reaction("⏪")
        await message.add_reaction("◀️")
        await message.add_reaction("⏺️")
        await message.add_reaction("▶️")
        await message.add_reaction("⏩")
        await message.add_reaction(cardDictionaries.cardEmoji["back"])
        self.messageID = message.id  
        reactionMessageIDs[self.messageID] = self

    async def handEmbed(self):
        selectedCard = self.player.hand[self.player.selectedIndex]
        embed = discord.Embed(title = f"<@{self.userID}>'s hand", description = "Your Hand", color = selectedCard.colorCode)
        embed.set_image(url=selectedCard.image)
        cardListSelected = [card.emoji for card in self.player.hand]
        cardListSelected[self.player.selectedIndex] = "[" + cardListSelected[self.player.selectedIndex]
        cardListSelected[self.player.selectedIndex] = cardListSelected[self.player.selectedIndex] + "]"
        embed.add_field(name = "Cards:", value = " ".join(cardListSelected))
        return embed

    async def updateMessage(self, amount, client):
        self.player.selectedIndex += amount
        if self.player.selectedIndex >= len(self.player.hand):
            self.player.selectedIndex -= (len(self.player.hand))
        if self.player.selectedIndex < 0:
            self.player.selectedIndex += len(self.player.hand)
        user = await client.fetch_user(self.userID)
        message = await user.fetch_message(self.messageID)
        await message.edit(embed = await self.handEmbed())

    async def attemptPlayCard(self, client):
        if not self.game.players[self.game.turnIndex].playerID == self.player.playerID:
            await GenericMessage("It's not your turn.", self.player).sendMessage(client)
            return
        elif not self.game.validCard(self.player.hand[self.player.selectedIndex]):
            await GenericMessage("You can't play that card.", self.player).sendMessage(client)
            return
        await self.game.playCard(self.player, client)

    async def drawCard(self, client):
        if not self.game.players[self.game.turnIndex].playerID == self.player.playerID:
            await GenericMessage("It's not your turn.", self.player).sendMessage(client)
            return
        rules = getRules(self.game.channelID)
        print(rules, self.player.drewCard)

        if self.player.drewCard == True:  #Stop if the player has already drawn a card before they play a card
            await self.game.playCard(player = self.player, client = client, source = "pass")
            return
        if rules["drawToMatch"]:  #If draw to match rule is on
            cardValid = False
            while not cardValid:  #While the card is not a valid one, keep drawing
                card = await self.player.drawCard(client)
                if self.game.validCard(card): cardValid = True
        else:   
            await self.player.drawCard(client)          
        self.player.drewCard = True
        if rules["forceplay"]: 
            await self.game.playCard(player = self.player, client = client, source = "pass")

class GenericMessage:
    def __init__(self, content, player):
        self.content = content
        self.player = player

    async def sendMessage(self, client):
        user = await client.fetch_user(self.player.playerID)  #Get the user the message is being sent to
        message = await user.send(self.content)
        await asyncio.sleep(5)
        await message.delete()