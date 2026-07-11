#!/usr/bin/env python
"""Walk through of Die: types, exploding, rerolling, rolling, history, rng."""

import random
from collections import Counter

import die

print('Various Die types.')
percentile = die.Standard(100)
Fudge = die.NumericBased('dF', (('+', 1, 2), ('-', -1, 2), (' ', 0, 2)))
FudgePlus = die.NumericBased('dF+', (('+', 1, 4), (' ', 0, 2)))
FudgeMinus = die.NumericBased('dF-', (('-', -1, 4), (' ', 0, 2)))
d6 = die.Standard(6)
dSymbolic = die.Symbolic(
    'dSymbolic',
    (
        ('bark', 'dog', 2),
        ('meow', 'cat', 1),
    ),
)
d6x = die.Exploding(6)
d20p = die.Exploding(20, explode_to=die.Exploding(6, math_correct=True), math_correct=True)

print(f'  {percentile.notation} a {percentile.description}')
print(f'  {Fudge.notation} a {Fudge.description}')
print(f'  {FudgePlus.notation} a {FudgePlus.description}')
print(f'  {FudgeMinus.notation} a {FudgeMinus.description}')
print(f'  {d6.notation} faces {d6.faces} - values {d6.values}')
print(f'  {dSymbolic.notation} faces {dSymbolic.faces} - values {dSymbolic.values}')
print(f'  {d6x.notation} a {d6x.description}')
print(f'  {d20p.notation} a {d20p.description}')
print(f'  {die.d100rm.notation} a {die.d100rm.description}')
print()

print('Exploding dice roll again and add when they roll into the explode range.')
print(f'  {d6x.notation} five rolls (some > 6, exploded) {d6x.roll(5, func=list)}')
print(
    f'  {d20p.notation} five rolls (some > 20, exploded, math corrected) {d20p.roll(5, func=list)}',
)
print(
    f'  {die.d100rm.notation} five rolls (Rolemaster double-ended: some > 95 or < 6, exploded) '
    f'{die.d100rm.roll(5, func=list)}',
)
print()

print('Rerolling dice roll again when they roll into the reroll range.')
d6r = die.Rerolling(6)
d6rr2 = die.Rerolling(6, reroll_range=2, once=False)
print(f'  {d6r.notation} a {d6r.description}')
print(f'  {d6rr2.notation} five rolls (never 1 or 2) {d6rr2.roll(5, func=list)}')
print()

print('Ready-made dice, importable directly, e.g. `from die import d6, d20x, d100p`.')
print(
    f'  {die.d6.notation} {die.d6.roll()}, {die.d20x.notation} {die.d20x.roll()}, '
    f'{die.d100p.notation} {die.d100p.roll()}',
)
print(f'  averaging die (2/3/3/4/4/5) {die.averaging.roll()}, d09 (0-9) {die.d09.roll()}')
print()

print('Warhammer 40k dice: scatter (HIT/arrow) and blast (numeric shots, or MISFIRE).')
print(f'  {die.scatter.notation} five rolls {die.scatter.roll(5, func=list)}')
print(f'  {die.blast.notation} five rolls {die.blast.roll(5, func=list)}')
print()

print('FFG narrative dice (Genesys, Star Wars): each face value is a Counter of symbols.')
print(f'  {die.gsys_proficiency.notation} one roll {die.gsys_proficiency.roll()}')
# A dice pool: roll several dice and total their symbols (cancellation left to the caller).
pool = (die.gsys_proficiency, die.gsys_ability, die.gsys_difficulty)
symbols = sum((d.roll() for d in pool), Counter())
print(f'  pool {[d.notation for d in pool]} totals {dict(symbols)}')
print()

print('Different methods to roll Die.')
print(
    f'  single roll {d6.roll()}, five rolls summed {d6.roll(5)}, as a list {d6.roll(5, func=list)}',
)
print(f'  max of three rolls {d6.roll(3, max)}')
print()

print('str(), int(), and float() also roll (same as every other operator).')
print(f'  str({d6.notation}) -> "{d6}", int -> {int(d6)}, float -> {float(d6)}')
print()

print('Die remember every roll; subscripting the history does not roll.')
d6.clear()
d6.roll(3)
print(f'  after three rolls: result {d6.result}, face "{d6.face}", value {d6.value}')
print(f'  first roll {d6[0]}, most recent {d6[-1]}, all {list(d6)}, len {len(d6)}')
print(f'  full records via history: {d6.history}')
d6.clear()
print(f'  after clear(): len {len(d6)}')
print()

print('Reproducible rolls via seeded rng.')
seeded = die.Standard(6, rng=random.Random(42))
print(f'  {seeded.notation} with random.Random(42) - {seeded.roll(5, func=list)}')
# Assigning die.Die.rng affects every die at once, even ones already created
# (like d6 above), except dice given their own rng.
die.Die.rng = random.Random(42)
first = (d6.roll(5, func=list), percentile.roll(5, func=list))
die.Die.rng = random.Random(42)
second = (d6.roll(5, func=list), percentile.roll(5, func=list))
print(
    f'  module-wide die.Die.rng, {d6.notation} and {percentile.notation} repeat: '
    f'{first == second} - {first}',
)
die.Die.rng = random
