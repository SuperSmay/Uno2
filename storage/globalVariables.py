reactionMessageIDs = {
    
}

openGames = {

}

openLobbies = {

}

playersInGame = {

}

playersInLobby = {
    
}

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