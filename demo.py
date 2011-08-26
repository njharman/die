#!/usr/bin/python
import random
import die

def printOdds(roll):
    lines = []
    cumulative = 0
    for x in roll.odds:
        cumulative += x[2]
        lines.append("%5s -> %-5i %6.2f%% %6.2f%%"%("'%s'"%str(x[0]),x[1],x[2]*100, cumulative*100))
    print "%s probabilities:\n%s\n" % (str(roll), '\n'.join(lines))

def printSummary(roll, count):
    stat = die.stats.Statistic(roll)
    stat.doRun(count)
    sum = stat.sum
    avr = stat.avr
    print "%-4i %ss\tavr %i\tsum %i"%(count, roll, avr, sum)
    for slot in stat.bucket:
        print "%s -> %i" %(slot[0], slot[1])
    print "\n"

# various dice
percentile = die.Standard(100)
Fudge = die.NumericBased('Fudge', (('+',1,2), ('-',-1,2), (' ',0,2)))
FudgePlus  = die.NumericBased('Fudge+', (('+', 1,4), (' ',0,2)))
FudgeMinus = die.NumericBased('Fudge-', (('-',-1,4), (' ',0,2)))
d6 = die.Standard(6)
dWeird = die.Weird('dWeird', (('bark','dog',2),('meow','cat',1),))

print "Percentile - %s / %s" % (percentile, percentile.description)
print "Fudge - %s / %s" % (Fudge, Fudge.description)
print "d6 %s - %s" % (d6.faces, d6.values)
print "%s %s - %s\n" % (dWeird, dWeird.faces, dWeird.values)

# Rolls group dice into a set
fudgeRoll = die.Roll(( Fudge, Fudge, Fudge, Fudge))
DnDStatRoll = die.Roll((d6,d6,d6,))
print fudgeRoll, fudgeRoll.rollTotal(), "\n"
print DnDStatRoll, DnDStatRoll.rollTotalX(6), "\n"

# another way to construct a Roll
aRoll = die.Roll()
for x in range(2):
    aRoll.addDie(d6)
printOdds(aRoll)
printSummary(aRoll, 1000)
