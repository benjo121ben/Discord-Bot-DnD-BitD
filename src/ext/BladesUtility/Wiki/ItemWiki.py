import json
import os
import pathlib

from discord.ext.bridge import BridgeExtContext

from . import EntryLabels as eLabel
from .WikiEntry import WikiEntry

relative_wiki_path = os.sep.join(["Assets", "item_wiki.json"])
wiki: dict[str, WikiEntry] = {}


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

    for category in imported_wiki[eLabel.CATEGORIES_LABEL]:
        if eLabel.CPROP_ENTRIES_LABEL in category:
            handle_entries(category)
        if eLabel.CPROP_SUPER_ENTRY_LABEL in category:
            handle_super_entries(category)
        if eLabel.CPROP_ENTRYGROUPS_LABEL in category:
            handle_entrygroup(category)



def handle_entries(category: dict):
    format_info = category[eLabel.CPROP_FORMATINFO_LABEL] if eLabel.CPROP_FORMATINFO_LABEL in category else {}
    for entry in category[eLabel.CPROP_ENTRIES_LABEL]:
        insert_wiki_entry(WikiEntry(entry, format_info))


def handle_entrygroup(category: dict):
    format_info = category[eLabel.CPROP_FORMATINFO_LABEL] if eLabel.CPROP_FORMATINFO_LABEL in category else {}
    for group in category[eLabel.CPROP_ENTRYGROUPS_LABEL]:
        for entry in group[eLabel.CPROP_ENTRIES_LABEL]:
            w_entry = WikiEntry(entry, format_info)
            for field in group[eLabel.ENTRYGROUP_VALUES_LABEL][eLabel.FIELD_LIST_LABEL]:
                w_entry.add_field(
                    field[eLabel.FIELD_HEADER_LABEL],
                    field[eLabel.FIELD_TEXT_LABEL],
                    field[eLabel.FIELD_INLINE_LABEL] if eLabel.FIELD_INLINE_LABEL in field else True
                )
            insert_wiki_entry(w_entry)


def handle_super_entries(category: dict):
    cat_format_info = category[eLabel.CPROP_FORMATINFO_LABEL] if eLabel.CPROP_FORMATINFO_LABEL in category else {}
    sup_entry_info = category[eLabel.CPROP_SUPER_ENTRY_LABEL]
    sup_format_info = sup_entry_info[eLabel.CPROP_FORMATINFO_LABEL] if eLabel.CPROP_FORMATINFO_LABEL in sup_entry_info else {}
    super_entry = WikiEntry(sup_entry_info, cat_format_info)
    if eLabel.CPROP_ENTRIES_LABEL in sup_entry_info:
        for entry in sup_entry_info[eLabel.CPROP_ENTRIES_LABEL]:
            super_entry.add_field(entry[eLabel.TITLE_LABEL], entry[eLabel.DESCRIPTION_LABEL])
            insert_wiki_entry(WikiEntry(entry, sup_format_info))
    elif eLabel.CPROP_REFERENCE_LABEL in sup_entry_info:
        for entry in sup_entry_info[eLabel.CPROP_REFERENCE_LABEL]:
            if entry.lower() not in wiki:
                print(entry, "not found")
                raise RuntimeError(entry + " not found")
            else:
                super_entry.add_field(wiki[entry.lower()].title, wiki[entry.lower()].entry_info[eLabel.DESCRIPTION_LABEL])
    insert_wiki_entry(super_entry)


def insert_wiki_entry(wiki_entry: WikiEntry):
    """
        parses the values inside a list or object type from a json wiki and puts it into the wiki dictionary.
        :param wiki_entry: The wiki entry to be inserted
    """
    wiki[wiki_entry.title.lower()] = wiki_entry


async def send_wiki_entry(ctx: BridgeExtContext, entry: WikiEntry):
    embed, file = entry.get_entry_embed()
    if file is None:
        await ctx.respond(embed=embed)
    else:
        await ctx.respond(embed=embed, file=file)


async def wiki_search(ctx:BridgeExtContext, search_term: str):
    found = []
    term = search_term.lower()
    if term in wiki:
        await send_wiki_entry(ctx, wiki[term])
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
            await send_wiki_entry(ctx, wiki[found[0]["key"]])

        elif len(found) > 1:
            await ctx.respond("Entry could not be found. Did you mean any of these?\n" +
                              ", ".join(
                                  ["**"+item["key"]+"**" for item in found]
                              ))
        else:
            await ctx.respond("Entry could not be found.")
