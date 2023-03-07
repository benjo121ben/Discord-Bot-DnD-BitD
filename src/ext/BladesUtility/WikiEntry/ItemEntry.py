from discord import Embed

from .EntryLabels import LOAD_LABEL, EXTRA_HEADER_LABEL, EXTRA_LABEL
from .WikiEntry import WikiEntry


class ItemEntry(WikiEntry):

    def __init__(self, info):
        super().__init__(info)
        self.load = info[LOAD_LABEL]
        self.extra_header = info[EXTRA_HEADER_LABEL] if EXTRA_HEADER_LABEL in info else ""
        self.extra_info = info[EXTRA_LABEL] if EXTRA_LABEL in info else ""

    async def send_info(self, ctx):
        embed = Embed(title=f'**{self.name}**\nPlaybook: _All playbooks_\nItem  Load _{self.load}_', description=self.description)
        if len(self.extra_header) > 0:
            embed.add_field(name="*"+self.extra_header+"*", value=f'_{self.extra_info}_', inline=True)
        await ctx.respond(embed=embed)
