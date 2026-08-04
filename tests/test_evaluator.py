"""The evaluation harness: run the sample solution against every fake-coin world.

The headline test parametrizes over all ``2N`` worlds so a failing world reads
as its own named case (e.g. ``coin7-lighter``) rather than a single opaque
failure. This is the "does the solution solve every case" gate.
"""

import pytest

from fakecoin import (
    Direction,
    Fake,
    Genuine,
    World,
    all_worlds,
    coins_in,
    depth,
    parse,
    simulate,
    solves_all,
)

pytestmark = pytest.mark.unit

_COIN_COUNT = 12
_WORLD_COUNT = 2 * _COIN_COUNT
_SAMPLE_DEPTH = 3

SAMPLE_COINS = frozenset(range(1, _COIN_COUNT + 1))
WORLDS = all_worlds(SAMPLE_COINS)


def _world_id(world: World) -> str:
    return f"coin{world.coin}-{world.direction.value}"


def test_coin_set_is_inferred_from_the_solution(sample_strategy):
    assert coins_in(sample_strategy) == SAMPLE_COINS


def test_there_are_two_worlds_per_coin(sample_strategy):
    assert len(all_worlds(coins_in(sample_strategy))) == _WORLD_COUNT


def test_sample_is_three_weighings_deep(sample_strategy):
    assert depth(sample_strategy) == _SAMPLE_DEPTH


@pytest.mark.parametrize("world", WORLDS, ids=_world_id)
def test_sample_resolves_every_world(sample_strategy, world):
    assert simulate(sample_strategy, world) == Fake(world.coin, world.direction)


@pytest.mark.parametrize("world", WORLDS, ids=_world_id)
def test_no_world_is_declared_genuine(sample_strategy, world):
    assert not isinstance(simulate(sample_strategy, world), Genuine)


def test_solves_all_reports_success(sample_strategy):
    report = solves_all(sample_strategy)
    assert report.solved
    assert report.failures == ()
    assert len(report.results) == _WORLD_COUNT


def test_solves_all_flags_a_broken_solution():
    broken = parse("fake(1,heavier)")  # only correct when coin 1 is the heavy fake
    report = solves_all(broken)
    assert report.solved is False
    failed_worlds = {result.world for result in report.failures}
    assert World(1, Direction.LIGHTER) in failed_worlds
