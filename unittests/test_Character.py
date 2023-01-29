from src.ext.Campaign.Character import Character


class TestCharacter:
    def test_char_constructor(self):
        c1 = Character("test", "test_name", 20)
        assert c1.player == ""
        assert c1.tag == "test"
        assert c1.health == 20
        assert c1.max_health == 20
        assert c1.damage_taken == 0
        assert c1.damage_caused == 0
        assert c1.damage_healed == 0
        assert c1.max_damage == 0
        assert c1.kills == 0
        assert c1.crits == 0
        assert c1.faints == 0
        assert c1.dodged == 0

    def test_set_player(self):
        c1 = Character("test", "test_name", 20)
        c1.set_player(20)
        assert c1.player == "20"

        c1.set_player("30")
        assert c1.player == "30"

    def test_test(self):
        c = Character("test", "test_name", 20)
        c.tank(2)
        c.rolled_crit()
        c.dodge()
        str(c)
        c.to_json()

    def test_cause_dam(self):
        c1 = Character("test", "test_name", 20)

        c1.cause_dam(20)
        assert c1.damage_caused == 20
        assert c1.kills == 0
        assert c1.max_damage == 20

        c1.cause_dam(10)
        assert c1.damage_caused == 30
        assert c1.kills == 0
        assert c1.max_damage == 20

        c1.cause_dam(30, 2)
        assert c1.damage_caused == 60
        assert c1.kills == 2
        assert c1.max_damage == 30

    def test_take_dam(self):
        c1 = Character("test", "test_name", 50)

        fainted, dam_taken = c1.take_dam(10)
        assert fainted is False
        assert dam_taken == 10
        assert c1.damage_taken == 10
        assert c1.health == 40
        assert c1.faints == 0

        fainted, dam_taken = c1.take_dam(10)
        assert fainted is False
        assert dam_taken == 10
        assert c1.damage_taken == 20
        assert c1.health == 30
        assert c1.faints == 0

        fainted, dam_taken = c1.take_dam(10, True)
        assert fainted is False
        assert dam_taken == 5
        assert c1.damage_taken == 30
        assert c1.health == 25
        assert c1.faints == 0

        fainted, dam_taken = c1.take_dam(50, True)
        assert fainted
        assert dam_taken == 25
        assert c1.damage_taken == 80
        assert c1.health == 0
        assert c1.faints == 1

        fainted, dam_taken = c1.take_dam(5, True)
        assert fainted is False
        assert dam_taken == 2
        assert c1.damage_taken == 85
        assert c1.health == 0
        assert c1.faints == 1

    def test_heal_dam(self):
        c = Character("test", "test", 20)
        c.health = 0

        c.heal_dam(10)
        assert c.health == 10
        assert c.damage_healed == 10
        c.heal_dam(20)
        assert c.health == 20
        assert c.damage_healed == 20

    def test_heal_max(self):
        c = Character("test", "test", 20)
        c.health = 10
        c.heal_max()
        assert c.health == 20
        assert c.damage_healed == 10
        c.heal_max()
        assert c.health == 20
        assert c.damage_healed == 10

    def test_set_max_health(self):
        c = Character("test", "test", 20)
        c.set_max_health(40)
        assert c.health == 40
        assert c.max_health == 40

        c.health = 10
        c.set_max_health(50)
        assert c.health == 20
        assert c.max_health == 50
