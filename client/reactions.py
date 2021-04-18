from storage.globalVariables import reactionMessageIDs, client

async def help(emoji, message, user):
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
    await helpMessageObject.updateMessage()


async def hand(emoji, message, user):
    handMessageObject = reactionMessageIDs[message.id]
    if user.id != handMessageObject.userID:
        return
    if not handMessageObject.player.state == "card":
        return
    if emoji.name == "⏪":
        client.loop.create_task(handMessageObject.updateMessage(-2))
    elif emoji.name == "◀️":
        client.loop.create_task(handMessageObject.updateMessage(-1))
    elif emoji.name == "⏺️":
        await handMessageObject.playCardButtonPressed()
    elif emoji.name == "▶️":
        client.loop.create_task(handMessageObject.updateMessage(1))
    elif emoji.name == "⏩":
        client.loop.create_task(handMessageObject.updateMessage(2))
    elif str(emoji) == "<:back:736433825097318541>":
        await handMessageObject.drawCard()

async def wild(emoji, message, user):
    wildMessageObject = reactionMessageIDs[message.id]
    if user.id != wildMessageObject.userID:
        return
    if not wildMessageObject.player.state == "wild":
        return
    if emoji.name == "🟥":
        await wildMessageObject.pickColor("red")
    elif emoji.name == "🟨":
        await wildMessageObject.pickColor("yellow")
    elif emoji.name == "🟩":
        await wildMessageObject.pickColor("green")
    elif emoji.name == "🟦":
        await wildMessageObject.pickColor("blue")

async def stack(emoji, message, user):
    stackMessageObject = reactionMessageIDs[message.id]
    if user.id != stackMessageObject.userID:
        return
    if not stackMessageObject.player.state == "stack":
        return
    if emoji.name == "◀️":
        await stackMessageObject.updateMessage(-1)
    elif emoji.name == "⏺️":
        await stackMessageObject.playStackCard()
    elif emoji.name == "▶️":
        await stackMessageObject.updateMessage(1)
    elif str(emoji) == "<:back:736433825097318541>":
        await stackMessageObject.endStack()

async def draw(emoji, message, user):
    drawMessageObject = reactionMessageIDs[message.id]
    if user.id != drawMessageObject.userID:
        return
    if not drawMessageObject.player.drewCard:
        return
    if emoji.name == "✅":
        await drawMessageObject.accept()
    elif emoji.name == "❎":
        await drawMessageObject.dismiss()