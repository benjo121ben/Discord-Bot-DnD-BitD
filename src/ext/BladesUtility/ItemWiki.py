import json
import logging
import os
import pathlib
from typing import TypeVar, Generic

from discord import Embed

relative_wiki_path = os.sep.join(["Assets", "item_wiki.json"])
wiki = {}

# property labels
NAME_LABEL = 'name'
DESCRIPTION_LABEL = 'description'
EXAMPLE_LABEL = 'example'
LOAD_LABEL = 'load'
PLAYBOOK_LABEL = 'playbook'
EXTRA_HEADER_LABEL = 'extra_header'
EXTRA_LABEL = 'extra'
LIST_LABEL = 'list'

# properties unique to created items
CREATION_TYPE_LABEL = 'type'
CREATION_DRAWBACK_LABEL = 'drawback'
CREATION_USES_LABEL = 'uses'
CREATION_TIER_LABEL = 'tier'

# wiki entry category labels
CAT_ITEMS_LABEL = 'items'
CAT_CLASS_ITEMS_LABEL = 'class_items'
CAT_CREATIONS_LABEL = 'sample-creations'
CAT_PLAYBOOKS_LABEL = 'playbooks'
CAT_STATS_LABEL = 'stats'




class WikiEntry:
    def __init__(self, info=None):
        self.name = ""
        self.description = ""
        if info is not None:
            self.name = info[NAME_LABEL]
            if DESCRIPTION_LABEL not in info:
                return
            self.description = info[DESCRIPTION_LABEL]

    async def send_info(self, ctx):
        embed = Embed(title=f'{self.name}', description=self.description)
        await ctx.respond(embed=embed)


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


class StatEntry(WikiEntry):

    def __init__(self, info):
        super().__init__(info)
        self.example = info[EXAMPLE_LABEL] if EXAMPLE_LABEL in info else ""

    async def send_info(self, ctx):
        embed = Embed(title=f'**{self.name}**', description=self.description)
        if self.example != "":
            embed.add_field(name="**Example**", value=f'_{self.example}_', inline=True)

        await ctx.respond(embed=embed)


def levenshtein_distance(word1, word2):
    # Declaring array 'D' with rows = len(a) + 1 and columns = len(b) + 1:
    D = [[0 for i in range(len(word2) + 1)] for j in range(len(word1) + 1)]

    # Initialising first row and first column:
    for row in range(len(word1) + 1):
        D[row][0] = row
    for col in range(len(word2) + 1):
        D[0][col] = col

    # check for each spot if substitution, insertion or
    for row in range(1, len(word1) + 1):
        for col in range(1, len(word2) + 1):
            if word1[row - 1] == word2[col - 1]:
                D[row][col] = D[row - 1][col - 1]
            else:
                # Adding 1 to account for the cost of operation
                insertion = 1 + D[row][col - 1]
                deletion = 1 + D[row - 1][col]
                replacement = 1 + D[row - 1][col - 1]

                # Choosing the best option:
                D[row][col] = min(insertion, deletion, replacement)

    return D[len(word1)][len(word2)]


def setup_wiki():
    wiki_path = os.sep.join([str(pathlib.Path(__file__).parent.resolve()), relative_wiki_path])

    with open(wiki_path)as file:
        imported_wiki = json.load(file)

        for name, entry in imported_wiki.items():
            if name == CAT_ITEMS_LABEL:
                insert_wiki_entry(entry, ItemEntry)
            elif name == CAT_CLASS_ITEMS_LABEL:
                insert_wiki_entry(entry, ClassItemEntry)
            elif name == CAT_PLAYBOOKS_LABEL:
                insert_wiki_entry(entry, WikiEntry)
            elif name == CAT_STATS_LABEL:
                composite_wiki_entry = insert_wiki_entry(entry, CompositeEntry)
                for child in composite_wiki_entry.children:
                    insert_wiki_entry(child, StatEntry)
            elif name == CAT_CREATIONS_LABEL:
                for item_cat in entry:
                    item_type = item_cat[CREATION_TYPE_LABEL]
                    item_drawback = item_cat[CREATION_DRAWBACK_LABEL] if CREATION_DRAWBACK_LABEL in entry else ""
                    for item in item_cat[LIST_LABEL]:
                        item[CREATION_TYPE_LABEL] = item_type
                        item[CREATION_DRAWBACK_LABEL] = item_drawback
                        insert_wiki_entry(item, CraftedItemEntry)


def insert_wiki_entry(checked_object, wiki_entry_class_type):
    """
        parses the values inside a list or object type from a json wiki and puts it into the wiki dictionary.

        :param checked_object: The object or list entry
        :param wiki_entry_class_type: the class that should be used to package the object

        :returns: None if the checked object was a list otherwise it will return the created WikiEntry
    """
    obj = None
    if type(checked_object) is list:
        for list_entry in checked_object:
            key = list_entry[NAME_LABEL].lower()
            wiki[key] = wiki_entry_class_type(list_entry)
    else:
        key = checked_object[NAME_LABEL].lower()
        obj = wiki_entry_class_type(checked_object)
        wiki[key] = obj
    return obj


async def wiki_search(ctx, search_term: str):
    found = []
    term = search_term.lower()
    if term in wiki:
        await wiki[term].send_info(ctx)
    else:
        for key in wiki.keys():
            if term in key and len(term) >= 4:
                found.append({"key": key, "distance": -1})
                continue
            distance = levenshtein_distance(term, key)
            if distance < 5:
                found.append({"key": key, "distance": distance})
        found = sorted(found, key=lambda val1: val1["distance"])
        found = found[:min(5, len(found))]

        if len(found) == 1:
            await wiki[found[0]["key"]].send_info(ctx)
        elif len(found) > 1:
            await ctx.respond("Entry could not be found. Did you mean any of these?\n" +
                              ", ".join(
                                  ["**"+item["key"]+"**" for item in found]
                              ))
        else:
            await ctx.respond("Entry could not be found.")
