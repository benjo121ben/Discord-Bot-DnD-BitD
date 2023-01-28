import json
import logging
import os
import pathlib

from discord import Embed

relative_wiki_path = os.sep.join(["Assets", "item_wiki.json"])
wiki = {}


class WikiEntry:
    def __init__(self, name, info):
        self.name = name
        self.info = info

    async def sendInfo(self, ctx):
        ctx.respond(str(self))


class ItemEntry(WikiEntry):
    async def sendInfo(self, ctx):
        embed = Embed(title=self.name, description=f'**load {self.info["load"]}**\n' + self.info["description"])
        if "extra_info" in self.info:
            embed.add_field(name="*Tip*", value=self.info["extra_info"], inline=True)
        await ctx.respond(embed=embed)


def setup_wiki():
    wiki_path = os.sep.join([str(pathlib.Path(__file__).parent.resolve()), relative_wiki_path])

    with open(wiki_path)as file:
        imported_wiki = json.load(file)
        for name, info in imported_wiki.items():
            if info["type"] == "Item":
                wiki[name] = ItemEntry(name, info)


async def wiki_search(ctx, name):
    if name in wiki:
        await wiki[name].sendInfo(ctx)
    else:
        await ctx.respond("item could not be found")

