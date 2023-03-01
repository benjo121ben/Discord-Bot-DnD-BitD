from src.ext.Campaign.Character import Character


class TestCharacter:
    def test_char_constructor(self):
        c1 = Character("test", "test_name")
        assert c1.player == ""
        assert c1.tag == "test"
        assert c1.damage_taken == 0
        assert c1.damage_resisted == 0
        assert c1.damage_caused == 0
        assert c1.damage_healed == 0
        assert c1.max_damage == 0
        assert c1.kills == 0
        assert c1.crits == 0
        assert c1.faints == 0
        assert c1.dodged == 0

    def test_set_player(self):
        c1 = Character("test", "test_name")
        c1.set_player(20)
        assert c1.player == "20"

        c1.set_player("30")
        assert c1.player == "30"

    def test_test(self):
        c = Character("test", "test_name")
        c.take_dam(2)
        c.rolled_crit()
        c.dodge()
        str(c)

    def test_cause_dam(self):
        c1 = Character("test", "test_name")

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
        c1 = Character("test", "test_name")

        dam_taken = c1.take_dam(10)
        assert dam_taken == 10
        assert c1.damage_taken == 10
        assert c1.damage_resisted == 0
        assert c1.faints == 0

        dam_taken = c1.take_dam(10)
        assert dam_taken == 10
        assert c1.damage_taken == 20
        assert c1.damage_resisted == 0
        assert c1.faints == 0

        dam_taken = c1.take_dam(10, True)
        assert dam_taken == 5
        assert c1.damage_taken == 25
        assert c1.damage_resisted == 5
        assert c1.faints == 0

        dam_taken = c1.take_dam(50, True)
        assert dam_taken == 25
        assert c1.damage_taken == 50
        assert c1.damage_resisted == 30
        assert c1.faints == 0

        dam_taken = c1.take_dam(5, True)
        assert dam_taken == 2
        assert c1.damage_taken == 52
        assert c1.damage_resisted == 33
        assert c1.faints == 0

    def test_heal(self):
        c = Character("test", "test")

        c.heal(10)
        assert c.damage_healed == 10
        c.heal(20)
        assert c.damage_healed == 30

