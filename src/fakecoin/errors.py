"""Exception hierarchy for the fake-coin DSL.

All failures raised by this package descend from :class:`FakeCoinError`, so a
caller can catch one failure mode without swallowing unrelated ones. Lexing and
parsing errors carry the source position that triggered them.
"""

from __future__ import annotations


class FakeCoinError(Exception):
    """Base class for every error raised by this package."""


class SourceError(FakeCoinError):
    """A failure tied to a position in the source text.

    Line and column are 1-based to match how editors report positions.
    """

    def __init__(self, message: str, line: int, column: int) -> None:
        super().__init__(f"{message} (line {line}, column {column})")
        self.raw_message = message
        self.line = line
        self.column = column


class LexError(SourceError):
    """The lexer encountered a character it cannot tokenize."""


class ParseError(SourceError):
    """The token stream does not conform to the grammar."""
