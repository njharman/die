#!/usr/bin/env python

import die


def print_odds(roll):
    lines = []
    cumulative = 0
    for x in roll.odds:
        cumulative += x[2]
        lines.append('%5s -> %-5i %6.2f%% %6.2f%%' % ('"%s"' % str(x[0]), x[1], x[2] * 100, cumulative * 100))
    print '%s rolled probabilities:\n%s\n' % (str(roll), '\n'.join(lines))


def print_summary(roll, count):
    stat = die.stats.Statistic(roll)
    stat.do_run(count)
    print '%-4i %ss' % (count, roll)
    for slot in stat.bucket:
        print '%5s -> %i' % (slot[0], slot[1]),
        if slot[0] == stat.avr:
            print ' "average"'
        else:
            print


# Various dice.
percentile = die.Standard(100)
Fudge = die.NumericBased('dFudge', (('+', 1, 2), ('-', -1, 2), (' ', 0, 2)))
FudgePlus = die.NumericBased('dFudge+', (('+', 1, 4), (' ', 0, 2)))
FudgeMinus = die.NumericBased('dFudge-', (('-', -1, 4), (' ', 0, 2)))
d6 = die.Standard(6)
dWeird = die.Weird('dWeird', (('bark', 'dog', 2), ('meow', 'cat', 1), ))

print '%s a %s' % (percentile, percentile.description)
print '%s a %s' % (Fudge, Fudge.description)
print '%s a %s' % (FudgePlus, FudgePlus.description)
print '%s a %s' % (FudgeMinus, FudgeMinus.description)
print '%s faces %s - values %s' % (d6, d6.faces, d6.values)
print '%s faces %s - values %s' % (dWeird, dWeird.faces, dWeird.values)
print

# Roll()s group dice into a set.
FudgeRoll = die.Roll((Fudge, Fudge, Fudge, Fudge))
DnDStatRoll = die.Roll((d6, d6, d6, ))
# Another way to construct a Roll().
twod6 = die.Roll()
for x in range(2):
    twod6.add_die(d6)

print FudgeRoll, '-', FudgeRoll.roll_total()
print DnDStatRoll, 'x6 -', ', '.join(str(i) for i in DnDStatRoll.roll_totalX(6))
print

print_odds(FudgeRoll)
print_odds(twod6)
print_summary(twod6, 1000)
