import discord
import asyncio
import storage.globalVariables as globalVariables
import storage.cardDictionaries as cardDictionaries
from storage.globalVariables import reactionMessageIDs, getRules, client
from client.cardClass import Card

class HelpMessage:  #Class for help command
    
    def __init__(self, ctx, argCommand): 
        self.guildID = ctx.guild.id
        self.channelID = ctx.channel.id
        self.userID = ctx.author.id
        self.helpPages = ["main", "join", "leave", "start", "rules", "ping"]  #List of help pages
        self.type = "help"  #Type for reaction reference dictionary
        self.index = self.helpPages.index(argCommand)

    async def updateMessage(self):
        self.sentMessage = await self.getSentMessage()  #Gets the message itself
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

    async def sendMessage(self, ctx):
        embedToSend = await self.currentEmbed()  #Generated embed
        self.sentMessage = await ctx.send(embed=embedToSend)
        self.sentMessageID = self.sentMessage.id
        globalVariables.reactionMessageIDs[self.sentMessage.id] = self  #Adds this object to reactionMessageIDs
        await self.sentMessage.add_reaction("◀️")  #Add control buttons
        await self.sentMessage.add_reaction("▶️")
        client.loop.create_task(self.close())   #Creates a task to delete this message from the reaction message dictionary

    async def getSentMessage(self):  #Get the message object from discord
        return await client.get_channel(self.channelID).fetch_message(self.sentMessageID)  
    
    async def close(self):  #This is run as a background task once the message is sent 
        await asyncio.sleep(300)  #Waiting for 300 seconds
        self.sentMessage = await self.getSentMessage()  #Get the message object
        await self.sentMessage.edit(embed=await self.currentEmbed(), content="This message is now inactive")  #Edit the message
        del(reactionMessageIDs[self.sentMessage.id])  #Delete the message from the reaction dictionary

class StackMessage:
    def __init__(self, player, game):
        self.userID = player.playerID
        self.type = "stack"
        self.player = player
        self.game = game
        self.stackHand = [card for card in player.hand if (card.face == "plus2" and card.color == game.currentCard.color) or card.face == "plus4" or (card.face == "plus2" and game.currentCard.face == "plus2")]
        self.index = 0
        self.player.stackMessage = self

    async def sendMessage(self):
        user = await client.fetch_user(self.userID)
        message = await user.send(embed = await self.stackEmbed())
        client.loop.create_task(message.add_reaction("◀️"))
        client.loop.create_task(message.add_reaction("⏺️"))
        client.loop.create_task(message.add_reaction("▶️"))
        client.loop.create_task(message.add_reaction(cardDictionaries.cardEmoji["back"]))
        globalVariables.reactionMessageIDs[message.id] = self
        self.player.state = "stack"
        self.messageID = message.id  
        reactionMessageIDs[self.messageID] = self

    async def stackEmbed(self):
        selectedCard = self.stackHand[self.index]
        embed = discord.Embed(title = f"<@{self.userID}>'s stackable cards", description = "Choose a card to stack (or draw cards instead)", color = selectedCard.colorCode)
        embed.add_field(name = "Current card count:", value=f"{self.game.stack.amount} cards")
        embed.set_image(url=selectedCard.image)
        cardListSelected = [card.emoji for card in self.stackHand]
        cardListSelected[self.index] = "[" + cardListSelected[self.index]
        cardListSelected[self.index] = cardListSelected[self.index] + "]"
        embed.add_field(name = "Cards:", value = " ".join(cardListSelected))
        return embed

    async def updateMessage(self, amount):
        self.index += amount
        if self.index >= len(self.stackHand):
            self.index -= (len(self.stackHand))
        if self.index < 0:
            self.index += len(self.stackHand)
        user = await client.fetch_user(self.userID)
        message = await user.fetch_message(self.messageID)
        await message.edit(embed = await self.stackEmbed())

    async def playStackCard(self):
        card = self.stackHand[self.index]
        if not self.game.players[self.game.turnIndex].playerID == self.player.playerID:
            await GenericMessage("It's not your turn.", self.player).sendMessage()
            return
        elif not self.game.validCard(card):
            await GenericMessage("You can't play that card.", self.player).sendMessage()
            return
        if card.face == "plus2":
            await self.game.playCard(self.player, card)
            statusMessage = await self.game.playPlus2(card)
        elif card.face == "plus4":
            statusMessage = await self.game.startPlus4(self.player, card)
        await self.deleteMessage()
        await self.game.updateGameMessages(statusMessage)

    async def endStack(self):
        user = await client.fetch_user(self.userID)
        await self.game.stack.endStack()
        statusMessage = f"{user.name} drew {self.game.stack.amount} cards"
        await self.deleteMessage()
        await self.game.updateGameMessages(statusMessage)

    async def deleteMessage(self):
        user = await client.fetch_user(self.userID)
        message = await user.fetch_message(self.messageID)
        await message.delete()
        self.player.state = "card"
        del(reactionMessageIDs[self.messageID]) 

