import json
import os
import pathlib

from .WikiEntry import EntryLabels as eLabel
from .WikiEntry.ClassItemEntry import ClassItemEntry
from .WikiEntry.CompositeEntry import CompositeEntry
from .WikiEntry.CraftedItemEntry import CraftedItemEntry
from .WikiEntry.ItemEntry import ItemEntry
from .WikiEntry.PlaybookEntry import PlaybookEntry
from .WikiEntry.StatEntry import StatEntry

relative_wiki_path = os.sep.join(["Assets", "item_wiki.json"])
wiki = {}


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
            if name == eLabel.CAT_ITEMS_LABEL:
                insert_wiki_entry(entry, ItemEntry)
            elif name == eLabel.CAT_CLASS_ITEMS_LABEL:
                insert_wiki_entry(entry, ClassItemEntry)
            elif name == eLabel.CAT_PLAYBOOKS_LABEL:
                insert_wiki_entry(entry, PlaybookEntry)
            elif name == eLabel.CAT_STATS_LABEL:
                composite_wiki_entry = insert_wiki_entry(entry, CompositeEntry)
                for child in composite_wiki_entry.children:
                    insert_wiki_entry(child, StatEntry)
            elif name == eLabel.CAT_CREATIONS_LABEL:
                for item_cat in entry:
                    item_type = item_cat[eLabel.CREATION_TYPE_LABEL]
                    item_drawback = item_cat[eLabel.CREATION_DRAWBACK_LABEL] if eLabel.CREATION_DRAWBACK_LABEL in entry else ""
                    for item in item_cat[eLabel.LIST_LABEL]:
                        item[eLabel.CREATION_TYPE_LABEL] = item_type
                        item[eLabel.CREATION_DRAWBACK_LABEL] = item_drawback
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
            key = list_entry[eLabel.NAME_LABEL].lower()
            wiki[key] = wiki_entry_class_type(list_entry)
    else:
        key = checked_object[eLabel.NAME_LABEL].lower()
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
