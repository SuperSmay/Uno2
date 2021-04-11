import asyncio
from client.reactions import hand
import discord
import time
from storage.globalVariables import openGames, openLobbies, playersInGame, playersInLobby, reactionMessageIDs
import random
import json
import storage.cardDictionaries as cardDictionaries

class Game:
    def __init__(self, gameLobby):
        

        self.channelID = gameLobby.channelID
        self.time = time.time()
        self.rules = {}
        self.players = []
        self.turnIndex = 0
        self.gameRunning = True
        self.reverse = False
        for playerID in gameLobby.players:
            self.players.append(Player(playerID, self))
            del(playersInLobby[playerID])
            playersInGame[playerID] = self.channelID
        openGames[self.channelID] = self
        self.deck = Deck()
        
        
        #print(self.channelID, self.players, self.time, self.deck, self.rules)

    async def startGame(self, client):

        print("Starting game...")

        self.currentCard = self.deck.drawCard()

        while self.currentCard.isColorChoice:
            self.deck.returnCard(self.currentCard)
            self.currentCard = self.deck.drawCard()

        print("First card found, starting players")

        for player in self.players:  #For each player in the list of players
            await player.start(client)  #Start that player
        print("Getting channel")
        channel = await client.fetch_channel(self.channelID)  #Get channel
        print("Sending message")
        gameMessage = await channel.send(embed = await self.gameStateEmbed(isDM = False, player = None, statusMessage = "Game started", client = client), content = "Game started")  #Send game message to channel
        self.gameMessageID = gameMessage.id  #Sets game messageID
        
        #Start first turn, either through the turn change function(todo, probably better) or just by initializing manually

    async def gameStateEmbed(self, isDM, player, statusMessage, client):  #Creates the content for the messages sent to a players DMs
        async def playerListString():
            playerList = []
            index = self.turnIndex
            for item in self.players:  #Creates a list of the players names who are in a game
                x = await client.fetch_user(item.playerID)
                x = x.name
                x = f"{x} - Cards: {str(len(item.hand))}"
                playerList.append(x)
            if self.reverse: arrow = "↑"  #If the game is reversed then the direction goes up
            else: arrow = "↓"  #If the game isn't reversed then the direction goes down
            playerList[index] = f"__{playerList[index]}__ {arrow}"
            playerList = "\n".join(playerList)
            return playerList    
        
        if isDM:             
            if self.players[self.turnIndex].playerID == player.playerID: turnStatus = "**It's your turn!**"
            else: 
                currentTurnUser = await self.currentTurnUser(client)
                turnStatus = f"It's {currentTurnUser.name}'s turn!"
            description = f"**Players:**\n{await playerListString()}\n{statusMessage}\n\n{turnStatus}"
            if not self.gameRunning:
                description = f"**{statusMessage}**"
            embed = discord.Embed(title = f"Uno2 game in <#{self.channelID}>", description = description, color = self.currentCard.colorCode())
            #embed.set_thumbnail(url = cardImages[self.topCard])
        else: 
            description = f"**Players:**\n{await playerListString()}\n{statusMessage}"
            if not self.gameRunning:
                description = f"**{statusMessage}**"
            embed = discord.Embed(title = f"Uno2 game in <#{self.channelID}>", description = description, color = self.currentCard.colorCode())
            #embed.set_thumbnail(url = cardImages[self.topCard])
        embed.set_thumbnail(url = self.currentCard.image)
        return embed

    

    async def currentTurnUser(self, client):
        return await client.fetch_user(self.players[self.turnIndex].playerID)

    async def channelName(self, client):
        channel = await client.fetch_channel(self.channelID)
        return channel.name

    def validCard(self, card):
        if card.face == self.currentCard.face or card.color == self.currentCard.color or card.color == "black":
            return True
        else:
            return False

    async def playCard(self, player, client, source = "hand", card = None):  #Assumes that the card is valid
        if source == "wild":
            selectedCard = card
        else:
            selectedCard = player.hand[player.selectedIndex]
            del(player.hand[player.selectedIndex])
            self.deck.returnCard(self.currentCard)  #Returns the top card to the deck
        self.currentCard = selectedCard
        reverse = False
        count = 1

        
        
        if selectedCard.isColorChoice:
            player.wildMessage = wildMessage(card = selectedCard, player = player, game = self)
            await player.wildMessage.sendMessage(client = client)
            count = 0
            statusMessage = "A color is being chosen"
        elif selectedCard.face == "skip":
            count = 2
        elif selectedCard.face == "reverse":
            reverse = True

        statusMessage = "Card played"  #TEMP
        await self.updateGame(reverse = reverse)
        await self.updateTurn(count = count)
        await self.updateMessages(statusMessage = statusMessage, client = client)
        await player.handMessage.updateMessage(amount = 0, client = client)

    async def updateGame(self, reverse = False):
        if reverse:
            self.reverse = (not self.reverse)
        

    async def updateTurn(self, count):
        self.turnIndex += count
        if self.turnIndex >= len(self.players):
            self.turnIndex -= (len(self.players))
        if self.turnIndex < 0:
            self.turnIndex += len(self.players)

    async def updateMessages(self, statusMessage, client):
        channel = await client.fetch_channel(self.channelID)  #Get channel
        gameMessage = await channel.fetch_message(self.gameMessageID)  #Get game message
        await gameMessage.edit(embed = await self.gameStateEmbed(isDM = False, player = None, statusMessage = statusMessage, client = client))  #Edit game message with new embed
        for player in self.players:
            user = await client.fetch_user(player.playerID)
            playerGameMessage = await user.fetch_message(player.gameMessageID)
            await playerGameMessage.edit(embed = await self.gameStateEmbed(isDM = True, player = player, statusMessage = statusMessage, client = client))

    async def playerLeave(self, userID, client):
        index = [player.playerID for player in self.players].index(userID)
        del(self.players[index])
        del(playersInGame[userID])
        if len(self.players) == 0:
            del openGames[self.channelID]
            channel = await client.fetch_channel(self.channelID)
            await channel.send("Game closed due to all players leaving")

        


   

