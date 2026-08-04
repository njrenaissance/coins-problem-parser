"""Token definitions shared by the lexer and parser."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    """The kinds of token the lexer can emit."""

    WEIGH = auto()
    VS = auto()
    FAKE = auto()
    GENUINE = auto()
    HEAVIER = auto()
    LIGHTER = auto()
    LEFT = auto()  # the "left>" branch label
    BALANCE = auto()  # the "balance" branch label
    RIGHT = auto()  # the "right>" branch label
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    COMMA = auto()
    COLON = auto()
    SEMICOLON = auto()
    INT = auto()
    EOF = auto()


@dataclass(frozen=True)
class Token:
    """A lexeme tagged with its type and 1-based source position."""

    type: TokenType
    lexeme: str
    line: int
    column: int
