from os import linesep as endl
import json


class Character:

    def __init__(self, player_name, name, max_health, damage_taken=0, damage_caused=0, damage_healed=0,max_damage=0):
        self.player = player_name
        self.name = name
        self.health = max_health
        self.max_health = max_health
        self.damage_taken = damage_taken
        self.damage_caused = damage_caused
        self.damage_healed = damage_healed
        self.max_damage = max_damage

    def cause_dam(self, dam: int):
        self.damage_caused += dam
        if dam > self.max_damage:
            self.max_damage = dam

    def take_dam(self, dam: int):
        self.damage_taken += dam
        self.health = max(self.health - dam, 0)

    def heal_dam(self, health: int):
        self.damage_healed += health
        self.health = min(self.max_health, self.health + health)

    def heal_max(self):
        diff = self.max_health - self.health
        self.damage_healed += diff
        self.health = self.max_health

    def inc_max_health(self, health: int):
        self.max_health += health
        self.health += health

    def __str__(self):
        return "------------------\n" +\
            self.name + "/" + self.player + "    " + \
            "health: " + str(self.health) + "/" + str(self.max_health) + "    " + \
            "damage c/t: " + str(self.damage_caused) + "/" + str(self.damage_taken) + "    " + \
            "healed: " + str(self.damage_healed)


def toJSON(character):
    return {
        'player': character.player,
        'name': character.name,
        "health": character.health,
        "max_health": character.max_health,
        "max_damage": character.max_damage,
        "damage_taken": character.damage_taken,
        "damage_caused": character.damage_caused,
        "damage_healed": character.damage_healed
    }


def char_from_data(data):
    char = Character(data['player'], data['name'], data['max_health'])
    char.health = data['health']
    char.max_damage = data['max_damage']
    char.damage_taken = data['damage_taken']
    char.damage_caused = data['damage_caused']
    char.damage_healed = data['damage_healed']
    return char


