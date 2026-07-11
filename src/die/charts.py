"""Chart dice probabilities and rolled results.

ASCII charts (``histogram``, ``scatter``) return multi-line strings for terminals.
Vega-Lite emitters (``vega``, ``vega_scatter``, ``vega_compare``) return spec dicts;
``json.dumps()`` one and render it with any Vega-Lite tool (https://vega.github.io/editor,
VSCode, JupyterLab, ``vl-convert`` for PNG/SVG).

Chart functions take a ``Roll`` or ``Die`` (theoretical probabilities, from ``odds``)
or a ``Statistic`` (observed frequencies, from a simulation)::

    die.charts.histogram(die.parse('3d6'))                     # theoretical curve
    die.charts.histogram(die.Statistic(die.d3d6).run(10_000))  # observed
"""

from .die import Die
from .rolls import Roll
from .stats import Statistic

_SCHEMA = 'https://vega.github.io/schema/vega-lite/v5.json'
# Eighth-width block characters, for smooth ASCII bar ends.
_BLOCKS = ('', '▏', '▎', '▍', '▌', '▋', '▊', '▉')


def _points(source):
    """List of ``Odds(value, ways, probability)`` charted for ``source``.

    ``Statistic`` charts observed ``frequencies``; ``Roll`` and ``Die`` chart
    theoretical ``odds``.

    :raises TypeError: If source is not a Statistic, Roll, or Die.
    :raises ValueError: If source has nothing to chart (empty Roll).
    :raises RuntimeError: If source is a Statistic whose ``run()`` hasn't been called.
    """
    if isinstance(source, Statistic):
        points = source.frequencies
    elif isinstance(source, Roll):
        points = source.odds
    elif isinstance(source, Die):
        points = source._as_roll().odds
    else:
        raise TypeError(f"cannot chart '{type(source).__name__}'")
    if not points:
        raise ValueError('nothing to chart: Roll of no dice')
    return points


def _title(source):
    """Chart title for ``source``: its notation, plus roll count for a Statistic."""
    if isinstance(source, Statistic):
        return f'{source.roll.notation}, {source.count} rolls'
    return source.notation


