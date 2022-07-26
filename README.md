# Benji's RPG/BitD utility Discord BOT
A discord bot for tracking stats in a game of "Dungeons and Dragons" as well as helping to GM a game of "Blades in the Dark", an RPG designed by John Harper

## Table of Contents
* [Goal](#goal)
  * [Campaign Stats](#campaign-stats)
  * [Devils Bargains and Entanglements](#devils-bargains-and-entanglements) 
* [Technologies](#technologies)
* [Using the Bot](#using-the-bot)
  * [Bot Key and Command Character](#bot-key-and-command-character)
  * [Permissions](#permissions)
  * [Local Campaign Tracking](#local-campaign-tracking)
* [Commands](#commands)
  * [Bot Commands](#bot-commands)
  * [Local Commands](#local-commands)

## Goal
The bot was generally designed for two purposes:
* [Campaign Stats](#campaign-stats)
* [Devils Bargains and Entanglements](#devils-bargains-and-entanglements) 

### Campaign Stats
The bot is designed to track multiple Player characters and their stats in multiple games of DnD at the same time. Stats referring not to the stats on a character sheet, but overarching campaign stats, such as "Enemies killed, damage done, damage taken". The bot should keep track of these stats. <strong>This feature is not yet fully implemented</strong>. It only works locally by running localRun.py

### Devils Bargains and Entanglements
On request, the bot sends a random Devil's Bargain Card, containing two devils bargains to get the GM thinking. These are for when you don't have an Idea or you just like the input.
It can also show you the appropriate entanglements, depending on the amount of heat you have and what you rolled.

## Technologies
Project is created with:
Python: 3.10
discord.py 1.7.3
with python-dotenv 0.20

The amazing Devil's Bargains - Card Deck was posted for free by the awesome reddit user u/Consistent-Tie-4394.
You can look at his reddit post on the BitD reddit:
https://www.reddit.com/r/bladesinthedark/comments/qh43y6/devils_bargains_card_deck/

Or directly download it from his google drive:
https://drive.google.com/drive/folders/14vCEjWrja7fE4dtpP89vS6RZpcdGjmpH?usp=sharing


The expanded Entanglements Table was created by the reddit user u/Lupo_1982.
You can look at his reddit post on the BitD reddit:
https://www.reddit.com/r/bladesinthedark/comments/mrzj9x/just_created_an_expanded_entanglements_table/

Or directly download it from his google drive:
https://drive.google.com/file/d/1mUHHYdV0VU8Ey69oUzMxeLc1lMavFohC/view?usp=sharing


## Using the Bot

### Bot Key and Command Character
All discord bots require a unique BOT-Token, which you get when you create a Discord bot on the Discord Developer Website.
Open the .env_example file inside the Bot's root folder. It will look something like this:

<em>DISCORD_TOKEN=""</em>
<em>COMMAND_CHAR=""</em>

In order to get the bot running, you will have to paste that TOKEN in between the "" and rename the '.env_example' file into '.env'.
You can also set the command character to be the desired character you wish to use for this bot's commands. All messages starting with that character will be interpreted as commands

f.e. if you set COMMAND_CHAR = "$"
to use the 'db' command, you will have to write '$db' into the chat.


### Permissions
To work properly the bot just needs to be able to have access to a chat on a server where it can send pictures, embeds and messages 

### Local Campaign Tracking
The campaign tracking has not yet been integrated with the bot itself and doesn't yet include all stats I would like, but can already be used via command line if you wish to try it out for yourself.
Just run localRun.py and insert a name for your savefile. If that name already exists, it loads in the existing save file for you to continue.

## Commands
These are all commands implemented so far.
parameters with a '*' are optional

all command parameters are separated by a space (" ") on input. f.e:
<em>'ent 2 7'</em>
to get an entanglement, having rolled a two, and with seven heat on the crew.

### Bot Commands
<ul>
  <li><strong>db</strong> : [*nr] The bot will send a devils bargain card. nr specifies the amount of cards, up to a maximum of 10. Defaults to one card.  </li>
  <li><strong>ent</strong> : [number_rolled, crew_heat] The bot sends the entanglements related to the specified number rolled in the entanglement roll and the heat of the crew.</li>
</ul>


### Local Commands
<ul>
  <li><strong>addC</strong> : [player_name, char_name, max_health] The bot adds a new PC to the current savefile.</li>
  <li><strong>log</strong> : shows a log of current characters in the savefile.</li>
  <li><strong>cause</strong> : [char_name, damage] Adds the amount of damage to the "damage caused" stat.</li>
  <li><strong>take</strong> : [char_name, damage] Adds the amount of damage to the "damage taken" stat and reduces a characters health.</li>
  <li><strong>heal</strong> : [char_name, amount] Adds the amount to the "damage healed" stat and heals a characters health up to their max health.</li>
  <li><strong>healm</strong> : [char_name] fully heals a character, increasing their health to the max and increasing their "damage healed" stat by the difference. This is used for long rests in DnD</li>
  <li><strong>inc</strong> : [char_name, amount] Adds the amount to a characters maximum health and health. permanently increasing their maximum health.</li>
</ul>
