"""Tests for the DSL lexer."""

import pytest

from fakecoin.errors import LexError
from fakecoin.lexer import tokenize
from fakecoin.tokens import TokenType

pytestmark = pytest.mark.unit

T = TokenType

_FIRST_TOKEN_COLUMN = 3  # "fake" starts after two leading spaces


def _types(source: str) -> list[TokenType]:
    return [token.type for token in tokenize(source)]


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        pytest.param("genuine", [T.GENUINE, T.EOF], id="genuine"),
        pytest.param(
            "fake(3,heavier)",
            [T.FAKE, T.LPAREN, T.INT, T.COMMA, T.HEAVIER, T.RPAREN, T.EOF],
            id="fake_conclusion",
        ),
        pytest.param("{1,2}", [T.LBRACE, T.INT, T.COMMA, T.INT, T.RBRACE, T.EOF], id="pan"),
        pytest.param("left> balance right>", [T.LEFT, T.BALANCE, T.RIGHT, T.EOF], id="branch_labels"),
        pytest.param("(* skip me *) genuine", [T.GENUINE, T.EOF], id="comment_skipped"),
        pytest.param("weigh vs", [T.WEIGH, T.VS, T.EOF], id="weigh_vs"),
    ],
)
def test_tokenizes_to_expected_types(source, expected):
    assert _types(source) == expected


def test_position_is_tracked_past_whitespace():
    first = tokenize("  fake")[0]
    assert first.type is T.FAKE
    assert first.line == 1
    assert first.column == _FIRST_TOKEN_COLUMN


@pytest.mark.parametrize(
    "source",
    [
        pytest.param("@", id="unknown_character"),
        pytest.param("(* unterminated", id="unterminated_comment"),
        pytest.param("left", id="label_without_gt"),
        pytest.param("wobble", id="unknown_keyword"),
    ],
)
def test_rejects_bad_input(source):
    with pytest.raises(LexError):
        tokenize(source)
