"""Evaluate a parsed strategy against every possible fake-coin world.

Exactly one coin is fake and it is either heavier or lighter, so a coin set of
size N yields ``2N`` worlds. :func:`solves_all` walks the strategy for each world
and reports whether every one resolves to the correct ``fake(...)`` verdict.

Weights are computed with :class:`fractions.Fraction` so the fake's deviation is
an exact fraction of a coin: a genuine-count difference between the pans always
dominates the fake's contribution, and equal-size pans balance unless the fake
is on one of them. No floating-point rounding is involved.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from .ast_nodes import Conclusion, Direction, Fake, Genuine, Strategy, Weighing

# A genuine coin weighs 1; the fake deviates by half a coin. Any value in the
# open interval (0, 1) works — one half keeps the arithmetic exact and readable.
_FAKE_DELTA = Fraction(1, 2)


@dataclass(frozen=True)
class World:
    """One hypothesis: ``coin`` is the fake and deviates in ``direction``."""

    coin: int
    direction: Direction


@dataclass(frozen=True)
class WorldResult:
    """The outcome of running a strategy against a single world."""

    world: World
    verdict: Conclusion
    expected: Fake
    solved: bool


@dataclass(frozen=True)
class Report:
    """The aggregate outcome across every world for one strategy."""

    results: tuple[WorldResult, ...]

    @property
    def solved(self) -> bool:
        """True when every world resolved to its correct verdict."""
        return all(result.solved for result in self.results)

    @property
    def failures(self) -> tuple[WorldResult, ...]:
        """The worlds whose verdict did not match the expected fake coin."""
        return tuple(result for result in self.results if not result.solved)


def coins_in(strategy: Strategy) -> frozenset[int]:
    """Return every coin label mentioned anywhere in the strategy."""
    if isinstance(strategy, Weighing):
        nested = coins_in(strategy.on_left) | coins_in(strategy.on_balance) | coins_in(strategy.on_right)
        return strategy.left | strategy.right | nested
    if isinstance(strategy, Fake):
        return frozenset({strategy.coin})
    return frozenset()  # Genuine mentions no specific coin.


def all_worlds(coins: frozenset[int]) -> list[World]:
    """Enumerate the ``2N`` worlds: each coin, heavier and lighter."""
    return [World(coin, direction) for coin in sorted(coins) for direction in Direction]


def depth(strategy: Strategy) -> int:
    """Return the maximum number of weighings on any path through the tree."""
    if isinstance(strategy, Weighing):
        branches = (strategy.on_left, strategy.on_balance, strategy.on_right)
        return 1 + max(depth(branch) for branch in branches)
    return 0


def simulate(strategy: Strategy, world: World) -> Conclusion:
    """Walk the strategy under ``world`` and return the conclusion reached."""
    node: Strategy = strategy
    while isinstance(node, Weighing):
        node = _branch_for(node, world)
    return node


def solves_all(strategy: Strategy) -> Report:
    """Run ``strategy`` against every world and collect a :class:`Report`."""
    results = []
    for world in all_worlds(coins_in(strategy)):
        expected = Fake(world.coin, world.direction)
        verdict = simulate(strategy, world)
        results.append(WorldResult(world, verdict, expected, verdict == expected))
    return Report(tuple(results))


def _branch_for(weighing: Weighing, world: World) -> Strategy:
    left = _pan_weight(weighing.left, world)
    right = _pan_weight(weighing.right, world)
    if left > right:
        return weighing.on_left
    if left < right:
        return weighing.on_right
    return weighing.on_balance


def _pan_weight(pan: frozenset[int], world: World) -> Fraction:
    weight = Fraction(len(pan))
    if world.coin in pan:
        weight += _FAKE_DELTA if world.direction is Direction.HEAVIER else -_FAKE_DELTA
    return weight


__all__ = [
    "Genuine",
    "Report",
    "World",
    "WorldResult",
    "all_worlds",
    "coins_in",
    "depth",
    "simulate",
    "solves_all",
]
