class Character:

    def __init__(self, tag, name):
        self.player: str = ""
        self.name: str = name
        self.tag: str = tag
        self.damage_taken: int = 0
        self.damage_resisted: int = 0
        self.damage_caused: int = 0
        self.damage_healed: int = 0
        self.max_damage: int = 0
        self.kills: int = 0
        self.crits: int = 0
        self.faints: int = 0
        self.dodged: int = 0

    def set_player(self, player: str):
        self.player = player

    def rolled_crit(self):
        self.crits += 1

    def dodge(self):
        self.dodged += 1

    def cause_dam(self, dam: int, kills: int = 0):
        self.damage_caused += dam
        self.kills += kills
        if dam > self.max_damage:
            self.max_damage = dam

    def take_dam(self, dam: int, resisted: bool = False) -> int:
        dam_after_res = int(dam / 2) if resisted else dam
        resisted_dam: int = dam - dam_after_res
        self.damage_taken += dam_after_res
        self.damage_resisted += resisted_dam
        return dam_after_res

    def heal(self, health: int):
        self.damage_healed += health

    def faint(self):
        self.faints += 1

    def __str__(self):
        return f"------------------\n" \
               f"**{self.name}** / _{self.tag}_\n" \
               f"damage caused/taken/healed: " \
               f"{self.damage_caused}/{self.damage_taken}/{self.damage_healed}\n" \
               f"resisted: {self.damage_resisted}" \
               f"max damage in one round: {self.max_damage}\n" \
               f"kills: {self.kills}    crits: {self.crits}   fainted: {self.faints}\n" \
               f"dodges: {self.dodged}"


