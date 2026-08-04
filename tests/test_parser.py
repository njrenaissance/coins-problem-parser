"""Tests for the recursive-descent parser."""

import pytest

from fakecoin import Direction, Fake, Genuine, Weighing, parse
from fakecoin.errors import ParseError

pytestmark = pytest.mark.unit

WEIGHING = "weigh({1} vs {2}){ left>: fake(1,heavier); balance: genuine; right>: fake(2,lighter); }"
REORDERED = "weigh({1} vs {2}){ balance: genuine; right>: fake(2,lighter); left>: fake(1,heavier); }"
NESTED = (
    "weigh({1} vs {2}){"
    " left>: weigh({1} vs {2}){ left>: genuine; balance: genuine; right>: genuine; };"
    " balance: genuine;"
    " right>: genuine; }"
)

_BUDGET_CONCLUSION_ONLY = 0
_BUDGET_ONE_WEIGHING = 1


def _expected_weighing() -> Weighing:
    return Weighing(
        frozenset({1}),
        frozenset({2}),
        on_left=Fake(1, Direction.HEAVIER),
        on_balance=Genuine(),
        on_right=Fake(2, Direction.LIGHTER),
    )


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        pytest.param("genuine", Genuine(), id="genuine"),
        pytest.param("fake(5,lighter)", Fake(5, Direction.LIGHTER), id="fake"),
    ],
)
def test_parses_conclusions(source, expected):
    assert parse(source) == expected


def test_parses_weighing():
    assert parse(WEIGHING) == _expected_weighing()


def test_branch_order_does_not_matter():
    assert parse(REORDERED) == _expected_weighing()


@pytest.mark.parametrize(
    "source",
    [
        pytest.param(
            "weigh({1} vs {2}){ left>: genuine balance: genuine; right>: genuine; }",
            id="missing_semicolon",
        ),
        pytest.param(
            "weigh({1} vs {2}){ left>: genuine; left>: genuine; right>: genuine; }",
            id="duplicate_branch",
        ),
        pytest.param(
            "weigh({1} vs {2}){ left>: genuine; balance: genuine; }",
            id="missing_branch",
        ),
        pytest.param("fake(3,genuine)", id="bad_direction"),
        pytest.param("genuine genuine", id="trailing_tokens"),
        pytest.param(
            "weigh({} vs {2}){ left>: genuine; balance: genuine; right>: genuine; }",
            id="empty_pan",
        ),
    ],
)
def test_rejects_malformed_input(source):
    with pytest.raises(ParseError):
        parse(source)


def test_budget_allows_weighing_within_limit():
    assert parse(WEIGHING, max_weighings=_BUDGET_ONE_WEIGHING) == _expected_weighing()


@pytest.mark.parametrize(
    ("source", "budget"),
    [
        pytest.param(WEIGHING, _BUDGET_CONCLUSION_ONLY, id="conclusion_only_budget"),
        pytest.param(NESTED, _BUDGET_ONE_WEIGHING, id="nested_exceeds_budget"),
    ],
)
def test_budget_rejects_too_many_weighings(source, budget):
    with pytest.raises(ParseError):
        parse(source, max_weighings=budget)
