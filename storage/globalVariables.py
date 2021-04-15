import json

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

def getRules(channelID):
    rules = json.load(open("storage/channelRulesets.json", "r"))
    if str(channelID) in rules.keys():
        return rules[str(channelID)]
    else:
        ruleset = {
            "startingCards" : 7,
            "jumpIns" : True,
            "stacking" : False,
            "forceplay" : False,
            "drawToMatch" : True
        }
        rules[str(channelID)] = ruleset
        json.dump(rules, open("storage/channelRulesets.json", "w"))
        return rules[str(channelID)]