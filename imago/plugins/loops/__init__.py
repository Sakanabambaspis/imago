"""Loops: how one user turn becomes one reply. The A/B switch lives here."""

from .plain import PlainLoop
from .stance import StanceLoop

LOOPS = {loop.name: loop for loop in (PlainLoop, StanceLoop)}
