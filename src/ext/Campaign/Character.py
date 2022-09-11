class Character:

    def __init__(self, player_name, name, max_health, damage_taken=0, damage_caused=0, damage_healed=0, max_damage=0):
        self.player = player_name
        self.name = name
        self.health = max_health
        self.max_health = max_health
        self.damage_taken = damage_taken
        self.damage_caused = damage_caused
        self.damage_healed = damage_healed
        self.max_damage = max_damage

    def to_json(self):
        test = {
            'player': self.player,
            'name': self.name,
            'health': self.health,
            'max_health': self.max_health,
            'damage_taken': self.damage_taken,
            'damage_caused': self.damage_caused,
            'damage_healed': self.damage_healed,
            'max_damage': self.max_damage
        }
        return self.__dict__

    def cause_dam(self, dam: int):
        self.damage_caused += dam
        if dam > self.max_damage:
            self.max_damage = dam

    def take_dam(self, dam: int):
        self.damage_taken += dam
        self.health = max(self.health - dam, 0)

    def take_dam_res(self, dam: int):
        self.damage_taken += dam
        self.health = max(self.health - int(dam/2), 0)

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
            self.name + " " + \
            "health: " + str(self.health) + "/" + str(self.max_health) + "    " + \
            "damage caused/taken/maxDam: " + str(self.damage_caused) + "/" + str(self.damage_taken) + "/" + \
               str(self.max_damage) + "    healed: " + str(self.damage_healed)


def char_from_data(data):
    char = Character(data['player'], data['name'], data['max_health'])
    char.__dict__ = data
    return char


