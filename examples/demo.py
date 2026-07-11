#!/usr/bin/env python
import random
import sys

import die


def print_args(*args):
    sys.stdout.write(' '.join(str(a) for a in args))
    sys.stdout.write('\n')
    sys.stdout.flush()


def print_odds(roll):
    lines = list()
    cumulative = 0
    for rolled, count, percent in roll.odds:
        cumulative += percent
        quoted = f'"{rolled}"'
        lines.append(
            f'{quoted:>5} -> {count:<5} {percent * 100:6.2f}% {cumulative * 100:6.2f}%',
        )
    joined = '\n'.join(lines)
    print_args(f'"{roll}" rolled probabilities:\n{joined}\n')


def print_summary(roll, count):
    stat = die.Statistic(roll)
    stat.run(count)
    print_args(f'{count:<4} "{roll}s"')
    for slot in stat.bucket:
        print_args(
            f'{slot[0]:>5} -> {slot[1]}',
        )
        if slot[0] == stat.avg:
            print_args(' "average"')


print_args('Various Die types.')
percentile = die.Standard(100)
Fudge = die.NumericBased('dFudge', (('+', 1, 2), ('-', -1, 2), (' ', 0, 2)))
FudgePlus = die.NumericBased('dFudge+', (('+', 1, 4), (' ', 0, 2)))
FudgeMinus = die.NumericBased('dFudge-', (('-', -1, 4), (' ', 0, 2)))
d6 = die.Standard(6)
dSymbolic = die.Symbolic(
    'dSymbolic',
    (
        ('bark', 'dog', 2),
        ('meow', 'cat', 1),
    ),
)
d6x = die.ExplodingDie(6)
d20p = die.ExplodingDie(20, explode_to=die.ExplodingDie(6, math_correct=True), math_correct=True)

print_args(f'  {percentile} a {percentile.description}')
print_args(f'  {Fudge} a {Fudge.description}')
print_args(f'  {FudgePlus} a {FudgePlus.description}')
print_args(f'  {FudgeMinus} a {FudgeMinus.description}')
print_args(f'  {d6} faces {d6.faces} - values {d6.values}')
print_args(f'  {dSymbolic} faces {dSymbolic.faces} - values {dSymbolic.values}')
print_args(f'  {d6x} a {d6x.description}')
print_args(f'  {d20p} a {d20p.description}')
print_args(f'  {die.d100rm} a {die.d100rm.description}')
print_args()

print_args('Exploding dice roll again and add when they roll into the explode range.')
print_args(f'  {d6x} five rolls (some > 6, exploded) {d6x.rolls(5)}')
print_args(f'  {d20p} five rolls (some > 20, exploded, math corrected) {d20p.rolls(5)}')
print_args(f'  {die.d100rm} five rolls (Rolemaster double-ended: some > 95 or < 6, exploded) {die.d100rm.rolls(5)}')
print_args()

print_args('Ready-made dice, importable directly, e.g. `from die import d6, d20x, d100p`.')
print_args(f'  {die.d6} {die.d6.roll()}, {die.d20x} {die.d20x.roll()}, {die.d100p} {die.d100p.roll()}')
print_args()

print_args('Different methods to roll Die.')
print_args(f'  single roll {d6.roll()}, five rolls {d6.rolls(5)}')
print_args(f'  (face, value) roll {d6.roll_item()}')
print_args()

print_args('Reproducible rolls via seeded rng.')
seeded = die.Standard(6, rng=random.Random(42))
print_args(f'  {seeded} with random.Random(42) - {seeded.rolls(5)}')
# Assigning die.Die.rng affects every die at once, even ones already created
# (like d6 above), except dice given their own rng.
die.Die.rng = random.Random(42)
first = (d6.rolls(5), percentile.rolls(5))
die.Die.rng = random.Random(42)
second = (d6.rolls(5), percentile.rolls(5))
print_args(f'  module-wide die.Die.rng, {d6} and {percentile} repeat: {first == second} - {first}')
die.Die.rng = random
print_args()

print_args('Die may be combined into Roll objects.')
FudgeRoll = die.Roll((Fudge, Fudge, Fudge, Fudge))
DnDStatRoll = die.Roll(
    (
        d6,
        d6,
        d6,
    ),
)
# Another way to construct a Roll().
twod6 = die.Roll()
for _ in range(2):
    twod6.add_die(d6)
# Rolls apply func (default sum) to the individual die rolls.
best_of_two = die.Roll((d6, d6), name='best of 2d6', func=max)

print_args(f'  {FudgeRoll} - {FudgeRoll.roll()} ')
rolls = ', '.join(str(i) for i in DnDStatRoll.rolls(6))
print_args(f'  {DnDStatRoll} six times - {rolls} ')
print_args(f'  {best_of_two} - {best_of_two.roll()} ')
print_args()

print_args('Rolls may also be built from dice notation.')
attack = die.parse('2d6+3')
print_args(f'  {attack} - {attack.roll()} ')
fudge4 = die.parse('4dF')
print_args(f'  {fudge4} - {fudge4.roll()} ')
print_args()

# Some statistics.
print_odds(FudgeRoll)
print_odds(twod6)
print_summary(twod6, 1000)