class GameLobby:
    def __init__(self, ctx):
        self.channelID = ctx.channel.id
        self.players = []
    def playerJoin(self, userID):
        self.players.append(userID)
        playersInLobby[userID] = self.channelID
    def playerLeave(self, userID):
        self.players.remove(userID)
        del(playersInLobby[userID])
        if len(self.players) == 0:
            del(openLobbies[self.channelID])

class Player:
    def __init__(self, playerID, game):
        self.playerID = playerID
        self.hand = []
        self.game = game
        self.gameMessages = {}
        self.selectedIndex = 0
        self.state = "card"


    async def start(self, client):
        #Create hand for player
        i = 0
        while i < getRules(self.game.channelID)["startingCards"]:
            self.hand.append(self.game.deck.drawCard())
            i += 1
        

        user = await client.fetch_user(self.playerID)  #Get the user from discord
        gameMessage = await user.send(embed = await self.game.gameStateEmbed(isDM = True, player = self, statusMessage = "Game started", client = client))  #Send the user the game message
        self.gameMessageID = gameMessage.id  #Set the players game message ID
        self.handMessage = handMessage(self, self.game)
        await self.handMessage.sendMessage(client)

    async def drawCard(self, client):
        #Pick card from deck
        card = self.game.deck.drawCard()
        #Add to hand
        self.hand.append(card)
        #Edit message
        await self.handMessage.updateMessage(0, client)       
       
        
    
    
        

class handMessage:
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
        print("Reacting with card")
        await message.add_reaction(cardDictionaries.cardEmoji["back"])
        self.messageID = message.id  
        reactionMessageIDs[self.messageID] = self

    async def handEmbed(self):
        selectedCard = self.player.hand[self.player.selectedIndex]
        embed = discord.Embed(title = f"<@{self.userID}>'s hand", description = "Your Hand", color = selectedCard.colorCode())
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
            await OtherMessage("It's not your turn.", self.player).sendMessage(client)
            return
        elif not self.game.validCard(self.player.hand[self.player.selectedIndex]):
            await OtherMessage("You can't play that card.", self.player).sendMessage(client)
            return
        await self.game.playCard(self.player, client)

    async def drawCard(self, client):
        await self.player.drawCard(client)

class OtherMessage:
    def __init__(self, content, player):
        self.content = content
        self.player = player

    async def sendMessage(self, client):
        user = await client.fetch_user(self.player.playerID)  #Get the user the message is being sent to
        message = await user.send(self.content)
        await asyncio.sleep(5)
        await message.delete()


