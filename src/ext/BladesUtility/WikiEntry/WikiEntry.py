from discord import Embed

from .EntryLabels import NAME_LABEL, DESCRIPTION_LABEL


class WikiEntry:
    def __init__(self, info=None):
        self.name: str = ""
        self.description: str = ""
        if info is not None:
            self.name: str = info[NAME_LABEL]
            if DESCRIPTION_LABEL not in info:
                return
            self.description = info[DESCRIPTION_LABEL]

    async def send_info(self, ctx):
        embed = Embed(title=f'{self.name}', description=self.description)
        await ctx.respond(embed=embed)
