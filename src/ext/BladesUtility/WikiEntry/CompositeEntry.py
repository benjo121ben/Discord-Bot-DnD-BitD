from discord import Embed

from .EntryLabels import NAME_LABEL, DESCRIPTION_LABEL, EXTRA_HEADER_LABEL, EXTRA_LABEL, \
    LIST_LABEL
from .WikiEntry import WikiEntry


class CompositeEntry(WikiEntry):
    def __init__(self, info):
        super().__init__(info)
        self.extra_header = info[EXTRA_HEADER_LABEL] if EXTRA_HEADER_LABEL in info else ""
        self.extra = info[EXTRA_LABEL] if EXTRA_LABEL in info else ""
        self.children = []
        for listentry in info[LIST_LABEL]:
            self.children.append(listentry)

    async def send_info(self, ctx):
        embed = Embed(title=f'**{self.name}**', description=self.description)
        if not self.extra == "":
            embed.add_field(name=f'**{self.extra_header}**', value=self.extra, inline=False)
        for child in self.children:
            embed.add_field(name=f'**{child[NAME_LABEL]}**', value=child[DESCRIPTION_LABEL])
        await ctx.respond(embed=embed)
