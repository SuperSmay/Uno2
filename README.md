# Uno2
![alt text](https://cdn.discordapp.com/attachments/742986384113008712/830589793037451294/UNO_Logo.png "Uno!")
## Uno2 is an in development Discord bot that hosts games of Uno. (It will be offline almost all of the time until it's done)
---
#### Disclaimer: 
  This bot is not complete and has no guarantee of functionality or support. Until the bot is complete it will ask for admin permissions when you add it to your server, this is because I was too lazy to figure out what permissions are needed exactly. Feel free to clone this code and work on it or host it yourself, but you will not get any support from me other than the hosting section of this readme file.
### Current features:
  * Creating and starting games
  * Fancy hand messages
  * Playing cards
  * Skip and reverse cards
  * Drawing cards
  * Stacks

### In progress features:
  * Jump ins
  * A better hand system
---
## How to use
1. First, [invite](https://discord.com/api/oauth2/authorize?client_id=736418090627235951&permissions=8&scope=bot%20applications.commands) the bot to your server.
2. To join a lobby, go the chat you want the game to be hosted in and type `/join`.
3. Once every player who wants to play is in the lobby, type `/start` to start the game.
4. The bot should begin DMing every player with a few game messages. This will take several seconds. The bot will tell you when the game has started.
5. When it is your turn to play, select a card from your hand and use the dot ⏺ to play it. If you cannot play a card, draw cards with the Uno card.
6. The first player to run out of cards wins the game!

### Controls
Use the arrows ◀ ▶ to cycle one card at a time through your hand, and use the double arrows ⏪ ⏩ to cycle two cards at a time through your hand. Use the dot ⏺ to play a card and the Uno card to draw cards. 

### Hosting
To host this bot yourself you need a recent version of Python 3 installed, as well as recent versions of the dependencies linked below (and maybe some others I'm too lazy to check just read the error message if one of them is missing). Additionally, you will need a [Discord bot account](https://discordpy.readthedocs.io/en/stable/discord.html#discord-intro). Place the token copied in step 7 in an empty file called `TOKEN.token` inside the storage folder. **When you create the link to add the bot account to your server, make sure to check `applications.commands` in the scopes section.** ![Image](https://discord-py-slash-command.readthedocs.io/en/latest/_images/scope.jpg) Assuming you did all that right and I wrote this guide right, simply run `bot.py`. **You will likely need to wait around an hour for the slash commands to register on Discord.** The bot will not be usuable until this happens. This is a Discord limitation for global slash commands. If you really want to get around this, you can create a list of the guild IDs that you want the bot to work in and add a `guild_ids = {list of guild_ids}` field to the declaration for *each* slash command you want, right after the name. Ex:
```py
guild_ids = [123456789, 987654321, 111111111]
@slash.slash(name="foo", guild_ids = guild_ids
    description="A development command."
)
```

###### Uno2 is written in Python and uses [discord.py](https://discordpy.readthedocs.io/en/stable/) and [discord-py-slash-command](https://pypi.org/project/discord-py-slash-command/) to interact with Discord. Created by [Smay#0001](https://discordapp.com/users/243759220057571328)
