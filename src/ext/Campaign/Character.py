class Character:

    def __init__(self, tag, name, max_health):
        self.player = ""
        self.name = name
        self.tag = tag
        self.health = max_health
        self.max_health = max_health
        self.damage_taken = 0
        self.damage_caused = 0
        self.damage_healed = 0
        self.max_damage = 0
        self.kills = 0
        self.crits = 0
        self.faints = 0
        self.dodged = 0

    def to_json(self):
        return self.__dict__

    def set_player(self, player):
        self.player = str(player)

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
        healing_amount = min(self.max_health - self.health, health)
        self.damage_healed += healing_amount
        self.health = min(self.max_health, self.health + healing_amount)

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
               f"**{self.name}** / _{self.tag}_\n" \
               f"health: {self.health}/{self.max_health}    damage taken/caused/max: " \
               f"{self.damage_taken}/{self.damage_caused}/{self.max_damage}    healed: {self.damage_healed}\n" \
               f"kills: {self.kills}    crits: {self.crits}   fainted: {self.faints}\n" \
               f"dodges: {self.dodged}"


