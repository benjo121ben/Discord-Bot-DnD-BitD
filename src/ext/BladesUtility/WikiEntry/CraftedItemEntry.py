from discord import Embed

from .EntryLabels import CREATION_TYPE_LABEL, CREATION_DRAWBACK_LABEL, \
    CREATION_USES_LABEL, CREATION_TIER_LABEL
from .WikiEntry import WikiEntry


class CraftedItemEntry(WikiEntry):

    def __init__(self, info):
        super().__init__(info)
        self.type = info[CREATION_TYPE_LABEL]
        self.drawback = info[CREATION_DRAWBACK_LABEL]
        self.uses = info[CREATION_USES_LABEL]
        self.tier = info[CREATION_TIER_LABEL]

    async def send_info(self, ctx):
        embed = Embed(title=f'**{self.name}**', description=self.description)
        embed.add_field(name="Type", value=f'_{self.type}_', inline=True)
        embed.add_field(name="Uses / Ammo", value=f'{self.uses}', inline=True)
        embed.add_field(name="Tier", value=f'{self.tier}', inline=True)
        if self.drawback != "":
            embed.add_field(name="Drawback", value=self.drawback, inline=False)
        await ctx.respond(embed=embed)
