from discord import Embed

from .EntryLabels import PLAYBOOK_ITEMS_LABEL, PLAYBOOK_FRIENDS_LABEL
from .WikiEntry import WikiEntry


class PlaybookEntry(WikiEntry):
    def __init__(self, info=None):
        super().__init__(info)
        self.items = info[PLAYBOOK_ITEMS_LABEL]
        self.friends = info[PLAYBOOK_FRIENDS_LABEL]

    async def send_info(self, ctx):
        embed = Embed(title=f'{self.name}', description=self.description)
        embed.add_field(name="*Special Items*", value=''.join([f'> {value}\n'.replace("Fine", "**Fine**") for value in self.items]), inline=True)
        embed.add_field(name="*Friends and Rivals*", value=''.join([f'> **{value.split(",")[0]}**, {value.split(",")[1]}\n' for value in self.friends]), inline=True)
        await ctx.respond(embed=embed)