def histogram(source, width=60):
    """ASCII bar chart of probability per value: the probability curve of ``source``.

    One line per distinct value: value, bar, percent. Bars scale so the most
    probable value spans ``width`` characters.

    :param source: Statistic (observed), or Roll/Die (theoretical).
    :param width: [60] Character width of the longest bar.
    :return: Multi-line string, no trailing newline.
    :raises ValueError: If width < 1, or source has nothing to chart.
    :raises TypeError: If source is not a Statistic, Roll, or Die.
    """
    if width < 1:
        raise ValueError(f'width must be >= 1, got {width!r}')
    points = _points(source)
    peak = max(point.probability for point in points)
    label_width = max(len(str(point.value)) for point in points)
    lines = list()
    for value, _, probability in points:
        eighths = round(probability / peak * width * 8)
        bar = '█' * (eighths // 8) + _BLOCKS[eighths % 8]
        lines.append(f'{value!s:>{label_width}} {bar:<{width}} {probability:7.2%}')
    return '\n'.join(lines)


def scatter(stat, width=60, height=20):
    """ASCII scatter plot of a Statistic's rolled results: roll order (x) vs value (y).

    :param stat: ``Statistic`` whose ``run()`` has been called.
    :param width: [60] Plot width in characters.
    :param height: [20] Plot height in lines.
    :return: Multi-line string, no trailing newline.
    :raises TypeError: If stat is not a Statistic.
    :raises ValueError: If width or height < 1.
    :raises RuntimeError: If ``run()`` has not been called.
    """
    if not isinstance(stat, Statistic):
        raise TypeError(f"cannot scatter '{type(stat).__name__}'; scatter needs a Statistic")
    if width < 1 or height < 1:
        raise ValueError(f'width and height must be >= 1, got {width!r}x{height!r}')
    values = stat.values
    low, high = min(values), max(values)
    span = high - low
    grid = [[' '] * width for _ in range(height)]
    last_col = width - 1
    last_row = height - 1
    for index, value in enumerate(values):
        col = index * last_col // (len(values) - 1) if len(values) > 1 else 0
        row = last_row - round((value - low) / span * last_row) if span else last_row
        grid[row][col] = '·'
    gutter = max(len(str(high)), len(str(low)))
    lines = list()
    for row, cells in enumerate(grid):
        if row == 0:
            label = str(high)
        elif row == last_row:
            label = str(low)
        else:
            label = ''
        lines.append(f'{label:>{gutter}} │{"".join(cells)}')
    lines.append(f'{"":>{gutter}} └{"─" * width}')
    return '\n'.join(lines)


def vega(source, kind='bar'):
    """Vega-Lite spec of probability per value: the probability curve of ``source``.

    :param source: Statistic (observed), or Roll/Die (theoretical).
    :param kind: ['bar'] Mark type: 'bar' or 'line'.
    :return: Vega-Lite v5 spec dict, data inline.
    :raises ValueError: If kind is not 'bar' or 'line', or source has nothing to chart.
    :raises TypeError: If source is not a Statistic, Roll, or Die.
    """
    if kind not in ('bar', 'line'):
        raise ValueError(f"kind must be 'bar' or 'line', got {kind!r}")
    points = _points(source)
    return {
        '$schema': _SCHEMA,
        'title': _title(source),
        'data': {'values': [{'value': p.value, 'probability': p.probability} for p in points]},
        'mark': kind if kind == 'bar' else {'type': 'line', 'point': True},
        'encoding': {
            'x': {'field': 'value', 'type': 'ordinal' if kind == 'bar' else 'quantitative'},
            'y': {'field': 'probability', 'type': 'quantitative', 'axis': {'format': '.1%'}},
            'tooltip': [
                {'field': 'value', 'type': 'nominal'},
                {'field': 'probability', 'type': 'quantitative', 'format': '.2%'},
            ],
        },
    }


def vega_scatter(stat):
    """Vega-Lite scatter spec of a Statistic's rolled results: roll order (x) vs value (y).

    :param stat: ``Statistic`` whose ``run()`` has been called.
    :return: Vega-Lite v5 spec dict, data inline.
    :raises TypeError: If stat is not a Statistic.
    :raises RuntimeError: If ``run()`` has not been called.
    """
    if not isinstance(stat, Statistic):
        raise TypeError(f"cannot scatter '{type(stat).__name__}'; vega_scatter needs a Statistic")
    return {
        '$schema': _SCHEMA,
        'title': _title(stat),
        'data': {
            'values': [{'roll': i, 'value': v} for i, v in enumerate(stat.values, start=1)],
        },
        'mark': 'point',
        'encoding': {
            'x': {'field': 'roll', 'type': 'quantitative'},
            'y': {'field': 'value', 'type': 'quantitative'},
            'tooltip': [
                {'field': 'roll', 'type': 'quantitative'},
                {'field': 'value', 'type': 'quantitative'},
            ],
        },
    }


def vega_compare(stat):
    """Vega-Lite spec overlaying observed frequencies (bars) with theoretical odds (line).

    Note ``Roll.odds`` is computed from face values, so the theoretical line is wrong
    for dice whose rolls don't come straight from their faces (``Exploding``,
    ``Rerolling``); the observed bars show the real distribution.

    :param stat: ``Statistic`` whose ``run()`` has been called.
    :return: Layered Vega-Lite v5 spec dict, data inline.
    :raises TypeError: If stat is not a Statistic.
    :raises RuntimeError: If ``run()`` has not been called.
    """
    if not isinstance(stat, Statistic):
        raise TypeError(f"cannot compare '{type(stat).__name__}'; vega_compare needs a Statistic")
    observed = stat.frequencies
    theoretical = stat.roll.odds

    def layer(points, mark, series):
        return {
            'data': {
                'values': [{'value': p.value, 'probability': p.probability} for p in points],
            },
            'mark': mark,
            'encoding': {
                'x': {'field': 'value', 'type': 'ordinal'},
                'y': {'field': 'probability', 'type': 'quantitative', 'axis': {'format': '.1%'}},
                'color': {'datum': series, 'legend': {'title': None}},
                'tooltip': [
                    {'field': 'value', 'type': 'nominal'},
                    {'field': 'probability', 'type': 'quantitative', 'format': '.2%'},
                ],
            },
        }

    return {
        '$schema': _SCHEMA,
        'title': _title(stat),
        'layer': [
            layer(observed, 'bar', 'observed'),
            layer(theoretical, {'type': 'line', 'point': True}, 'theoretical'),
        ],
    }