class wildMessage:
    def __init__(self, card, player, game):
        self.userID = player.playerID
        self.type = "wild"
        self.game = game
        self.card = card
        self.player = player

    async def sendMessage(self, client):
        self.player.state = "wild"
        user = await client.fetch_user(self.userID)
        message = await user.send(embed = self.wildEmbed())
        await message.add_reaction("🟥")
        await message.add_reaction("🟨")
        await message.add_reaction("🟩")
        await message.add_reaction("🟦")    
        self.messageID = message.id  
        reactionMessageIDs[self.messageID] = self

    def wildEmbed(self):
        embed = discord.Embed(title = f"Choose a color", description = self.card.face, color = self.card.colorCode())
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

class Stack:
    def __init__(self, game):
        self.game = game
        game.stack = True

    def startStack(self, card):
        if card.face == "plus2": self.amount = 2
        elif card.face == "plus4": self.amount = 4
        self.recentCard = card

    def canStack(self, player):
        if "plus2" or "plus4" in [card.face for card in player.hand]: return True
        else: return False

    def addStack(self, card):
        if card.face == "plus2": self.amount += 2
        elif card.face == "plus4" and card.color == "black": self.amount += 4
        self.recentCard == card

    def endStack(self, client):
        i = self.amount
        while i > 0:
            self.game.players[self.game.currentTurnIndex].drawCard(client)
            i -= 1

class stackMessage:
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
        embed = discord.Embed(title = f"<@{self.userID}>'s stackable cards", description = "Choose a card to stack (or draw cards instead)", color = selectedCard.colorCode())
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
            await OtherMessage("It's not your turn.", self.player).sendMessage(client)
            return
        elif not self.game.validCard(self.stackHand[self.index]):
            await OtherMessage("You can't play that card.", self.player).sendMessage(client)
            return
        await self.game.playCard(self.player, client)
        await self.deleteMessage()

    async def deleteMessage(self, client):
        user = await client.fetch_user(self.userID)
        message = await user.fetch_message(self.messageID)
        await message.delete()


class Deck:
    def __init__(self):
        colors = ["red", "yellow", "green", "blue"]
        faces = [0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, "skip", "skip", "reverse", "reverse", "plus2", "plus2"]
        self.cards = []
        for color in colors:
            for face in faces:
                self.cards.append(Card(color, face))
        count = 0
        while count < 4:
            self.cards.append(Card("black", "wild", True))
            self.cards.append(Card("black", "plus4", True))
            count += 1

    def drawCard(self):
        cardIndex = random.randint(0, len(self.cards) - 1)
        returnCard = self.cards[cardIndex]
        self.cards.remove(returnCard)
        return returnCard

    def returnCard(self, card):
        if not card.returnable == False:
            self.cards.append(card)

class Card:
    def __init__(self, color, face, isColorChoice = False, returnable = True):
        self.isColorChoice = isColorChoice
        self.color = color
        self.returnable = returnable
        self.face = face
        self.image = cardDictionaries.cardImages[str(face) + "_" + color]
        self.emoji = cardDictionaries.cardEmoji[str(face) + "_" + color]

    def colorCode(self):
        if self.color == "blue": return 29372               
        elif self.color == "green": return 5876292
        elif self.color == "yellow": return 16768534
        elif self.color == "red": return 15539236
        else: return 4802889


def getRules(channelID):
    rules = json.load(open("storage/channelRulesets.json", "r"))
    if str(channelID) in rules.keys():
        return rules[str(channelID)]
    else:
        ruleset = {
            "startingCards" : 7,
            "jumpIns" : True,
            "stacking" : True,
            "forceplay" : False,
            "drawToMatch" : True
        }
        rules[channelID] = ruleset
        json.dump(rules, open("storage/channelRulesets.json", "w"))
        return rules[str(channelID)]

def channelInGame(channelID):
    print(channelID, openGames)
    if channelID in openGames.keys(): return True
    else: return False
    

def channelHasLobby(channelID):
    if channelID in openLobbies.keys(): return True
    else: return False

def playerInGame(userID):
    if userID in playersInGame.keys(): return True
    else: return False

def playerInLobby(userID):
    if userID in playersInLobby.keys(): return True
    else: return False