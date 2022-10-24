class Character:

    def __init__(self, player_name, name, max_health, damage_taken=0,
                 damage_caused=0, damage_healed=0, max_damage=0, kills=0, crits=0, faints=0, dodged=0):
        self.player = player_name
        self.name = name
        self.health = max_health
        self.max_health = max_health
        self.damage_taken = damage_taken
        self.damage_caused = damage_caused
        self.damage_healed = damage_healed
        self.max_damage = max_damage
        self.kills = kills
        self.crits = crits
        self.faints = faints
        self.dodged = dodged

    def to_json(self):
        return self.__dict__

    def rolled_crit(self):
        self.crits += 1

    def dodge(self):
        self.dodged += 1

    def cause_dam(self, dam: int, kills: int = 0):
        self.damage_caused += dam
        self.kills += kills
        if dam > self.max_damage:
            self.max_damage = dam

    def take_dam(self, dam: int, resisted: bool = False):
        dam_after_res = int(dam / 2) if resisted else dam
        fainted = False
        if dam_after_res >= self.health > 0:
            self.faints += 1
            fainted = True
        self.damage_taken += dam
        self.health = max(self.health - dam_after_res, 0)
        return fainted, dam_after_res

    def tank(self, dam):
        self.damage_taken += dam

    def heal_dam(self, health: int):
        self.damage_healed += health
        self.health = min(self.max_health, self.health + health)

    def heal_max(self):
        diff = self.max_health - self.health
        self.damage_healed += diff
        self.health = self.max_health

    def set_max_health(self, new_max: int):
        old_max = self.max_health
        self.max_health = new_max
        self.health = \
            max(
                min(
                    self.health + (new_max - old_max),
                    new_max
                ),
                0
            )

    def __str__(self):
        return f"------------------\n" \
               f"{self.name} health: {self.health}/{self.max_health}    damage taken/caused/maxDam: " \
               f"{self.damage_taken}/{self.damage_caused}/{self.max_damage}    healed: {self.damage_healed}\n" \
               f"kills: {self.kills}    crits: {self.crits}   fainted: {self.faints}\n" \
               f"dodges: {self.dodged}"


def char_from_data(data):
    char = Character(data['player'], data['name'], data['max_health'])
    char.__dict__ = data
    if not char.__dict__.__contains__('crits'):
        char.__dict__['crits'] = 0
        char.__dict__['faints'] = 0
        char.__dict__['kills'] = 0
    if not char.__dict__.__contains__('dodged'):
        char.__dict__['dodged'] = 0
    return char
