## Bot in the Dark

> NOTE: Renamed from “Blades in the Bot” to “Bot in the Dark”

Discord bot for tracking stats in Blades in the Dark and commands for the game.

This bot is a fork of Benji’s RPG Campaign Utility DIscord Bot and rewritten entirely by me.

## Features
- **Tracking player and crew stats**
- **Dice rolling**: offers standard dices as well as custom ones. If you are familiar with Inconnu or Masquerade, you’ll fit right in!
- **Generating progress clocks**: Procedurally generated progress clocks to ensure any values are accounted for.
- **Providing Devil’s Bargain cards and rolling Entanglements**: Now fully customizable via dashboard!
- **Wiki**: a mini wiki accessible via commands

## Player and Crew Stats
Bots in the Dark is designed for tracking multiple player characters and their character sheet stats and crew stats for quick lookups.

Bots in the Dark should be able to keep tabs of players in a persistent manner.

Users can claim

## Dice
Bots in the Dark has built-in d20, d12, d8, d6, and d4. The graphics and results are procedurally generated.

The underlying code was actually inspired by `/bladesroll` command by Benji—which should factpr in the special dice system used by Blades in the Dark.

The Blades in the Dark dice system can recognize succes, partials, fails, crits, and handling rolls when the player has zero attributes in the specific action.
## Devil’s Bargain and Entanglements
Using a command, the bot sends a random Devil’s Bargain Card, allowing the GM to have some inspirations and ideas.

## Progress Clocks
Bots in the Dark allows for the creation of creating clocks, as well as tick them, and output them.

The clocks themselves are procedurally generated and can dynamically adjust with code.

## Wiki
The bot has a selection of entries for all Blades in the Dark specific items and stats that users can look up. Use `/wiki` to see a general list of entries. Use arguments to refine the selection further.

The entries are fully customizable. These entries are for:
- Standard Items
- Playbook Items
- Created Items/Leech Alchemicals
- Playbook Overviews
- Actions
- Custom Entries (NPC Cards)
Entries can be added either via commands and dashboard (simple items) or injected as files (NPC cards from markdown)
