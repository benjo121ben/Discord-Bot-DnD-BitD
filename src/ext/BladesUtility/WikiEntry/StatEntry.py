from discord import Embed

from .EntryLabels import EXAMPLE_LABEL
from .WikiEntry import WikiEntry


class StatEntry(WikiEntry):

    def __init__(self, info):
        super().__init__(info)
        self.example = info[EXAMPLE_LABEL] if EXAMPLE_LABEL in info else ""

    async def send_info(self, ctx):
        embed = Embed(title=f'**{self.name}**', description=self.description)
        if self.example != "":
            embed.add_field(name="**Example**", value=f'_{self.example}_', inline=True)

        await ctx.respond(embed=embed)
