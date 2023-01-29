import json
import logging
import os
import pathlib

from discord import Embed

relative_wiki_path = os.sep.join(["Assets", "item_wiki.json"])
wiki = {}


class WikiEntry:

    async def sendInfo(self, ctx):
        ctx.respond(str(self))


class ItemEntry(WikiEntry):

    def __init__(self, info):
        self.name = info["name"]
        self.load = int(info["load"])
        self.description = info["description"]
        if "extra_info" in info:
            self.extra_header = info["extra_header"]
            self.extra_info = info["extra_info"]
        else:
            self.extra_header = ""

    async def sendInfo(self, ctx):
        embed = Embed(title=f'**{self.name}**\n_load {self.load}_', description=self.description)
        if len(self.extra_header) > 0:
            embed.add_field(name="*"+self.extra_header+"*", value=self.extra_info, inline=True)
        await ctx.respond(embed=embed)


class StatEntry(WikiEntry):

    def __init__(self, info):
        self.name = info["name"]
        self.description = info["description"]
        self.example = info["example"]

    async def sendInfo(self, ctx):
        embed = Embed(title=f'{self.name}', description=self.description)
        embed.add_field(name="*Example*", value=f'*{self.example}*', inline=True)

        await ctx.respond(embed=embed)


class PlaybookEntry(WikiEntry):

    def __init__(self, info):
        self.name = info["name"]
        self.description = info["description"]

    async def sendInfo(self, ctx):
        embed = Embed(title=f'{self.name}', description=self.description)
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
        for item in imported_wiki["items"]:
            key = item["name"].lower()
            wiki[key] = ItemEntry(item)
        for playbook in imported_wiki["playbooks"]:
            key = playbook["name"].lower()
            wiki[key] = PlaybookEntry(playbook)
        for stat in imported_wiki["stats"]:
            key = stat["name"].lower()
            wiki[key] = StatEntry(stat)


async def wiki_search(ctx, search_term: str):
    found = []
    term = search_term.lower()
    if term in wiki:
        await wiki[term].sendInfo(ctx)
    else:
        print("\n"+term)
        for key in wiki.keys():
            if term in key and len(term) >= 4:
                found.append({"key": key, "distance": -1})
                print(key, levenshtein_distance(term, key))
                continue
            distance = levenshtein_distance(term, key)
            print(key, distance)
            if distance < 5:
                found.append({"key": key, "distance": distance})
        print()
        found = sorted(found, key=lambda val1: val1["distance"])
        found = found[:min(5, len(found))]

        if len(found) == 1:
            await wiki[found[0]["key"]].sendInfo(ctx)
        elif len(found) > 1:
            await ctx.respond("Entry could not be found. Did you mean any of these?\n" +
                              ", ".join(
                                  ["**"+item["key"]+"**" for item in found]
                              ))
        else:
            await ctx.respond("Entry could not be found.")