class WildMessage:
    def __init__(self, player, game):
        self.userID = player.playerID
        self.type = "wild"  #Type for reaction message dictionary
        self.game = game
        self.player = player
        self.player.wildMessage = self

    async def sendMessage(self):
        self.player.state = "wild"  #Sets the player state to wild
        user = await client.fetch_user(self.userID)  #Gets user
        message = await user.send(embed = self.wildEmbed())  #Sends the embed to the user
        client.loop.create_task(message.add_reaction("🟥"))  #Add color reactions
        client.loop.create_task(message.add_reaction("🟨"))
        client.loop.create_task(message.add_reaction("🟩"))
        client.loop.create_task(message.add_reaction("🟦"))
        self.messageID = message.id
        reactionMessageIDs[self.messageID] = self

    def wildEmbed(self):
        embed = discord.Embed(title = f"Choose a color", description = "Wild", color = 4802889)  
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/742986384113008712/742986442975871017/Background_2.png")
        return embed

    async def deleteMessage(self):
        user = await client.fetch_user(self.userID)
        message = await user.fetch_message(self.messageID)
        await message.delete()
        del(reactionMessageIDs[self.messageID]) 

    async def pickColor(self, color):
        self.player.state = "card"
        client.loop.create_task(self.deleteMessage())
        card = Card(color = color, face = "wild", returnable = False)
        print(vars(card))
        statusMessage = await self.game.endWild(self.player, card = card)  #TODO - Change to not call play card please god
        await self.game.updateGameMessages(statusMessage)
        
class Plus4Message:
    def __init__(self, player, game):
        self.userID = player.playerID
        self.type = "wild"  #Type for reaction message dictionary
        self.game = game
        self.player = player
        self.player.wildMessage = self

    async def sendMessage(self):
        self.player.state = "wild"  #Sets the player state to wild
        user = await client.fetch_user(self.userID)  #Gets user
        message = await user.send(embed = self.plus4Embed())  #Sends the embed to the user
        client.loop.create_task(message.add_reaction("🟥"))  #Add color reactions
        client.loop.create_task(message.add_reaction("🟨"))
        client.loop.create_task(message.add_reaction("🟩"))
        client.loop.create_task(message.add_reaction("🟦"))   
        self.messageID = message.id
        reactionMessageIDs[self.messageID] = self

    def plus4Embed(self):
        embed = discord.Embed(title = f"Choose a color", description = "Plus 4", color = 4802889)  
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/742986384113008712/742986443441307728/Background_3.png")
        return embed

    async def deleteMessage(self):
        user = await client.fetch_user(self.userID)
        message = await user.fetch_message(self.messageID)
        await message.delete()
        del(reactionMessageIDs[self.messageID]) 

    async def pickColor(self, color):
        self.player.state = "card"
        client.loop.create_task(self.deleteMessage())
        card = Card(color = color, face = "plus4", returnable = False)
        print(vars(card))
        statusMessage = await self.game.endPlus4(self.player, card = card)  #TODO - Change to not call play card please god
        await self.game.updateGameMessages(statusMessage)

class HandMessage:
    def __init__(self, player, game):
        self.userID = player.playerID
        self.type = "hand"
        self.player = player
        self.game = game
        self.player.handMessage = self

    async def sendMessage(self):
        user = await client.fetch_user(self.userID)
        message = await user.send(embed = await self.handEmbed())
        client.loop.create_task(message.add_reaction("⏪"))
        client.loop.create_task(message.add_reaction("◀️"))
        client.loop.create_task(message.add_reaction("⏺️"))
        client.loop.create_task(message.add_reaction("▶️"))
        client.loop.create_task(message.add_reaction("⏩"))
        client.loop.create_task(message.add_reaction(cardDictionaries.cardEmoji["back"]))
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

    async def updateMessage(self, amount):
        self.player.selectedIndex += amount
        if self.player.selectedIndex >= len(self.player.hand):
            self.player.selectedIndex -= (len(self.player.hand))
        if self.player.selectedIndex < 0:
            self.player.selectedIndex += len(self.player.hand)
        user = await client.fetch_user(self.userID)
        message = await user.fetch_message(self.messageID)
        await message.edit(embed = await self.handEmbed())

    async def playCardButtonPressed(self):
        card = self.player.hand[self.player.selectedIndex]
        print(card)
        if not self.game.players[self.game.turnIndex].playerID == self.player.playerID:
            if self.game.validJumpIn(card):
                await self.game.playCardJumpIn(self.player, card)
                return
            client.loop.create_task(GenericMessage("It's not your turn.", self.player).sendMessage())
            return 
        elif not self.game.validCard(card):
            client.loop.create_task(GenericMessage("You can't play that card.", self.player).sendMessage())
            return
        await self.game.playCard(self.player, card)

    async def drawCard(self):
        if not self.game.players[self.game.turnIndex].playerID == self.player.playerID:
            client.loop.create_task(GenericMessage("It's not your turn.", self.player).sendMessage())
            return
        rules = getRules(self.game.channelID)

        if self.player.drewCard == True:  #Stop if the player has already drawn a card before they play a card
            statusMessage = await self.game.passTurn(player = self.player)
            await self.game.updateGameMessages(statusMessage)
            return
        if rules["drawToMatch"]:  #If draw to match rule is on
            await self.player.drawCard(count = 0, drawToMatch = True)
        else:   
            await self.player.drawCard(count = 1, drawToMatch = False)
        self.player.drewCard = True

    async def deleteMessage(self):
        user = await client.fetch_user(self.userID)
        message = await user.fetch_message(self.messageID)
        await message.delete()
        del(reactionMessageIDs[self.messageID]) 

