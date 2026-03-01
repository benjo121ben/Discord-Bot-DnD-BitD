## Bot in the Dark

> NOTE: Renamed from “Blades in the Bot” to “Bot in the Dark”

Discord bot for tracking stats in Blades in the Dark and commands for the game.

This bot is a fork of Benji’s RPG Campaign Utility Discord Bot and rewritten entirely by me.

## Features
- **Tracking player and crew stats**
- **Dice rolling**: offers standard dice as well as custom ones. If you are familiar with Inconnu or Masquerade, you’ll fit right in!
- **Generating progress clocks**: Procedurally generated progress clocks to ensure any values are accounted for.
- **Providing Devil’s Bargain cards and rolling Entanglements**: Now fully customizable via dashboard!
- **Wiki**: a mini wiki accessible via commands

## Player and Crew Stats
Bot in the Dark is designed for tracking multiple player characters and their character sheet stats and crew stats for quick lookups.

Bot in the Dark should be able to keep tabs of players in a persistent manner.

Users can claim the playable character of their choosing one at a time and have it binded to their User ID provided that character is unowned.

## Dice
Bot in the Dark has built-in d20, d12, d8, d6, and d4. The graphics and results are procedurally generated.

The underlying code was actually inspired by `/bladesroll` command by Benji—which should factor in the special dice system used by Blades in the Dark.

The Blades in the Dark dice system can recognize success, partials, fails, crits, and handling rolls when the player has zero attributes in the specific action.

## Devil’s Bargain and Entanglements
Using a command, the bot sends a random Devil’s Bargain Card, allowing the GM to have some inspirations and ideas.

## Progress Clocks
Bot in the Dark allows for the creation of clocks, as well as tick them, and output them.

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

## Disclaimers and Credits

**Disclaimer:** I am not associated with Evil Hat or John Harper in any way, I only love John Harper's games. I own no copyright for any of the images used for playbooks.

### Assets Used
- **Devil's Bargain Card Deck**: Created by reddit user *[u/Consistent-Tie-4394][db_user]*. The user was asked for their consent and agreed to the use of their asset. You can look at their reddit post on the [BitD reddit][db_reddit] or directly download the deck from their [google drive][db_drive].
- **Expanded Entanglements Table**: Created by the reddit user *[u/Lupo_1982][exp_ent_user]*. The user was asked for their consent and agreed to the use of their asset. Check out their reddit post on the [BitD reddit][exp_ent_reddit] or directly download the table from their [google drive][exp_ent_drive].
- **Playbook Images**: Official material from Evil Hat and John Harper.

<!-- links -->
[exp_ent_user]: https://www.reddit.com/user/Lupo_1982/
[exp_ent_reddit]: https://www.reddit.com/r/bladesinthedark/comments/mrzj9x/just_created_an_expanded_entanglements_table/
[exp_ent_drive]: https://drive.google.com/file/d/1mUHHYdV0VU8Ey69oUzMxeLc1lMavFohC/view?usp=sharing
[db_user]: https://www.reddit.com/user/Consistent-Tie-4394/
[db_reddit]: https://www.reddit.com/r/bladesinthedark/comments/qh43y6/devils_bargains_card_deck/
[db_drive]: https://drive.google.com/drive/folders/14vCEjWrja7fE4dtpP89vS6RZpcdGjmpH?usp=sharing
