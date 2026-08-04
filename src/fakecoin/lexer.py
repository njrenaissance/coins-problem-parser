"""Lexer: turn DSL source text into a flat list of tokens.

Whitespace and ``(* ... *)`` comments are discarded. Multi-character branch
labels (``left>`` / ``right>``) and keywords are recognised as single tokens.
"""

from __future__ import annotations

from .errors import LexError
from .tokens import Token, TokenType

_KEYWORDS: dict[str, TokenType] = {
    "weigh": TokenType.WEIGH,
    "vs": TokenType.VS,
    "fake": TokenType.FAKE,
    "genuine": TokenType.GENUINE,
    "heavier": TokenType.HEAVIER,
    "lighter": TokenType.LIGHTER,
    "balance": TokenType.BALANCE,
    "left>": TokenType.LEFT,
    "right>": TokenType.RIGHT,
}

_SYMBOLS: dict[str, TokenType] = {
    "(": TokenType.LPAREN,
    ")": TokenType.RPAREN,
    "{": TokenType.LBRACE,
    "}": TokenType.RBRACE,
    ",": TokenType.COMMA,
    ":": TokenType.COLON,
    ";": TokenType.SEMICOLON,
}

_WHITESPACE = " \t\r\n"


class Lexer:
    """Scans a source string once, producing tokens with source positions."""

    def __init__(self, source: str) -> None:
        self._source = source
        self._pos = 0
        self._line = 1
        self._col = 1

    def tokenize(self) -> list[Token]:
        """Return every token in the source, terminated by an ``EOF`` token."""
        tokens: list[Token] = []
        while not self._at_end():
            char = self._current()
            if char in _WHITESPACE:
                self._advance()
            elif char == "(" and self._peek_next() == "*":
                self._skip_comment()
            elif char.isdigit():
                tokens.append(self._number())
            elif char.isalpha():
                tokens.append(self._word())
            else:
                tokens.append(self._symbol())
        tokens.append(Token(TokenType.EOF, "", self._line, self._col))
        return tokens

    def _at_end(self) -> bool:
        return self._pos >= len(self._source)

    def _current(self) -> str:
        return self._source[self._pos]

    def _peek_next(self) -> str:
        following = self._pos + 1
        return self._source[following] if following < len(self._source) else ""

    def _advance(self) -> str:
        char = self._source[self._pos]
        self._pos += 1
        if char == "\n":
            self._line += 1
            self._col = 1
        else:
            self._col += 1
        return char

    def _skip_comment(self) -> None:
        start_line, start_col = self._line, self._col
        self._advance()  # "("
        self._advance()  # "*"
        while not self._at_end():
            if self._current() == "*" and self._peek_next() == ")":
                self._advance()  # "*"
                self._advance()  # ")"
                return
            self._advance()
        raise LexError("unterminated comment", start_line, start_col)

    def _number(self) -> Token:
        line, col = self._line, self._col
        start = self._pos
        while not self._at_end() and self._current().isdigit():
            self._advance()
        return Token(TokenType.INT, self._source[start : self._pos], line, col)

    def _word(self) -> Token:
        line, col = self._line, self._col
        start = self._pos
        while not self._at_end() and self._current().isalpha():
            self._advance()
        lexeme = self._source[start : self._pos]
        if not self._at_end() and self._current() == ">":
            self._advance()
            lexeme += ">"
        token_type = _KEYWORDS.get(lexeme)
        if token_type is None:
            raise LexError(f"unknown keyword {lexeme!r}", line, col)
        return Token(token_type, lexeme, line, col)

    def _symbol(self) -> Token:
        line, col = self._line, self._col
        char = self._current()
        token_type = _SYMBOLS.get(char)
        if token_type is None:
            raise LexError(f"unexpected character {char!r}", line, col)
        self._advance()
        return Token(token_type, char, line, col)


def tokenize(source: str) -> list[Token]:
    """Convenience wrapper: tokenize ``source`` in one call."""
    return Lexer(source).tokenize()
