#!/usr/bin/env python
"""Run every demo: demo_die.py, demo_rolls.py, demo_stats.py."""

import pathlib
import runpy

for name in ('demo_die.py', 'demo_rolls.py', 'demo_stats.py'):
    print(f'──── {name} ────')
    runpy.run_path(str(pathlib.Path(__file__).parent / name))
    print()
