"""Abstract syntax tree for a parsed fake-coin strategy.

A strategy is a decision tree: each internal node is a :class:`Weighing` with
three labelled branches (one per balance outcome), and each leaf is a
:class:`Conclusion` — either a :class:`Fake` verdict or :class:`Genuine`.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Direction(Enum):
    """Which way the fake coin deviates from a genuine one."""

    HEAVIER = "heavier"
    LIGHTER = "lighter"


@dataclass(frozen=True)
class Fake:
    """A verdict naming the fake coin and how it deviates."""

    coin: int
    direction: Direction


@dataclass(frozen=True)
class Genuine:
    """A verdict that no fake is present (all coins genuine)."""


@dataclass(frozen=True)
class Weighing:
    """One weighing of two pans, with a sub-strategy per outcome.

    ``on_left`` is taken when the left pan reads heavier, ``on_right`` when the
    right pan reads heavier, and ``on_balance`` when the pans balance.
    """

    left: frozenset[int]
    right: frozenset[int]
    on_left: Strategy
    on_balance: Strategy
    on_right: Strategy


Conclusion = Fake | Genuine
Strategy = Weighing | Conclusion
