from storage.globalVariables import reactionMessageIDs

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
        client.loop.create_task(handMessageObject.updateMessage(-2, client))
    elif emoji.name == "◀️":
        client.loop.create_task(handMessageObject.updateMessage(-1, client))
    elif emoji.name == "⏺️":
        await handMessageObject.playCardButtonPressed(client)
    elif emoji.name == "▶️":
        client.loop.create_task(handMessageObject.updateMessage(1, client))
    elif emoji.name == "⏩":
        client.loop.create_task(handMessageObject.updateMessage(2, client))
    elif str(emoji) == "<:back:736433825097318541>":
        await handMessageObject.drawCard(client)

async def wild(emoji, message, user, client):
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

async def stack(emoji, message, user, client):
    stackMessageObject = reactionMessageIDs[message.id]
    if user.id != stackMessageObject.userID:
        return
    if not stackMessageObject.player.state == "stack":
        return
    if emoji.name == "◀️":
        await stackMessageObject.updateMessage(-1, client)
    elif emoji.name == "⏺️":
        await stackMessageObject.playStackCard(client)
    elif emoji.name == "▶️":
        await stackMessageObject.updateMessage(1, client)
    elif str(emoji) == "<:back:736433825097318541>":
        await stackMessageObject.endStack(client)

async def draw(emoji, message, user, client):
    drawMessageObject = reactionMessageIDs[message.id]
    if user.id != drawMessageObject.userID:
        return
    if not drawMessageObject.player.drewCard:
        return
    if emoji.name == "✅":
        await drawMessageObject.accept(client)
    elif emoji.name == "❎":
        await drawMessageObject.dismiss(client)