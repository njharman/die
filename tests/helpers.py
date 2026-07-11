class StubRng:
    """Deterministic rng: choice returns face at fixed index, choices repeats it."""

    def __init__(self, index=0):
        self.index = index

    def choice(self, seq):
        return seq[self.index]

    def choices(self, seq, k=1):
        return [seq[self.index]] * k


class SequenceRng:
    """Deterministic rng: choice returns the face matching the next value in a fixed sequence."""

    def __init__(self, values):
        self.values = list(values)

    def choice(self, seq):
        value = self.values.pop(0)
        for face in seq:
            if face[1] == value:
                return face
        raise ValueError(f'{value} not in {seq}')


class FakeRoll:
    """Test double satisfying the interface Statistic needs from a Roll:
    ``numeric``, ``roll(count, func)``, and ``notation``. Lets statistics and
    charts be asserted against fixed values instead of real dice randomness.
    """

    notation = 'fake'

    def __init__(self, rolls, numeric=True):
        self.numeric = numeric
        self._rolls = list(rolls)

    def roll(self, count, func=sum):
        return func(self._rolls)
