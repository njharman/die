import die


class TestReadyMadeDice:
    def test_plain_dice_are_standard(self):
        for d, sides in (
            (die.d2, 2),
            (die.d3, 3),
            (die.d4, 4),
            (die.d6, 6),
            (die.d8, 8),
            (die.d10, 10),
            (die.d12, 12),
            (die.d16, 16),
            (die.d20, 20),
            (die.d24, 24),
            (die.d30, 30),
            (die.d100, 100),
        ):
            assert d.sides == sides
            assert d.roll() in d.values

    def test_exploding_dice(self):
        for d, sides in (
            (die.d2x, 2),
            (die.d6x, 6),
            (die.d100x, 100),
        ):
            assert d.sides == sides
            assert d.name == f'd{sides}x'
            assert d.roll() >= 1

    def test_penetrating_dice(self):
        for d, sides in (
            (die.d2p, 2),
            (die.d6p, 6),
            (die.d20p, 20),
            (die.d100p, 100),
        ):
            assert d.sides == sides
            assert d.name == f'd{sides}p'
            assert d.roll() >= 0

    def test_d100rm(self):
        assert die.d100rm.sides == 100
        assert die.d100rm.roll() >= -5

    def test_coin(self):
        assert die.coin.sides == 2
        assert sorted(die.coin.values) == [0, 1]
        assert die.coin.roll() in (0, 1)

    def test_dfudge(self):
        assert die.dFudge.sides == 6
        assert sorted(die.dFudge.values) == [-1, -1, 0, 0, 1, 1]
        assert die.dFudge.roll() in (-1, 0, 1)

    def test_d0(self):
        assert die.d0.name == 'd0'
        assert die.d0.sides == 1
        assert die.d0.values == [0]
        assert die.d0.roll() == 0
        assert die.d0 + 5 == 5
