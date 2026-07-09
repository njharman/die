#!/usr/bin/env python
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
    stat = die.stats.Statistic(roll)
    stat.do_run(count)
    print_args(f'{count:<4} "{roll}s"')
    for slot in stat.bucket:
        print_args(
            f'{slot[0]:>5} -> {slot[1]}',
        )
        if slot[0] == stat.avr:
            print_args(' "average"')


print_args('Various Die types.')
percentile = die.Standard(100)
Fudge = die.NumericBased('dFudge', (('+', 1, 2), ('-', -1, 2), (' ', 0, 2)))
FudgePlus = die.NumericBased('dFudge+', (('+', 1, 4), (' ', 0, 2)))
FudgeMinus = die.NumericBased('dFudge-', (('-', -1, 4), (' ', 0, 2)))
d6 = die.Standard(6)
dWeird = die.Weird(
    'dWeird',
    (
        ('bark', 'dog', 2),
        ('meow', 'cat', 1),
    ),
)

print_args(f'  {percentile} a {percentile.description}')
print_args(f'  {Fudge} a {Fudge.description}')
print_args(f'  {FudgePlus} a {FudgePlus.description}')
print_args(f'  {FudgeMinus} a {FudgeMinus.description}')
print_args(f'  {d6} faces {d6.faces} - values {d6.values}')
print_args(f'  {dWeird} faces {dWeird.faces} - values {dWeird.values}')
print_args()

print_args('Different methods to roll Die.')
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

print_args(f'  {FudgeRoll} - {FudgeRoll.roll()} ')
rolls = ', '.join(str(i) for i in DnDStatRoll.roll(6))
print_args(f'  {DnDStatRoll} six times - {rolls} ')
print_args()

# Some statistics.
print_odds(FudgeRoll)
print_odds(twod6)
print_summary(twod6, 1000)
