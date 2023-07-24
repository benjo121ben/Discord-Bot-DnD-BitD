# Benji's RPG campaign utility Discord BOT
A discord bot for tracking campaign stats in a game of "Dungeons and Dragons" 
as well as helping to run a game of "Blades in the Dark"

---


## Table of Contents
* [Disclaimer](#disclaimer)
* [What is this Bot](#what-is-this-bot)
  * [Campaign Stats](#campaign-stats)
  * [Devils Bargains](#devils-bargains)
  * [Entanglements](#entanglements) 
  * [Progress Clocks](#progress-clocks) 
  * [Dice](#dice) 
  * [Wiki](#wiki) 


* [Technologies and Assets](#technologies-and-assets)
  * [Devils bargain card deck](#devils-bargain-card-deck)
  * [Expanded Entanglements Table](#expanded-entanglements-table)
  * [Clock images](#clock-images)
  * [Playbook images](#playbook-images)


* [How it works](#how-it-works)
  * [Setup](#setup)
    * [.ENV](#.ENV)
    * [Permissions](#permissions)
  * [Offline Mode](#offline-mode)
  

* [Commands](#commands)
  * [Common Commands](#common-commands)
  * [Blades in the Dark Commands](#blades-in-the-dark-commands)
    * [Utility Commands](#utility-commands)
    * [Progress Clock Commands](#progress-clock-commands)
  * [Campaign tracking commands](#campaign-tracking-commands)
    * [Management Commands](#management-commands)
    * [Stat Commands](#stat-commands)

---

# Disclaimer
<h3>I am not associated with Evil Hat or John Harper in any way, I only love John Harpers games. 
I own no copyright for any of the images used for playbooks</h3>

# What is this bot
The bot was generally designed as a tool to help me with Game mastering tabletop roleplaying games, specifically Dungeons and Dragons
and Blades in the Dark.  
It now has 5 main functions:  

**For all systems that are more stat based (DnD, Pathfinder)**
* Tracking [Campaign Stats](#campaign-stats) for one or multiple campaigns at the same time. 
* Rolling [dice](#dice) for any game system

**For Blades in the Dark**
* Providing [Devils bargain cards](#devils-bargains) and rolling [Entanglements](#entanglements)
* Generating [progress clocks](#progress-clocks) in a Discord chat saving them permanently. 
* Rolling [dice](#dice) in a Discord chat for games of Blades in the Dark or other game systems
* [Wiki](#wiki): the bot has a small wiki function, allowing users to look up item and class information for Blades in the Dark characters


### Campaign Stats
The bot is designed to track multiple Player characters and their stats in multiple games of DnD/pathfinder/similar
at the same time. By stats I am not referring to the stats on a character sheet such as ability scores or skill scores, 
but overarching campaign stats, such as:  

* enemies killed
* damage done
* damage taken

The bot keeps track of these stats over multiple sessions and stores them permanently.
Users cannot access other users' content, unless specifically authorized.

### Devils Bargains
On request, the bot sends a random Devil's Bargain Card, containing two devils bargains to get the GM thinking. 
These are for when you don't have an Idea or you just like the input.  

### Entanglements 
By inputting the number rolled in the entanglements roll and the heat on the crew, 
the bot sends you the appropriate entanglements from the [expanded entanglements table](#expanded-entanglements-table).

### Progress Clocks
After a request from someone on the BitD discord, I included the option to create clocks, tick them and output them.  
Though it is possible to create clocks of greater sizes and tick them, at the moment it is only possible to
output images of clocks of size 3, 4, 6, 8 and 10 since the images are not created dynamically. 
All other clocks are only output via text.

### Dice
The bot is capable of rolling any dice and has visuals for d20, d12, d8, d6 and d4. (Only test assets so far). 
This function is currently part of the Blades in the Dark functions, but will be moved soon.  
For games of Blades in the Dark, the bot also has the separate `/bladesroll` command, which understands the special dice system used
by the game.

### Wiki
The bot has a small selection of entries for all blades specific items and stats. Users can look up information
by using the `/wiki` command. The bot uses levenstein distance to determine entries close to the search term.  
There are entries for
* Standard Items
* Playbook Items
* Created Items/Leech Alchemicals
* Playbook overviews
* Actions

---

## Technologies and Assets
<strong>Project is created with Python: 3.10.  
For packages see [requirements.txt](requirements.txt)</strong>  
All of the functionality works via discords slash command system.


### Devils bargain card deck
The amazing *Devil's Bargain-Card Deck* was created by reddit user *[u/Consistent-Tie-4394][db_user]*.  
The user was asked for their consent and agreed to the use of their asset.  
You can look at their reddit post on the [BitD reddit][db_reddit]
or directly download the deck from his [google drive][db_drive].

### Expanded Entanglements Table
The, just as great, *expanded Entanglements Table* was created by the reddit user *[u/Lupo_1982][exp_ent_user]*.  
The user was asked for their consent and agreed to the use of their asset.  
Check out their reddit post on the [BitD reddit][exp_ent_reddit]
or directly download the table from his [google drive][exp_ent_drive].

### Clock images
The clock images were created by my friend and are open for use by others.

### Playbook Images
The images for playbooks are official material from Evil Hat and John Harper

---

## How it works 
The bot **auto saves** all changes inside dedicated save files inside the *./saves* folder, so it is not required for you to run
any sort of save command. The saves folder and according file is created when you add your first character.
Save files are saved in the standardized json format, which makes the data easily transferable.


### Setup 
1. All discord bots require a unique BOT-Token, which you get when you create a Discord bot on the [Discord Developer Website][discord_dev].
2. Once you are logged in, create a `new Application`
3. Within the application, enter the `Bot` tab and choose `Add Bot`
4. Still in the `Bot` tab under the bot's username is your bot's token. Copy that token and store it safely. 
Keep this token secret, do not publish this token anywhere. It can be misused by malicious third parties.  
5. Install python and the necessary packages outlined in requirements.txt
6. Continue the .ENV process outlined below

##### .ENV

After you have set up your discord bot and have your token, open the `.env_example` file inside the Bots root folder.
(if you cannot see the file, enable file attachments in your explorer).  
It will look something like this:

```
DISCORD_TOKEN=""
COMMAND_CHAR="!"
CLOUD_SAVE_CHANNEL=
ADMIN_ID=
DND=1
BLADES=1
```

In order to get the bot running, follow these steps:  
1. rename the `.env_example` file to `.env` and open the `.env` file.  
2. Paste the token you got from the Discord bots developer page in between the 
" " of the *DISCORD_TOKEN* variable 
3. Set your own [discord id][discord_id] as the ADMIN_ID in order to ensure certain commands are locked for 
your own use alone.  
4. If you wish to be able to save your save files into a predetermined discord channel via the `/cache` command, 
you can copy the channels discord id into the `CLOUD_SAVE_CHANNEL` variable. 
Just make sure the bot has access to the channel and authorization to post there.  
5. Set DND to 1 if you wish to enable campaign tracking specific commands, otherwise set 0.
6. Set Blades to 1 if you wish to enable Blades in the Dark specific commands, otherwise set 0.

At the end of this process your .env file should look something like this (values are just examples):
```
DISCORD_TOKEN="youR241DiscordBotTokenPastedHERE"
COMMAND_CHAR="!"
CLOUD_SAVE_CHANNEL=1save24ChannelID
ADMIN_ID=231OfAdmin23UserID
DND=0
BLADES=1
```


These are the variables that can be assigned in the .env file.

| Variable           | Required | Use                                                                         |
|--------------------|----------|-----------------------------------------------------------------------------|
 | DISCORD_TOKEN      | YES      | bot token assigned by the discord developer page                            |
 | ADMIN_ID           | YES      | user id of user assigned as administrator                                   |
 | COMMAND_CHAR       | YES      | prefix used for admin commands                                              |
 | CLOUD_SAVE_CHANNEL | NO       | channel id, in which the bot sends save files if the /cache command is used |
| DND                | YES      | Enables/Disables Campaign tracking commands                                 |
| BLADES             | YES      | Enables/Disables Blades in the Dark specific commands                       |


#### Permissions
To work properly, the bot requires these permissions, some of them are not yet used, but may be used in future versions. 
1. Once you are done with the setup above, enter into the OAuth tab on the Discord Developer page and select the URL generator.
2. Here you will need to select the permissions ticked in the image below and copy the URL at the bottom
![test](Assets/readme_images/OAuthGenerator.png)
3. Save this url somewhere. People will be able to invite your discord bot into their server, by using this url.
4. Enter the url into your browser and invite the bot to your discord server. 
5. Run `main.py`


### Offline Mode
Local Run is not working at the moment and is disabled for now.

---

## Commands
These are all the commands implemented so far, ordered by the Cogs they are assigned to.  

* parameters with a star (*) are optional parameters, default values are written in the use section  

### Common Commands
Commands that are always enabled

| command name | parameters | Use                                                                      |
|:------------:|:----------:|:-------------------------------------------------------------------------|
 |     ping     |     /      | The bot will answer the ping. This is to check whether the bot is online |

### Blades in the Dark Commands
Commands that are enabled with setting `BLADES=1`
#### Utility commands
|    command name     |        parameters        | Use                                                                                                                                         |
|:-------------------:|:------------------------:|:--------------------------------------------------------------------------------------------------------------------------------------------|
 |   devils_bargain    |           *nr            | The bot will send a devils bargain card.<br> nr specifies the amount of cards, up to a maximum of 10. <br>**Defaults to one card.**         |
 |    entanglement     | number_rolled, crew_heat | The bot sends the entanglements related to the specified number rolled in the entanglement roll and the heat of the crew.                   |
 | entanglement_wanted | wanted_level, crew_heat  | The bot rolls for entanglement using the given wanted level and sends the entanglements related to the heat of the crew.                    |
|        wiki         |        entry_name        | The bot looks for the wiki entry by that name, returning the one found, or the closest one to it. If multiple are found, it returns a list. |
|      bladeroll      |       dice_amount        | Makes a d6 roll using the Blades system. It recognizes success, partials, fails and crits and can handle 0 dice.                            |
|        roll         |  dice_amount, dice_size  | Makes a roll using the dice size provided. 2d8 => amount=2 sice=8                                                                           |

#### Progress Clock Commands
| command name |                 parameters                 | Use                                                                                                                                                             |
|:------------:|:------------------------------------------:|:----------------------------------------------------------------------------------------------------------------------------------------------------------------|
 |  clock_add   | clock_tag, clock_title, clock_size, *ticks | Adds a new clock with the given title, tag, size and starting ticks. The tag is used to adress the clock in all other commands. <br> **Default: 0 start ticks** |
 |  clock_rem   |                 clock_tag                  | Deletes the selected clock.                                                                                                                                     |
 |  clock_show  |                 clock_tag                  | Sends all info of a saved clock, with picture if possible.                                                                                                      |
|  clock_all   |                     /                      | Prints out all saved clocks.                                                                                                                                    |
|  clock_tick  |             clock_tag, *ticks              | Ticks the selected clock by a selected amount. <br>**Default: 1 tick, negative values possible**                                                                |

---

### Campaign Tracking Commands
Commands that are enabled with setting `DND=1`
#### Management Commands
These are commands used to load files, manage characters and their assignment to discord users.

| command name |          parameters           | Admin Only | Use                                                                                                                                                                                                                                                                                       |
|:------------:|:-----------------------------:|:----------:|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|     load     |           file_name           |     NO     | Load one of the save files.                                                                                                                                                                                                                                                               |
 |     add      | char_tag, char_name, *user_id |     NO     | Adds new character to currently selected savefile and sets their name and tag. <br>The tag is used to adress them later. <br>If user_id is provided, it tries to claim the character for the user with the provided discord user id. (See `/claim`)                                       |
 |    rename    |    char_tag, new_char_name    |     NO     | Rename a character on the current save file.                                                                                                                                                                                                                                              |
 |    retag     | old_char_name, new_char_name  |     NO     | Change the tag of a character on the current save file.                                                                                                                                                                                                                                   |
 |    claim     |      char_tag, *user_id       |  DEPENDS   | Tries to assign a character to the user with the user_id provided. If none is provided, it will try to assign it to the user executing the command.<br>**A user can only claim one character per save file. Only the file creator can assign characters that already belong to a player** |
|   unclaim    |           *user_id            |  DEPENDS   | Unclaims the character assigned to yourself, or the user_id provided. <br>**You can only unclaim other users characters, if you are the creator of the currently loaded file.**                                                                                                           |
|   session    |               /               |  DEPENDS   | Increases the session counter by 1. <br>**If you are a bot administrator, the bot also tries to execute the `/cache` command.**                                                                                                                                                           |
|   download   |               /               |     NO     | Sends a copy of the currently selected save file into the channel where the command was called.                                                                                                                                                                                           |
|     undo     |               /               |     NO     | Undo your last command. You can undo a maximum of 10 commands. If you send a new command after undoing one or more commands, the undone commands are lost and cannot be redone via the redo command.                                                                                      |
|     redo     |               /               |     NO     | Redo a command you've previously undone.                                                                                                                                                                                                                                                  |
|    cache     |               /               |    YES     | Sends a copy of the currently selected save file into the channel with the id assigned in the .env files `CLOUD_SAVE_CHANNEL` variable.<br>**Make sure the bot has the necessary access and permissions to send messages in the channel with the provided ID**                            |
|  get_cache   |               /               |    YES     | Gets the latest savefile uploaded into the channel assigned in the .env file's `CLOUD_SAVE_CHANNEL` variable and checks if it is a more current version than the one currently stored. If yes, the currently sroted file is replaced with the one downloaded from the chat.               |

#### Stat Commands

All stat commands except for log have an optional `char_tag` parameter. If a user executes a stat
command and no `char_tag` is provided, the command is applied to the executing users' claimed character.

| command name |        parameters         | Use                                                                                                                                                                                                                                                                                     |
|:------------:|:-------------------------:|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|     log      |         *advanced         | Output the stats of all characters in the currently selected save file.<br>Also outputs the commands that have been sent and can be undone/redone if the `advanced` parameter is set to 1                                                                                               |
 |     crit     |    *amount, *char_tag     | Increase the `crit` stat by the given amount for the selected character.<br>**Default: increase by one**                                                                                                                                                                                |
 |    dodged    |    *amount, *char_tag     | Increase the `dodged` stat by the given amount for the selected character.<br>**Default: increase by one**                                                                                                                                                                              |
 |    faint     |    *amount, *char_tag     | Increase the `fainted` stat by the given amount for the selected character.<br>**Default: increase by one**                                                                                                                                                                             |
 |    cause     | amount, *kills, *char_tag | Increases the `damage_caused` stat for the selected character by the provided `amount`. If kills are provided it also increases the `kills` stat by that amount. If the `amount` is greater than the characters previous `max_damage` stat, the stat will be replaced by the new amount |
|     take     |     amount, *char_tag     | Increases the `damage_taken` stat for selected character.                                                                                                                                                                                                                               |
|    taker     |     amount, *char_tag     | Works the same as take, increasing `damage_taken` stat by half of the `amount` rounded down, and the `damage_resisted` stat by the other half to account for damage resistances provided by abilities, such as the barbarian in dnd 5e                                                  |
|     heal     |     amount, *char_tag     | Increases the `damage_healed` stat by the amount.                                                                                                                                                                                                                                       |


<!-- links --> 

[exp_ent_user]: https://www.reddit.com/user/Lupo_1982/
[exp_ent_reddit]: https://www.reddit.com/r/bladesinthedark/comments/mrzj9x/just_created_an_expanded_entanglements_table/
[exp_ent_drive]: https://drive.google.com/file/d/1mUHHYdV0VU8Ey69oUzMxeLc1lMavFohC/view?usp=sharing

[db_user]: https://www.reddit.com/user/Consistent-Tie-4394/
[db_reddit]: https://www.reddit.com/r/bladesinthedark/comments/qh43y6/devils_bargains_card_deck/
[db_drive]: https://drive.google.com/drive/folders/14vCEjWrja7fE4dtpP89vS6RZpcdGjmpH?usp=sharing
[discord_dev]: https://discord.com/developers/applications
[discord_setup]: https://www.upwork.com/resources/how-to-make-discord-bot
[discord_id]: https://www.remote.tools/remote-work/how-to-find-discord-id
