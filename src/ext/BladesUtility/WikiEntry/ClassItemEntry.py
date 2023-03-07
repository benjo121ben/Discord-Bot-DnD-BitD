from discord import Embed

from .EntryLabels import LOAD_LABEL, PLAYBOOK_LABEL, EXTRA_LABEL
from .WikiEntry import WikiEntry


class ClassItemEntry(WikiEntry):

    def __init__(self, info):
        super().__init__(info)
        self.load = info[LOAD_LABEL]
        self.playbook = info[PLAYBOOK_LABEL]
        self.extra = info[EXTRA_LABEL] if EXTRA_LABEL in info else ""

    async def send_info(self, ctx):
        embed = Embed(title=f'**{self.name}**\nPlaybook: _{self.playbook}_\nItem  Load: _{self.load}_', description=self.description)
        if len(self.extra) > 0:
            embed.add_field(name="Also", value=f'_{self.extra}_', inline=True)
        await ctx.respond(embed=embed)
