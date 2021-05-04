import asyncio
import random
import time

import discord
from storage.globalVariables import client, getRules, openGames, openLobbies, playersInGame, playersInLobby

import client.messageClasses as messageClasses
from client.cardClass import Card


class Game:
    def __init__(self, gameLobby):
        '''
        A game object for Uno.\n
        Attributes:
            - channelID: int; The ID of the channel the game is hosted in 
            - rules: dict; The rules for the game, stored "ruleName" : Value
            - players: list[Player]; The list of players who are in the game
            - turnIndex: int; Index of who's turn it is in the lsit of players
            - gameRunning: bool; Whether or not the game is running
            - playerStartedCount: int; The number of players who have been correctly started
            - reverse: bool; Whether the gameplay direction is reversed or not
            - stackActive: bool; Whether or not a stack is currently active in the game
            - deck: Deck; The deck for the game
        '''
        self.channelID = gameLobby.channelID
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

    async def startGame(self) -> None:
        '''
        Starts the game. Sets up the game deck and rules, sends all base messages to all players, and adds game to the openGames dictionary.\n
        Returns: None
        '''
        openGames[self.channelID] = self  #Store the game object in the games dictionary with the key of the channelID
        self.currentCard = self.deck.drawCard()  #Draws a starting card
        while self.currentCard.face == "plus4" or self.currentCard.face == "wild":  #If the card is a wild or plus4, return it to the deck and try again
            self.deck.returnCard(self.currentCard)
            self.currentCard = self.deck.drawCard()
        for player in self.players:  #For each player in the list of players
            client.loop.create_task(player.start())   #Start that player in a background task
        while self.playerStartedCount < len(self.players):  #Wait for all players to start
            await asyncio.sleep(0.5)
        channel = await client.fetch_channel(self.channelID)  #Get channel
        gameMessage = await channel.send(embed = await self.gameStateEmbed(isDM = False, player = None, statusMessage = "Game started"), content = "Game started")  #Send game message to channel
        self.gameMessageID = gameMessage.id  #Sets game messageID

    async def gameStateEmbed(self, isDM: bool, player, statusMessage: str) -> discord.Embed:
        '''
        Creates the embeds for the game message.\n
        Parameters:
            - isDM: bool; Whether the embed is being generated for a DM.\n
            - player: Player; Object for the player the message is being sent to. Ignored if isDM = False.\n
            - statusMessage: str; The message to be incuded in the returned embed.\n
        Returns: discord.Embed; The game embed of the current game state
        '''
        async def playerListString() -> str:
            '''
            Returns: str; A list of all the player names in the game sepated by linebreaks
            '''
            playerList = []
            index = self.turnIndex
            for [player] in self.players:  #Creates a list of the players names who are in a game
                user = await client.fetch_user(player.playerID)
                userName = user.name
                completeLine = f"{userName} - Cards: {str(len(player.hand))}"
                playerList.append(completeLine)
            if self.reverse: arrow = "↑"  #If the game is reversed then the direction goes up
            else: arrow = "↓"  #If the game isn't reversed then the direction goes down
            playerList[index] = f"__{playerList[index]}__ {arrow}"  #Underline the player whose turn it is
            playerList = "\n".join(playerList)  #Join all the lines together into one string separated by linebreaks
            return playerList    
        
        currentTurnUser = await self.currentTurnUser()  
        turnStatus = f"It's {currentTurnUser.name}'s turn!"
        if isDM:  #If the message is being sent in a DM, the description is changed
            if self.players[self.turnIndex].playerID == player.playerID:  #If its the current players turn, then change the message to say that
                turnStatus = "**It's your turn!**"
        if not self.gameRunning: description = f"**Players:**\n{await playerListString()}\n\n{statusMessage}"
        else: description = f"**Players:**\n{await playerListString()}\n\n{statusMessage}\n\n{turnStatus}"
        embed = discord.Embed(title = f"Uno2 game in <#{self.channelID}>", description = description, color = self.currentCard.colorCode)  #Create embed
        if self.stackActive:
            embed.add_field(name = "Current stack count:", value=f"{self.stack.amount} cards")
        embed.set_thumbnail(url = self.currentCard.image)
        return embed

    async def currentTurnUser(self) -> discord.User:  
        '''
        Returns: discord.User; The user object for the player who's turn it is
        '''
        return await client.fetch_user(self.players[self.turnIndex].playerID)

    async def channelName(self) -> str:
        '''
        Returns: str; The name of the channel the game is in
        '''
        channel = await client.fetch_channel(self.channelID)
        return channel.name

    def validCard(self, card) -> bool:  
        '''
        Checks if the card is a valid one to play.\n
        Parameters:
            - card: Card; The card to check\n
        Returns: bool; Whether the card is valid to play or not
        '''
        if card.face == self.currentCard.face or card.color == self.currentCard.color or card.color == "black":
            return True
        else:
            return False

    async def gameWon(self, player) -> None:
        '''
        Ends the game. Deletes all non game message messages, edits the game message to say who won, and removes game from the openGames dict and players from the playersInGame dict.\n
        Parameters:
            - player: Player; The Player object of the player who won\n
        Returns: None
        '''

        async def deleteAllMessages(player) -> None:  
            '''
            Trys to delete any messages that may remain\n
            Parameters:
                - player: Player; The Player object to delete messages from\n
            Returns: None
            '''
            try: player.handMessage.deleteMessage()
            except: pass
            try: player.wildMessage.deleteMessage()
            except: pass
            try: player.stackMessage.deleteMessage()
            except: pass
            try: player.drawMessage.deleteMessage()
            except: pass

        self.gameRunning = False
        user = await client.fetch_user(player.playerID)  #Get user from player passed in

        channel = await client.fetch_channel(self.channelID)  #Get channel
        gameMessage = await channel.fetch_message(self.gameMessageID)  #Get game message
        embed = discord.Embed(title = f"Uno2 game in <#{self.channelID}>", description = f"{user.name} won the game!", color = self.currentCard.colorCode)
        client.loop.create_task(gameMessage.edit(embed = embed))  #Edit game message with new embed
        for player in self.players:
            user = await client.fetch_user(player.playerID)
            playerGameMessage = await user.fetch_message(player.gameMessageID)
            client.loop.create_task(playerGameMessage.edit(embed = embed))  #Set the embed in the game message to the win embed
            client.loop.create_task(deleteAllMessages(player))  #Delete all extra messages for player
            del(playersInGame[player.playerID])  #Remove player from the dict of players who are in games
        del(openGames[self.channelID])  #Delete the game from thw game list dict

    async def playCardGeneric(self, player, card) -> str:  #Assumes that the card is valid
        '''
        Plays the given card from the given player.\n
        #### Assumes that the player and card are valid to be played.\n
        Parameters:
            - player: Player; The player playing the card
            - card: Card; The card being played\n
        Returns: str; The status message of the player playing the card
        '''
        user = await client.fetch_user(player.playerID)
        self.deck.returnCard(self.currentCard)  #Returns the top card to the deck
        self.currentCard = card  #Sets new top card
        player.hand.remove(card)  #Removes the card. Works correctly because card is a reference type so the same card that was played is the one that is removed
        if len(player.hand) == 0:  #If the player ran out of cards;
            await self.gameWon(player)
            return 
        client.loop.create_task(player.handMessage.updateMessage(amount = 0))  #Update the players hand
        player.drewCard = False  #Update drewCard to allow player to draw again
        statusMessage = f"{user.name} played a card"
        self.incrementTurn()
        return statusMessage

    async def passTurn(self, player) -> str:
        '''
        Passes the current player's turn.\n
        #### Assumes that the player is allowed to be passing their turn.\n
        Parameters:
            - player: Player; The player playing the card\n
        Returns: str; The status message of the player passing their
        '''
        user = await client.fetch_user(player.playerID)
        statusMessage = f"{user.name} drew and passed their turn"
        self.incrementTurn()
        player.drewCard = False
        return statusMessage

    async def skipTurn(self) -> str:
        '''
        Skips the current players turn.\n
        Returns: str; The status message of the player being skipped
        '''
        user = await client.fetch_user(self.players[self.turnIndex].playerID)
        statusMessage = f"{user.name} was skipped"
        self.incrementTurn()
        return statusMessage

    async def playPlus2(self, card) -> str:
        '''
        Plays the given plus 2. If stacking is enabled and no stack is found, then a new one is started. If a stack is found, then it is added to.\n
        Also checks if the next player can add to the stack. If they cannot, then the stack is closed via stack.endStack().\n
        #### Assumes that the card is valid and that playCardGeneric was already run.\n
        Parameters:
            - card: Card; The card being played\n
        Returns: str; The status message of the player drawing cards
        '''
        rules = getRules(self.channelID)
        if not rules["stacking"]:  #If stacking is off
            currentPlayer = self.players[self.turnIndex]
            currentUser = await client.fetch_user(currentPlayer.playerID)
            self.player.drawCard(client, count = 2, drawToMatch = False, canPlay = False)  #Make the current player draw 2 cards
            self.incrementTurn()  #Then skip their turn
            statusMessage = f"{currentUser.name} drew 2 cards"
        else:
            #Do stack stuff
            if self.stackActive:  #If a stack is already running
                self.stack.addStack(card)  #Add to it
            else:
                self.stack = Stack(self)  #Create a new stack
                self.stack.startStack(card)  #Start the stack
            currentPlayer = self.players[self.turnIndex]
            currentUser = await client.fetch_user(currentPlayer.playerID)
            print("Can stack? " + str(self.stack.canStack(currentPlayer)))
            if self.stack.canStack(currentPlayer):
                messageClasses.StackMessage(currentPlayer, self)
                await currentPlayer.stackMessage.sendMessage()
                statusMessage = f"{currentUser.name} started a stack!"
            else:
                await self.stack.endStack()
                statusMessage = f"{currentUser.name} drew {self.stack.amount} cards"
        return statusMessage

    ### Wild and plus 4

    async def startWild(self, player, card) -> str:
        '''
        Plays the given wild card.\n
        Creates and sends the user the wild message.\n
        #### Assumes that the card is valid and that playCardGeneric NOT was already run.\n
        Parameters:
            - player: Player; The player playing the card
            - card: Card; The card being played\n
        Returns: str; The status message of the player choosing a color
        '''
        user = await client.fetch_user(player.playerID)
        player.hand.remove(card)
        self.deck.returnCard(self.currentCard)  #Returns the top card to the deck
        self.currentCard = card
        if len(player.hand) == 0:
            await self.gameWon(player)
            return
        messageClasses.WildMessage(player = player, game = self)
        client.loop.create_task(player.handMessage.updateMessage(amount = 0))
        client.loop.create_task(player.wildMessage.sendMessage())
        statusMessage = f"{user.name} is choosing a color"
        return statusMessage

    async def endWild(self, player, card) -> str:
        '''
        Plays the given colored wild.\n
        #### Assumes that the card is valid and that playCardGeneric NOT was already run.\n
        Parameters:
            - player: Player; The player playing the card
            - card: Card; The card being played\n
        Returns: str; The status message of the color chosen
        '''
        user = await client.fetch_user(player.playerID)
        self.currentCard = card 
        statusMessage = f"{user.name} chose {card.color}"
        self.incrementTurn()
        return statusMessage

    async def startPlus4(self, player, card) -> str:
        '''
        Plays the given plus 4. If stacking is enabled and no stack is found, then a new one is started. If a stack is found, then it is added to.\n
        Also checks if the next player can add to the stack. If they cannot, then the stack is closed via stack.endStack().\n
        #### Assumes that the card is valid and that playCardGeneric NOT was already run.\n
        Parameters:
            - player: Player; The player playing the card
            - card: Card; The card being played\n
        Returns: str; The status message of the player choosing a color
        '''
        rules = getRules(self.channelID)
        user = await client.fetch_user(player.playerID)
        player.hand.remove(card)
        self.deck.returnCard(self.currentCard)  #Returns the top card to the deck
        self.currentCard = card
        if len(player.hand) == 0:
            await self.gameWon(player)
            return
        messageClasses.Plus4Message(player = player, game = self)
        client.loop.create_task(player.handMessage.updateMessage(amount = 0))
        client.loop.create_task(player.wildMessage.sendMessage())
        statusMessage = f"{user.name} is choosing a color"
        #TODO - If card is a plus card, check stack rule then start stack, or if source is stack then add to the current stack
        if self.stackActive:
            self.stack.addStack(card)
        elif rules["stacking"]:
            self.stack = Stack(self)
            self.stack.startStack(card)
        return statusMessage

    async def endPlus4(self, player, card) -> str:
        '''
        Plays the given colored plus 4. If stacking is enabled, then it is added to.\n
        Also checks if the next player can add to the stack. If they cannot, then the stack is closed via stack.endStack().\n
        #### Assumes that the card is valid and that playCardGeneric NOT was already run.\n
        Parameters:
            - player: Player; The player playing the card
            - card: Card; The card being played\n
        Returns: str; The status message of the player drawing cards
        '''
        rules = getRules(self.channelID)
        user = await client.fetch_user(player.playerID)
        self.currentCard = card 
        self.incrementTurn()
        if not rules["stacking"]:
            currentPlayer = self.players[self.turnIndex]
            currentUser = await client.fetch_user(currentPlayer.playerID)
            self.player.drawCard(count = 4, drawToMatch = False, canPlay = False)
            self.incrementTurn()
            statusMessage = f"{user.name} chose {card.color}, and {currentUser.name} drew 4 cards"
        else:
            #Do stack stuff
            currentPlayer = self.players[self.turnIndex]
            currentUser = await client.fetch_user(currentPlayer.playerID)
            print("Can stack? " + str(self.stack.canStack(currentPlayer)))
            if self.stack.canStack(currentPlayer):
                messageClasses.StackMessage(currentPlayer, self)
                await currentPlayer.stackMessage.sendMessage()
                statusMessage = f"{currentUser.name} started a stack!"
            else:
                await self.stack.endStack()
                statusMessage = f"{currentUser.name} drew {self.stack.amount} cards"
        return statusMessage

    ###

    async def playCard(self, player, card) -> None:  #Assumes valid card
        '''
        Plays the given card by calling the correct series of functions for that card type.\n
        #### Assumes that the card is valid.\n
        Parameters:
            - player: Player; The player playing the card
            - card: Card; The card being played\n
        Returns: None
        '''
        if card.face == "skip":
            await self.playCardGeneric(player, card)
            statusMessage = await self.game.skipTurn()
        elif card.face == "reverse":
            await self.playCardGeneric(player, card)
            statusMessage = self.updateReverse()
        elif card.face == "plus2":
            await self.playCardGeneric(player, card)
            statusMessage = await self.playPlus2(card)
        elif card.face == "plus4":
            statusMessage = await self.startPlus4(player, card)
        elif card.face == "wild":
            statusMessage = await self.startWild(player, card)
        else: 
            statusMessage = await self.playCardGeneric(player, card)
        await self.updateGameMessages(statusMessage)

    def updateReverse(self) -> str:
        '''
        Flips the state of self.reverse.\n
        Parameters: None\n
        Returns: str; "The direction was reversed"
        '''
        self.reverse = (not self.reverse)
        return "The direction was reversed"
        
    def incrementTurn(self) -> None:
        '''
        Increments the turn, and also rolls the index over correctly when the index is outside the list of players.\n
        Parameters: None\n
        Returns: None
        '''
        self.turnIndex += 1
        if self.turnIndex >= len(self.players):
            self.turnIndex -= (len(self.players))
        if self.turnIndex < 0:
            self.turnIndex += len(self.players)

    async def updateGameMessages(self, statusMessage) -> None:
        '''
        Updates the game message of every player in the game.\n
        Parameters: 
            - statusMessage: str; The message to include with the game embed\n
        Returns: None
        '''
        async def updatePlayer(player) -> None:
            '''
            Helper function to update a single player.\n
            Parameters: 
                - player: Player; The player to update\n
            Returns: None
            '''
            user = await client.fetch_user(player.playerID)
            playerGameMessage = await user.fetch_message(player.gameMessageID)
            await playerGameMessage.edit(embed = await self.gameStateEmbed(isDM = True, player = player, statusMessage = statusMessage))

        if not self.gameRunning:
            return
        channel = await client.fetch_channel(self.channelID)  #Get channel
        gameMessage = await channel.fetch_message(self.gameMessageID)  #Get game message
        client.loop.create_task(gameMessage.edit(embed = await self.gameStateEmbed(isDM = False, player = None, statusMessage = statusMessage)))  #Edit game message with new embed
        for player in self.players:
            client.loop.create_task(updatePlayer(player))
            

    async def playerLeave(self, userID) -> None:
        '''
        Removes a player from the game.\n
        Parameters: 
            - userID: int; The ID of the discord user to remove\n
        Returns: None
        '''
        index = [player.playerID for player in self.players].index(userID)
        del(self.players[index])
        del(playersInGame[userID])
        if len(self.players) <= 1:
            del openGames[self.channelID]
            channel = await client.fetch_channel(self.channelID)
            await channel.send("Game closed due to too many players leaving")
        await self.updateGameMessages("Game closed due to too many players leaving")

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

    async def start(self):
        #Create hand for player
        i = 0
        while i < getRules(self.game.channelID)["startingCards"]:
            self.hand.append(self.game.deck.drawCard())
            i += 1
        user = await client.fetch_user(self.playerID)  #Get the user from discord
        gameMessage = await user.send(embed = await self.game.gameStateEmbed(isDM = True, player = self, statusMessage = "Game started"))  #Send the user the game message
        self.gameMessageID = gameMessage.id  #Set the players game message ID
        self.handMessage = messageClasses.HandMessage(self, self.game)
        await self.handMessage.sendMessage()
        self.game.playerStartedCount += 1

    async def drawCard(self, count = 0, drawToMatch = False, canPlay = True):
        #Pick card from deck
        self.drawMessage = messageClasses.DrawMessage(self, self.game)
        await self.drawMessage.drawCards(count, drawToMatch)
        await self.drawMessage.sendMessage()

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

    async def endStack(self):
        self.game.players[self.game.turnIndex].drawCard(count = self.amount, drawToMatch = False, canPlay = False)
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
            self.cards.append(Card("black", "wild"))
            self.cards.append(Card("black", "plus4"))
            count += 1

    def drawCard(self):
        cardIndex = random.randint(0, len(self.cards) - 1)
        returnCard = self.cards[cardIndex]
        self.cards.remove(returnCard)
        return returnCard

    def returnCard(self, card):
        if not card.returnable == False:
            self.cards.append(card)
