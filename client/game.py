import asyncio
import discord
import time
from storage.globalVariables import openGames, openLobbies, playersInGame, playersInLobby, channelInGame, channelHasLobby, playerInGame, playerInLobby, getRules
import random
from client.cardClass import Card, FakeCard
import client.messageClasses as messageClasses

class Game:
    def __init__(self, gameLobby):
        self.channelID = gameLobby.channelID
        self.time = time.time()  #Time game was started
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

    async def startGame(self, client):
        self.currentCard = self.deck.drawCard()
        while self.currentCard.isColorChoice:
            self.deck.returnCard(self.currentCard)
            self.currentCard = self.deck.drawCard()
        for player in self.players:  #For each player in the list of players
            await player.start(client)  #Start that player
        channel = await client.fetch_channel(self.channelID)  #Get channel
        gameMessage = await channel.send(embed = await self.gameStateEmbed(isDM = False, player = None, statusMessage = "Game started", client = client), content = "Game started")  #Send game message to channel
        self.gameMessageID = gameMessage.id  #Sets game messageID

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
        
        currentTurnUser = await self.currentTurnUser(client)
        turnStatus = f"It's {currentTurnUser.name}'s turn!"
        if isDM:  #If the message is being sent in a DM, the description is changed
            if self.players[self.turnIndex].playerID == player.playerID:  #If its the current players turn, then change the message to say that
                turnStatus = "**It's your turn!**"
                if not self.gameRunning: 
                    statusMessage = "**You won the game!**"
        if not self.gameRunning: description = f"**Players:**\n{await playerListString()}\n\n{statusMessage}"
        else: description = f"**Players:**\n{await playerListString()}\n\n{statusMessage}\n\n{turnStatus}"
        embed = discord.Embed(title = f"Uno2 game in <#{self.channelID}>", description = description, color = self.currentCard.colorCode)
        embed.set_thumbnail(url = self.currentCard.image)
        return embed

    async def currentTurnUser(self, client):  #Get the user object for the player who's turn it is
        return await client.fetch_user(self.players[self.turnIndex].playerID)

    async def channelName(self, client):  #Get the name of the channel the game is in
        channel = await client.fetch_channel(self.channelID)
        return channel.name

    def validCard(self, card):  #If the card is a valid one to play, return true
        if card.face == self.currentCard.face or card.color == self.currentCard.color or card.color == "black":
            return True
        else:
            return False

    async def playCard(self, player, client, card):  #Assumes that the card is valid
        user = await client.fetch_user(player.playerID)
        player.hand.remove(card)
        self.deck.returnCard(self.currentCard)  #Returns the top card to the deck
        self.currentCard = card 
        await player.handMessage.updateMessage(amount = 0, client = client)
        player.drewCard = False
        statusMessage = f"{user.name} played a card"
        self.incrementTurn()
        await self.updateGameMessages(statusMessage = statusMessage, client = client)

    async def startWild(self, player, client, card):
        user = await client.fetch_user(player.playerID)
        statusMessage = f"{user.name} is chose a color"
        self.deck.returnCard(self.currentCard)  #Returns the top card to the deck
        self.currentCard = card
        player.wildMessage = messageClasses.WildMessage(card = card, player = player, game = self)
        await player.wildMessage.sendMessage(client = client)
        await self.updateGameMessages(statusMessage = statusMessage, client = client)

    
    async def endWild(self, player, client, card):
        pass

    async def playPlus4(self, player, client, card):
        user = await client.fetch_user(player.playerID)
        self.deck.returnCard(self.currentCard)  #Returns the top card to the deck
        self.currentCard = card
        player.wildMessage = messageClasses.WildMessage(card = card, player = player, game = self)
        await player.wildMessage.sendMessage(client = client)
        statusMessage = f"{user.name} is chose a color"
        #TODO - If card is a plus card, check stack rule then start stack, or if source is stack then add to the current stack
        await self.updateGameMessages(statusMessage = statusMessage, client = client)

    async def passTurn(self, player, client, card):
        user = await client.fetch_user(player.playerID)
        selectedCard = FakeCard(self.currentCard)
        statusMessage = f"{user.name} drew and passed their turn"
        await self.updateGameMessages(statusMessage = statusMessage, client = client)

    async def skipTurn(self, player, client, card = None):
        self.incrementTurn()
        user = await client.fetch_user(player.playerID)
        selectedCard = FakeCard(self.currentCard)
        statusMessage = f"{user.name} was skipped"
        await self.updateGameMessages(statusMessage = statusMessage, client = client)

    def updateReverse(self):
        self.reverse = (not self.reverse)
        
    def incrementTurn(self):
        self.turnIndex += 1
        if self.turnIndex >= len(self.players):
            self.turnIndex -= (len(self.players))
        if self.turnIndex < 0:
            self.turnIndex += len(self.players)

    async def updateGameMessages(self, statusMessage, client):
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
        self.drewCard = False

    async def start(self, client):
        #Create hand for player
        i = 0
        while i < getRules(self.game.channelID)["startingCards"]:
            self.hand.append(self.game.deck.drawCard())
            i += 1
        user = await client.fetch_user(self.playerID)  #Get the user from discord
        gameMessage = await user.send(embed = await self.game.gameStateEmbed(isDM = True, player = self, statusMessage = "Game started", client = client))  #Send the user the game message
        self.gameMessageID = gameMessage.id  #Set the players game message ID
        self.handMessage = messageClasses.HandMessage(self, self.game)
        await self.handMessage.sendMessage(client)

    async def drawCard(self, client):
        #Pick card from deck
        card = self.game.deck.drawCard()
        #Add to hand
        self.hand.append(card)
        #Edit message
        await self.handMessage.updateMessage(0, client)
        return card

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