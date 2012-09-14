#!/usr/bin/env python
import sys
import die


def print_(*args):
    sys.stdout.write(' '.join(str(a) for a in args))
    sys.stdout.write('\n')
    sys.stdout.flush()


def print_odds(roll):
    lines = list()
    cumulative = 0
    for rolled, count, percent in roll.odds:
        cumulative += percent
        lines.append('%5s -> %-5i %6.2f%% %6.2f%%' % (
            '"%s"' % rolled,
            count,
            percent * 100,
            cumulative * 100))
    print_('"%s" rolled probabilities:\n%s\n' % (str(roll), '\n'.join(lines)))


def print_summary(roll, count):
    stat = die.stats.Statistic(roll)
    stat.do_run(count)
    print_('%-4i "%ss"' % (count, roll))
    for slot in stat.bucket:
        print_('%5s -> %i' % (slot[0], slot[1]),)
        if slot[0] == stat.avr:
            print_(' "average"')


print_('Various Die types.')
percentile = die.Standard(100)
Fudge = die.NumericBased('dFudge', (('+', 1, 2), ('-', -1, 2), (' ', 0, 2)))
FudgePlus = die.NumericBased('dFudge+', (('+', 1, 4), (' ', 0, 2)))
FudgeMinus = die.NumericBased('dFudge-', (('-', -1, 4), (' ', 0, 2)))
d6 = die.Standard(6)
dWeird = die.Weird('dWeird', (('bark', 'dog', 2), ('meow', 'cat', 1), ))

print_('  %s a %s' % (percentile, percentile.description))
print_('  %s a %s' % (Fudge, Fudge.description))
print_('  %s a %s' % (FudgePlus, FudgePlus.description))
print_('  %s a %s' % (FudgeMinus, FudgeMinus.description))
print_('  %s faces %s - values %s' % (d6, d6.faces, d6.values))
print_('  %s faces %s - values %s' % (dWeird, dWeird.faces, dWeird.values))
print_()

print_('Different methods to roll Die.')
print ('  float(%s) -> %f' % (d6, float(d6)))
print ('  int(%s) -> %i' % (d6, int(d6)))
print ('  %s+10 -> %i (and most other numeric operators)' % (d6, d6 + 10))
print ('  %s>10 -> %s (and most other numeric comparisons except ==, !=)' % (d6, d6 > 10))
print ('  %s() -> %i' % (d6, d6()))
print ('  %s.roll() -> %i' % (d6, d6.roll()))
print_()

print_('Die may be combined into Roll objects.')
FudgeRoll = die.Roll((Fudge, Fudge, Fudge, Fudge))
DnDStatRoll = die.Roll((d6, d6, d6, ))
# Another way to construct a Roll().
twod6 = die.Roll()
for x in range(2):
    twod6.add_die(d6)

print_('  %s - %s ' % (FudgeRoll, FudgeRoll.roll()))
print_('  %s six times - %s ' % (DnDStatRoll, ', '.join(str(i) for i in DnDStatRoll.roll(6))))
print_()

# Some statistics.
print_odds(FudgeRoll)
print_odds(twod6)
print_summary(twod6, 1000)
