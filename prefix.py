from pathlib import Path
import pickle

try:  #Trys to open and unpickle the file. If any one of those fails, the dictionary is set to a blank dictionary for the change prefix code to initialize later
    prefixFile = open("prefixList.pickle", "rb")
    prefixDict = pickle.load(prefixFile)
    prefixFile.close
    
except: prefixDict = {}

def changePrefix(message):
    '''Changes the prefix for a given serverID. Works as a direct response to a prefix command with no pre- or post- processing.

        Parameters:
            message: The message object from discord from the command sent
        
        Returns:
            Response(str): Either a success message with the new prefix or an error message.
        '''
    serverID = message.guild.id
    messageContent = message.content
    if len(messageContent.split()) < 2: return "You can't use a blank prefix!"  #If there is nothing after the prefix command, then return an error. 
    else: prefix = messageContent.split()[1]  #Sets the prefix to the prefix defined in the message
    if len(prefix) > 5:  #If the prefix is over 5 characters, then return error
        return "That prefix is too long!"
    prefixDict[serverID] = prefix  #Sets the prefix for the given serverID to the new prefix
    prefixFile = open("prefixList.pickle", "wb+")
    pickle.dump(prefixDict, prefixFile)
    return f"Set prefix to `{prefix}`"

def getPrefix(client, message):
    '''Gets the prefix for a given serverID. Returns the prefix as a string Defaults to "uno!"'''
    serverID = message.guild.id
    if serverID in prefixDict.keys():  #If the server ID is in the dictionary of IDs, then return the prefix for that ID. If not, then return the default prefix
        return prefixDict[serverID]
    else:
        return "uno!"