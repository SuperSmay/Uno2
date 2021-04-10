from globalVariables import reactionMessageIDs

async def help(emoji, message, user, client):
    helpMessageObject = reactionMessageIDs[message.id]
    if user.id != helpMessageObject.userID:
        return
    if emoji.name == "◀️":
        #print(f"Current index:{helpMessageObject.index}")
        helpMessageObject.index -= 1
        #print(f"New index:{helpMessageObject.index}")
        if helpMessageObject.index < 0: helpMessageObject.index = len(helpMessageObject.helpPages) - 1
        #print(f"Final index:{helpMessageObject.index}")
    elif emoji.name == "▶️":
        #print(f"Current index:{helpMessageObject.index}")
        helpMessageObject.index += 1
        #print(f"New index:{helpMessageObject.index}")
        if helpMessageObject.index >= len(helpMessageObject.helpPages): helpMessageObject.index = 0
        #print(f"Final index:{helpMessageObject.index}")
    await helpMessageObject.updateMessage(client)


async def hand(emoji, message, user, client):
    handMessageObject = reactionMessageIDs[message.id]
    if user.id != handMessageObject.userID:
        return
    if not handMessageObject.player.state == "card":
        return
    if emoji.name == "⏪":
        await handMessageObject.updateMessage(-2, client)
    elif emoji.name == "◀️":
        await handMessageObject.updateMessage(-1, client)
    elif emoji.name == "⏺️":
        await handMessageObject.attemptPlayCard(client)
    elif emoji.name == "▶️":
        await handMessageObject.updateMessage(1, client)
    elif emoji.name == "⏩":
        await handMessageObject.updateMessage(2, client)

async def wild(emoji, message, user, client):
    print("wild played")
    wildMessageObject = reactionMessageIDs[message.id]
    if user.id != wildMessageObject.userID:
        return
    if not wildMessageObject.player.state == "wild":
        return
    if emoji.name == "🟥":
        await wildMessageObject.pickColor("red", client)
    elif emoji.name == "🟨":
        await wildMessageObject.pickColor("yellow", client)
    elif emoji.name == "🟩":
        await wildMessageObject.pickColor("green", client)
    elif emoji.name == "🟦":
        await wildMessageObject.pickColor("blue", client)
    print("Wild sent")


