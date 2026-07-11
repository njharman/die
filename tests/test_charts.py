import json

import pytest
from helpers import FakeRoll

import die
import die.charts
from die.stats import Statistic


def stat_of(rolls):
    return Statistic(FakeRoll(rolls)).run(len(rolls))


class TestPoints:
    def test_roll_uses_odds(self):
        r = die.Roll((die.Standard(2),))
        assert die.charts._points(r) == r.odds

    def test_die_lifted_to_roll(self):
        assert die.charts._points(die.d2) == die.Roll((die.d2,)).odds

    def test_statistic_uses_frequencies(self):
        s = stat_of([1, 1, 2])
        assert die.charts._points(s) == s.frequencies

    def test_unchartable_type_raises(self):
        with pytest.raises(TypeError, match='cannot chart'):
            die.charts._points('3d6')

    def test_empty_roll_raises(self):
        with pytest.raises(ValueError, match='nothing to chart'):
            die.charts._points(die.Roll())

    def test_statistic_not_run_raises(self):
        with pytest.raises(RuntimeError, match='run'):
            die.charts._points(Statistic(FakeRoll([1])))


class TestHistogram:
    def test_line_per_value_sorted(self):
        lines = die.charts.histogram(stat_of([3, 1, 1, 2])).splitlines()
        assert len(lines) == 3
        assert [line[0] for line in lines] == ['1', '2', '3']

    def test_peak_bar_spans_width(self):
        lines = die.charts.histogram(stat_of([1, 1, 2]), width=10).splitlines()
        assert '█' * 10 in lines[0]
        assert '█' * 10 not in lines[1]

    def test_percent_column(self):
        lines = die.charts.histogram(stat_of([1, 1, 2, 2])).splitlines()
        assert lines[0].endswith(' 50.00%')
        assert lines[1].endswith(' 50.00%')

    def test_theoretical_from_die(self):
        lines = die.charts.histogram(die.d2, width=10).splitlines()
        assert len(lines) == 2
        assert all(line.endswith(' 50.00%') for line in lines)

    def test_labels_right_aligned(self):
        lines = die.charts.histogram(stat_of([9, 10]), width=5).splitlines()
        assert lines[0].startswith(' 9 ')
        assert lines[1].startswith('10 ')

    def test_width_below_one_raises(self):
        with pytest.raises(ValueError, match='width'):
            die.charts.histogram(die.d2, width=0)


class TestScatter:
    def test_dimensions(self):
        text = die.charts.scatter(stat_of([1, 2, 3, 4]), width=8, height=4)
        lines = text.splitlines()
        assert len(lines) == 5
        assert lines[-1].endswith('└' + '─' * 8)

    def test_axis_labels_extremes(self):
        lines = die.charts.scatter(stat_of([2, 7, 5]), width=8, height=4).splitlines()
        assert lines[0].startswith('7 ')
        assert lines[3].startswith('2 ')

    def test_dots_plotted_corner_to_corner(self):
        lines = die.charts.scatter(stat_of([1, 6]), width=8, height=4).splitlines()
        assert lines[3].endswith('│·' + ' ' * 7)
        assert lines[0].endswith(' ' * 7 + '·')

    def test_constant_values_bottom_row(self):
        lines = die.charts.scatter(stat_of([4, 4, 4]), width=8, height=4).splitlines()
        assert '·' in lines[3]
        assert all('·' not in line for line in lines[:3])

    def test_single_roll(self):
        lines = die.charts.scatter(stat_of([5]), width=8, height=4).splitlines()
        assert lines[3].endswith('│·' + ' ' * 7)

    def test_non_statistic_raises(self):
        with pytest.raises(TypeError, match='needs a Statistic'):
            die.charts.scatter(die.Roll((die.d6,)))

    def test_bad_dimensions_raise(self):
        with pytest.raises(ValueError, match='width and height'):
            die.charts.scatter(stat_of([1, 2]), width=0)

    def test_not_run_raises(self):
        with pytest.raises(RuntimeError, match='run'):
            die.charts.scatter(Statistic(FakeRoll([1])))


class TestVega:
    def test_bar_spec(self):
        spec = die.charts.vega(die.Roll((die.d2,)))
        assert spec['$schema'].endswith('vega-lite/v5.json')
        assert spec['mark'] == 'bar'
        assert spec['encoding']['x']['type'] == 'ordinal'
        assert spec['data']['values'] == [
            {'value': 1, 'probability': 0.5},
            {'value': 2, 'probability': 0.5},
        ]

    def test_line_spec(self):
        spec = die.charts.vega(die.d2, kind='line')
        assert spec['mark'] == {'type': 'line', 'point': True}
        assert spec['encoding']['x']['type'] == 'quantitative'

    def test_statistic_titled_with_roll_count(self):
        spec = die.charts.vega(stat_of([1, 1, 2]))
        assert spec['title'] == 'fake, 3 rolls'

    def test_roll_titled_with_notation(self):
        assert die.charts.vega(die.parse('3d6'))['title'] == '3d6'

    def test_bad_kind_raises(self):
        with pytest.raises(ValueError, match='kind'):
            die.charts.vega(die.d2, kind='pie')

    def test_json_serializable(self):
        json.dumps(die.charts.vega(die.parse('2d6')))


class TestVegaScatter:
    def test_spec(self):
        spec = die.charts.vega_scatter(stat_of([4, 2, 6]))
        assert spec['mark'] == 'point'
        assert spec['data']['values'] == [
            {'roll': 1, 'value': 4},
            {'roll': 2, 'value': 2},
            {'roll': 3, 'value': 6},
        ]

    def test_non_statistic_raises(self):
        with pytest.raises(TypeError, match='needs a Statistic'):
            die.charts.vega_scatter(die.d6)

    def test_json_serializable(self):
        json.dumps(die.charts.vega_scatter(stat_of([1, 2, 3])))


class TestVegaCompare:
    def test_layers_observed_and_theoretical(self):
        stat = Statistic(die.Roll((die.Standard(1),))).run(3)
        spec = die.charts.vega_compare(stat)
        observed, theoretical = spec['layer']
        assert observed['mark'] == 'bar'
        assert observed['encoding']['color']['datum'] == 'observed'
        assert observed['data']['values'] == [{'value': 1, 'probability': 1.0}]
        assert theoretical['mark'] == {'type': 'line', 'point': True}
        assert theoretical['encoding']['color']['datum'] == 'theoretical'
        assert theoretical['data']['values'] == [{'value': 1, 'probability': 1.0}]

    def test_non_statistic_raises(self):
        with pytest.raises(TypeError, match='needs a Statistic'):
            die.charts.vega_compare(die.parse('3d6'))

    def test_json_serializable(self):
        stat = Statistic(die.parse('2d4')).run(20)
        json.dumps(die.charts.vega_compare(stat))
