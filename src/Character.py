from os import linesep as endl


class Character:

    def __init__(self, playername, name):
        self.player = playername
        self.name = name
        self.damage_taken = 0
        self.damage_caused = 0
        self.damage_healed = 0

    def cause_dam(self, dam):
        self.damage_caused += dam

    def take_dam(self, dam):
        self.damage_taken += dam

    def heal_dam(self, dam):
        self.damage_healed += dam

    def __str__(self):
        return self.name + "\n" + \
               "    Damage taken: " + str(self.damage_taken) + endl + \
               "    Damage caused: " + str(self.damage_caused) + endl +\
               "    Damage healed: " + str(self.damage_healed)