class GenericMessage:
    def __init__(self, content, player):
        self.content = content
        self.player = player

    async def sendMessage(self):
        user = await client.fetch_user(self.player.playerID)  #Get the user the message is being sent to
        message = await user.send(self.content)
        await asyncio.sleep(5)
        await message.delete()

class DrawMessage:
    def __init__(self, player, game):
        self.player = player
        player.drawMessage = self
        self.game = game
        self.type = "draw"
        self.cards = []
        self.userID = player.playerID

    async def drawCards(self, count, drawToMatch = False):
        if drawToMatch:
            cardValid = False
            while not cardValid:  #While the card is not a valid one, keep drawing
                card = self.game.deck.drawCard()
                #self.cards.append(card)
                self.cards.append(Card("black", "plus4"))
                cardValid = self.game.validCard(card)
        while count > 0:
            self.cards.append(await self.game.deck.drawCard())
            count -= 1
        self.player.hand += self.cards
        print(self.cards)

    async def sendMessage(self, canPlay = True):
        self.player.state = "draw"
        self.canPlay = canPlay
        rules = getRules(self.game.channelID)
        user = await client.fetch_user(self.userID)
        message = await user.send(embed = self.cardsEmbed())
        self.messageID = message.id
        reactionMessageIDs[self.messageID] = self
        if rules["drawToMatch"] and canPlay:
            if not rules["forceplay"]:
                client.loop.create_task(message.add_reaction("✅"))
                client.loop.create_task(message.add_reaction("❎"))
                client.loop.create_task(self.autoDismiss())
                self.canPlay = True
            else:
                self.playCard()
                client.loop.create_task(message.add_reaction("❎"))
                client.loop.create_task(self.autoDismiss())
                self.canPlay = False
        else:
            client.loop.create_task(message.add_reaction("❎"))
            client.loop.create_task(self.autoDismiss())
            self.canPlay = False
        await self.player.handMessage.updateMessage(0)
        
    def cardsEmbed(self):
        rules = getRules(self.game.channelID)
        if rules["drawToMatch"]:
            if rules["forceplay"]:
                description = f"You were forced to play {self.cards[-1].emoji}"
            else:
                description = f"Would you like to play {self.cards[-1].emoji}?"
            embed = discord.Embed(title = f"You drew {len(self.cards)} cards", description = description, color = 4802889) 
            embed.add_field(name = "Cards:", value = "".join([card.emoji for card in self.cards]))
        else:
            description = self.cards[0].emoji
            embed = discord.Embed(title = f"You drew a card", description = description, color = 4802889) 
        return embed

    async def deleteMessage(self):
        user = await client.fetch_user(self.userID)
        message = await user.fetch_message(self.messageID)
        await message.delete()
        del(reactionMessageIDs[self.messageID]) 

    async def dismiss(self):
        self.player.state = "card"
        await self.deleteMessage()
        statusMessage = await self.game.passTurn(self.player)
        await self.game.updateGameMessages(statusMessage)
        self.player.drewCard = False

    async def accept(self):
        if not self.canPlay:
            return
        self.player.state = "card"
        await self.playCard()
        self.player.drewCard = False

    async def autoDismiss(self):
        await asyncio.sleep(10)
        try:
            await self.dismiss()
        except:
            pass

    async def playCard(self):  #Assumes card is valid
        self.canPlay = False
        card = self.cards[-1]
        await self.game.playCard(self.player, card)
        await self.dismiss()