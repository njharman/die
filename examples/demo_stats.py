#!/usr/bin/env python
"""Walk through of Statistic and die.charts."""

import json

import die

print('die.Statistic rolls a numeric Roll many times and reports statistics.')
stat = die.Statistic(die.d3d6)
print(f'  Statistic on {stat.roll.notation}, count before run(): {stat.count}')
stat.run(1000)
stat.run(1000)  # run() accumulates onto previous runs
print(f'  after two run(1000) calls, count: {stat.count}')
print(
    f'  mean {stat.mean:.2f}, median {stat.median}, mode {stat.mode}, '
    f'stdev {stat.stdev:.2f}, min {stat.min}, max {stat.max}',
)
print(f'  sum {stat.sum}, first five values {stat.values[:5]}')
print(f'  three most common (stat.counts is a Counter): {stat.counts.most_common(3)}')
print(f'  observed frequencies, empirical Roll.odds: {stat.frequencies[0]}')
print(
    f'  run() returns self, so statistics chain: {die.Statistic(die.parse("d20")).run(100).max}',
)
stat.clear()
print(f'  after clear(), count: {stat.count}')
print()

FudgeRoll = die.parse('4dF')
print(f'Theoretical probabilities of "{FudgeRoll.notation}" (die.charts.histogram).')
print(die.charts.histogram(FudgeRoll, width=40))
print()

twod6 = die.parse('2d6')
stat = die.Statistic(twod6).run(1000)
print(
    f'Observed frequencies of one thousand "{twod6.notation}" rolls '
    f'(same chart function, Statistic source).',
)
print(die.charts.histogram(stat, width=40))
print()

print('Rolled results scattered by roll order (die.charts.scatter).')
print(die.charts.scatter(stat, width=70, height=10))
print()

print('Vega-Lite spec emitters for real graphics; json.dumps a spec and render it')
print('at vega.github.io/editor, in VSCode/JupyterLab, or via vl-convert.')
bar = die.charts.vega(twod6)  # theoretical, bar chart
line = die.charts.vega(stat, kind='line')  # observed, line chart
scatter = die.charts.vega_scatter(stat)  # rolled results, roll order vs value
compare = die.charts.vega_compare(stat)  # observed bars + theoretical line
print(f'  die.charts.vega(twod6) -> {json.dumps(bar)[:70]}...')
print(f'  die.charts.vega(stat, kind="line") -> {json.dumps(line)[:70]}...')
print(f'  die.charts.vega_scatter(stat) -> {json.dumps(scatter)[:70]}...')
print(f'  die.charts.vega_compare(stat) -> {json.dumps(compare)[:70]}...')
