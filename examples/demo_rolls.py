#!/usr/bin/env python
"""Walk through of Roll: construction, dice notation, composing, odds."""

import die

print('Die may be combined into Roll objects.')
Fudge = die.NumericBased('dF', (('+', 1, 2), ('-', -1, 2), (' ', 0, 2)))
d6 = die.Standard(6)
FudgeRoll = die.Roll((Fudge, Fudge, Fudge, Fudge))
DnDStatRoll = die.Roll(
    (
        d6,
        d6,
        d6,
    ),
)
# Another way to construct a Roll(): from a list of dice.
twod6 = die.Roll([d6 for _ in range(2)])
# Rolls apply func (default sum) to the individual die rolls.
best_of_two = die.Roll((d6, d6), func=max, name='best of 2d6')

print(f'  {FudgeRoll.notation} - {FudgeRoll.roll()} ')
rolls = ', '.join(str(i) for i in DnDStatRoll.roll(6, func=list))
print(f'  {DnDStatRoll.notation} six times - {rolls} ')
print(f'  {best_of_two.name} - {best_of_two.roll()} ')
print()

print('Rolls remember every roll too.')
twod6.roll(2)
print(f'  results {twod6.results}, value {twod6.value}')
print(f'  first roll {twod6[0]}, most recent {twod6[-1]}, len {len(twod6)}')
print(f'  full records via history: {twod6.history}')
print()

print('Rolls may also be built from dice notation.')
attack = die.parse('2d6+3')
print(f'  {attack.notation} - {attack.roll()} ')
fudge4 = die.parse('4dF')
print(f'  {fudge4.notation} - {fudge4.roll()} ')
print()

print('Die and Roll compose via plus/minus/times/div/mod, chains bind left to right.')
composed = die.d6.times(2).plus(3).div(die.d6)
print(f'  {composed.notation} - {composed.roll()}')
chained = die.d8.plus(die.d6).minus(1)
print(f'  {chained.notation} - {chained.roll()}')
# Notation expressions (standard precedence, parens) build the identical Roll.
parsed = die.parse('(d6*2+3)/d6')
print(f'  parse("(d6*2+3)/d6") odds == composed odds: {parsed.odds == composed.odds}')
print()

print('Keep/drop the n highest/lowest die values, summing the kept.')
ability = die.parse('4d6').drop_lowest()
print(f'  {ability.notation} - {ability.roll()}')
advantage = die.d20.plus(die.d20).keep_highest()
print(f'  {advantage.notation} - {advantage.roll()}')
print()

print('Success/failure counting for dice pools.')
pool = die.parse('6d10')
hits = pool.successes(7)
print(f'  {hits.notation} - {hits.roll()} dice rolled 7+')
botches = pool.failures(1)
print(f'  {botches.notation} - {botches.roll()} dice rolled 1')
print()

print('Every numeric Roll knows its exact odds.')
threed6 = die.parse('3d6')
print(f'  {threed6.notation} lowest {threed6.odds[0]}, highest {threed6.odds[-1]}')
print(f'  chance of 15+ on {threed6.notation}: {threed6.chance(gte=15):.2f}%')
print(f'  chance of 2 or lower on {die.d20.notation}: {die.d20.chance(lte=2):.1f}%')
