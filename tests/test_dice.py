from collections import Counter

from helpers import SequenceRng

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

    def test_exploding_dice(self, monkeypatch):
        for d, sides in (
            (die.d2x, 2),
            (die.d6x, 6),
            (die.d100x, 100),
        ):
            assert d.sides == sides
            assert d.notation == f'd{sides}x'
            # Rolling max explodes, adding a re-roll (here a 1) to the total.
            monkeypatch.setattr(die.Die, 'rng', SequenceRng([sides, 1]))
            assert d.roll() == sides + 1

    def test_penetrating_dice(self, monkeypatch):
        for d, sides in (
            (die.d2p, 2),
            (die.d6p, 6),
            (die.d20p, 20),
            (die.d100p, 100),
        ):
            assert d.sides == sides
            assert d.notation == f'd{sides}p'
            # Rolling max penetrates: the re-roll (here a 1) is added math-corrected (minus 1),
            # so a max followed by a 1 totals exactly sides. Chained explode_to dice (d20p, d100p)
            # draw the re-roll from the same class rng.
            monkeypatch.setattr(die.Die, 'rng', SequenceRng([sides, 1]))
            assert d.roll() == sides

    def test_d100rm(self):
        assert die.d100rm.sides == 100

    def test_d100rm_normal_roll(self):
        # Mid-range roll neither explodes low (<=5) nor high (>=96).
        d = die.Exploding(100, explode_range=5, explode_range_low=5, rng=SequenceRng([50]))
        assert d.roll() == 50

    def test_d100rm_low_open_ended(self):
        # Rolling <=5 subtracts a fresh d100 roll, so results go below zero (unbounded below).
        d = die.Exploding(100, explode_range=5, explode_range_low=5, rng=SequenceRng([3, 50]))
        assert d.roll() == 3 - 50

    def test_d100rm_high_open_ended(self):
        # Rolling >=96 adds a fresh d100 roll.
        d = die.Exploding(100, explode_range=5, explode_range_low=5, rng=SequenceRng([98, 40]))
        assert d.roll() == 98 + 40

    def test_coin(self):
        assert die.coin.sides == 2
        assert sorted(die.coin.values) == [0, 1]
        assert die.coin.roll() in (0, 1)

    def test_df(self):
        assert die.dF.sides == 6
        assert sorted(die.dF.values) == [-1, -1, 0, 0, 1, 1]
        assert die.dF.roll() in (-1, 0, 1)

    def test_df_round_trips_and_groups_with_parsed(self):
        r = die.Roll([die.dF, die.dF])
        assert r.notation == '2dF'
        parsed = die.Roll.from_notation(r.notation)
        assert parsed.notation == '2dF'
        assert [d.items for d in parsed.dice] == [d.items for d in r.dice]

    def test_doubling(self):
        assert die.doubling.sides == 6
        assert sorted(die.doubling.values) == [2, 4, 8, 16, 32, 64]
        assert die.doubling.roll() in (2, 4, 8, 16, 32, 64)

    def test_exports(self):
        assert die.Odds is die.rolls.Odds
        assert die.Rolled is die.rolls.Rolled
        assert 'd100lo' in die.__all__
        assert 'd100ho' in die.__all__

    def test_d0(self):
        assert die.d0.notation == 'd0'
        assert die.d0.sides == 1
        assert die.d0.values == [0]
        assert die.d0.roll() == 0
        assert die.d0 + 5 == 5

    def test_averaging(self):
        assert die.averaging.sides == 6
        assert sorted(die.averaging.values) == [2, 3, 3, 4, 4, 5]
        assert die.averaging.roll() in (2, 3, 4, 5)

    def test_d09(self):
        assert die.d09.notation == 'd09'
        assert die.d09.sides == 10
        assert sorted(die.d09.values) == list(range(10))
        assert die.d09.roll() in range(10)

    def test_ffg_narrative_dice(self):
        for d, sides in (
            (die.gsys_boost, 6),
            (die.gsys_setback, 6),
            (die.gsys_ability, 8),
            (die.gsys_difficulty, 8),
            (die.gsys_proficiency, 12),
            (die.gsys_challenge, 12),
            (die.gsys_force, 12),
        ):
            assert d.sides == sides
            assert d.numeric is False
            assert isinstance(d.roll(), Counter)

    def test_ffg_symbols_net_across_dice(self):
        total = die.gsys_ability.roll(3, func=lambda vs: sum(vs, Counter()))
        assert isinstance(total, Counter)
        assert set(total) <= {'success', 'advantage'}

    def test_scatter(self):
        assert die.scatter.sides == 6
        assert sorted(die.scatter.values) == ['HIT', 'HIT', 'arrow', 'arrow', 'arrow', 'arrow']
        assert die.scatter.roll() in ('HIT', 'arrow')

    def test_blast(self):
        assert die.blast.sides == 6
        assert die.blast.numeric is False
        assert sorted(die.blast.values, key=str) == [10, 2, 4, 6, 8, 'MISFIRE']
        assert die.blast.roll() in (2, 4, 6, 8, 10, 'MISFIRE')
