import asyncio
import discord
import time

from discord.embeds import Embed
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
        self.playerStartedCount = 0
        self.reverse = False
        self.stackActive = False
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
            client.loop.create_task(player.start(client))   #Start that player in a background task
        channel = await client.fetch_channel(self.channelID)  #Get channel
        while self.playerStartedCount < len(self.players):
            await asyncio.sleep(0.5)
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
        if not self.gameRunning: description = f"**Players:**\n{await playerListString()}\n\n{statusMessage}"
        else: description = f"**Players:**\n{await playerListString()}\n\n{statusMessage}\n\n{turnStatus}"
        embed = discord.Embed(title = f"Uno2 game in <#{self.channelID}>", description = description, color = self.currentCard.colorCode)
        if self.stackActive:
            embed.add_field(name = "Current stack count:", value=f"{self.stack.amount} cards")
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

    async def gameWon(self, player, client):

        async def deleteAllMessages(player, client):
            try: player.handMessage.deleteMessage(client)
            except: pass
            try: player.wildMessage.deleteMessage(client)
            except: pass
            try: player.stackMessage.deleteMessage(client)
            except: pass

        self.gameRunning = False
        user = await client.fetch_user(player.playerID)
        client.loop.create_task(deleteAllMessages(client))

        channel = await client.fetch_channel(self.channelID)  #Get channel
        gameMessage = await channel.fetch_message(self.gameMessageID)  #Get game message
        embed = discord.Embed(title = f"Uno2 game in <#{self.channelID}>", description = f"{user.name} won the game!", color = self.currentCard.colorCode)
        client.loop.create_task(gameMessage.edit(embed = embed))  #Edit game message with new embed
        for player in self.players:
            user = await client.fetch_user(player.playerID)
            playerGameMessage = await user.fetch_message(player.gameMessageID)
            client.loop.create_task(playerGameMessage.edit(embed = embed))


    async def playCardGeneric(self, player, client, card):  #Assumes that the card is valid
        user = await client.fetch_user(player.playerID)
        self.deck.returnCard(self.currentCard)  #Returns the top card to the deck
        self.currentCard = card 
        player.hand.remove(card)
        if len(player.hand) == 0:
            await self.gameWon(player, client)
            return 
        client.loop.create_task(player.handMessage.updateMessage(amount = 0, client = client))
        player.drewCard = False
        statusMessage = f"{user.name} played a card"
        self.incrementTurn()
        return statusMessage

    async def passTurn(self, player, client):
        user = await client.fetch_user(player.playerID)
        statusMessage = f"{user.name} drew and passed their turn"
        self.incrementTurn()
        player.drewCard = False
        return statusMessage

    async def skipTurn(self, client):
        user = await client.fetch_user(self.players[self.turnIndex].playerID)
        statusMessage = f"{user.name} was skipped"
        self.incrementTurn()
        return statusMessage

    async def playPlus2(self, client, card):
        rules = getRules(self.channelID)
        if not rules["stacking"]:
            currentPlayer = self.players[self.turnIndex]
            currentUser = await client.fetch_user(currentPlayer.playerID)
            self.player.drawCard(client, count = 2, drawToMatch = False, canPlay = False)
            self.incrementTurn()
            statusMessage = f"{currentUser.name} drew 2 cards"
        else:
            #Do stack stuff
            if self.stackActive:
                self.stack.addStack(card)
            else:
                self.stack = Stack(self)
                self.stack.startStack(card)
            currentPlayer = self.players[self.turnIndex]
            currentUser = await client.fetch_user(currentPlayer.playerID)
            print("Can stack? " + str(self.stack.canStack(currentPlayer)))
            if self.stack.canStack(currentPlayer):
                messageClasses.StackMessage(currentPlayer, self)
                await currentPlayer.stackMessage.sendMessage(client)
                statusMessage = f"{currentUser.name} started a stack!"
            else:
                await self.stack.endStack(client)
                statusMessage = f"{currentUser.name} drew {self.stack.amount} cards"
        return statusMessage

    ### Wild and plus 4

    async def startWild(self, player, client, card):
        user = await client.fetch_user(player.playerID)
        player.hand.remove(card)
        self.deck.returnCard(self.currentCard)  #Returns the top card to the deck
        self.currentCard = card
        if len(player.hand) == 0:
            await self.gameWon(player, client)
            return
        messageClasses.WildMessage(player = player, game = self)
        client.loop.create_task(player.handMessage.updateMessage(amount = 0, client = client))
        client.loop.create_task(player.wildMessage.sendMessage(client = client))
        statusMessage = f"{user.name} is chose a color"
        return statusMessage

    async def endWild(self, player, client, card):
        user = await client.fetch_user(player.playerID)
        self.currentCard = card 
        statusMessage = f"{user.name} chose {card.color}"
        self.incrementTurn()
        return statusMessage

    async def startPlus4(self, player, client, card):
        rules = getRules(self.channelID)
        user = await client.fetch_user(player.playerID)
        player.hand.remove(card)
        self.deck.returnCard(self.currentCard)  #Returns the top card to the deck
        self.currentCard = card
        if len(player.hand) == 0:
            await self.gameWon(player, client)
            return
        messageClasses.Plus4Message(player = player, game = self)
        client.loop.create_task(player.handMessage.updateMessage(amount = 0, client = client))
        client.loop.create_task(player.wildMessage.sendMessage(client = client))
        statusMessage = f"{user.name} is chosing a color"
        #TODO - If card is a plus card, check stack rule then start stack, or if source is stack then add to the current stack
        if self.stackActive:
            self.stack.addStack(card)
        elif rules["stacking"]:
            self.stack = Stack(self)
            self.stack.startStack(card)
        return statusMessage

    async def endPlus4(self, player, client, card):
        rules = getRules(self.channelID)
        user = await client.fetch_user(player.playerID)
        self.currentCard = card 
        self.incrementTurn()
        if not rules["stacking"]:
            currentPlayer = self.players[self.turnIndex]
            currentUser = await client.fetch_user(currentPlayer.playerID)
            self.player.drawCard(client, count = 4, drawToMatch = False, canPlay = False)
            self.incrementTurn()
            statusMessage = f"{user.name} chose {card.color}, and {currentUser.name} drew 4 cards"
        else:
            #Do stack stuff
            currentPlayer = self.players[self.turnIndex]
            currentUser = await client.fetch_user(currentPlayer.playerID)
            print("Can stack? " + str(self.stack.canStack(currentPlayer)))
            if self.stack.canStack(currentPlayer):
                messageClasses.StackMessage(currentPlayer, self)
                await currentPlayer.stackMessage.sendMessage(client)
                statusMessage = f"{currentUser.name} started a stack!"
            else:
                await self.stack.endStack(client)
                statusMessage = f"{currentUser.name} drew {self.stack.amount} cards"
        return statusMessage

    ###

    async def playCard(self, client, player, card):  #Assumes valid card
        if card.face == "skip":
            await self.playCardGeneric(player, client, card)
            statusMessage = await self.game.skipTurn(client)
        elif card.face == "reverse":
            await self.playCardGeneric(player, client, card)
            statusMessage = self.updateReverse()
        elif card.face == "plus2":
            await self.playCardGeneric(player, client, card)
            statusMessage = await self.playPlus2(client, card)
        elif card.face == "plus4":
            statusMessage = await self.startPlus4(player, client, card)
        elif card.face == "wild":
            statusMessage = await self.startWild(player, client, card)
        else: 
            statusMessage = await self.playCardGeneric(player, client, card)
        await self.updateGameMessages(statusMessage, client)

    def updateReverse(self):
        self.reverse = (not self.reverse)
        return "The direction was reversed"
        
    def incrementTurn(self):
        self.turnIndex += 1
        if self.turnIndex >= len(self.players):
            self.turnIndex -= (len(self.players))
        if self.turnIndex < 0:
            self.turnIndex += len(self.players)

    async def updateGameMessages(self, statusMessage, client):

        async def updatePlayer(player):
            user = await client.fetch_user(player.playerID)
            playerGameMessage = await user.fetch_message(player.gameMessageID)
            await playerGameMessage.edit(embed = await self.gameStateEmbed(isDM = True, player = player, statusMessage = statusMessage, client = client))

        if not self.gameRunning:
            return
        channel = await client.fetch_channel(self.channelID)  #Get channel
        gameMessage = await channel.fetch_message(self.gameMessageID)  #Get game message
        client.loop.create_task(gameMessage.edit(embed = await self.gameStateEmbed(isDM = False, player = None, statusMessage = statusMessage, client = client)))  #Edit game message with new embed
        for player in self.players:
            client.loop.create_task(updatePlayer(player))
            

    async def playerLeave(self, userID, client):
        index = [player.playerID for player in self.players].index(userID)
        del(self.players[index])
        del(playersInGame[userID])
        if len(self.players) <= 1:
            del openGames[self.channelID]
            channel = await client.fetch_channel(self.channelID)
            await channel.send("Game closed due to too many players leaving")

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
        self.game.playerStartedCount += 1

    async def drawCard(self, client, count = 0, drawToMatch = False, canPlay = True):
        #Pick card from deck
        self.drawMessage = messageClasses.DrawMessage(self, self.game)
        await self.drawMessage.drawCards(count, drawToMatch)
        await self.drawMessage.sendMessage(client)

class Stack:
    def __init__(self, game):
        self.game = game
        game.stackActive = True

    def startStack(self, card):
        if card.face == "plus2": self.amount = 2
        elif card.face == "plus4": self.amount = 4
        self.recentCard = card

    def canStack(self, player):
        if len([card for card in player.hand if (card.face == "plus2" and card.color == self.game.currentCard.color) or card.face == "plus4" or (card.face == "plus2" and self.game.currentCard.face == "plus2")]) > 0: return True
        else: return False

    def addStack(self, card):
        if card.face == "plus2": self.amount += 2
        elif card.face == "plus4" and card.color == "black": self.amount += 4
        self.recentCard == card

    async def endStack(self, client):
        self.game.players[self.game.turnIndex].drawCard(client, count = self.amount, drawToMatch = False, canPlay = False)
        self.game.incrementTurn()
        self.game.stackActive = False
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