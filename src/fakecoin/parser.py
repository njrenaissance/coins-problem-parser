"""Recursive-descent parser for the fake-coin DSL.

Each grammar production maps to one method: :meth:`Parser._strategy`,
:meth:`Parser._weighing`, :meth:`Parser._pan`, and :meth:`Parser._conclusion`.
The optional ``max_weighings`` budget models the grammar's ``strategy<k>``
parameter — once it reaches zero, only a conclusion is allowed.
"""

from __future__ import annotations

from .ast_nodes import Conclusion, Direction, Fake, Genuine, Strategy, Weighing
from .errors import ParseError
from .lexer import tokenize
from .tokens import Token, TokenType

# The three outcome branches every weighing must define exactly once. The
# grammar writes them left>/balance/right>, but real solutions order them
# freely, so the parser accepts any order and only requires all three present.
_BRANCH_LABELS: tuple[TokenType, ...] = (TokenType.LEFT, TokenType.BALANCE, TokenType.RIGHT)


class Parser:
    """Builds a :class:`Strategy` AST from a token stream."""

    def __init__(self, tokens: list[Token], max_weighings: int | None = None) -> None:
        self._tokens = tokens
        self._index = 0
        self._max_weighings = max_weighings

    def parse(self) -> Strategy:
        """Parse a whole solution and require the input to end afterwards."""
        strategy = self._strategy(self._max_weighings)
        self._expect(TokenType.EOF)
        return strategy

    def _strategy(self, remaining: int | None) -> Strategy:
        if self._peek().type != TokenType.WEIGH:
            return self._conclusion()
        if remaining is not None and remaining <= 0:
            token = self._peek()
            raise ParseError("weighing exceeds the allowed budget", token.line, token.column)
        deeper = None if remaining is None else remaining - 1
        return self._weighing(deeper)

    def _weighing(self, remaining: int | None) -> Weighing:
        self._expect(TokenType.WEIGH)
        self._expect(TokenType.LPAREN)
        left = self._pan()
        self._expect(TokenType.VS)
        right = self._pan()
        self._expect(TokenType.RPAREN)
        self._expect(TokenType.LBRACE)
        branches = self._branches(remaining)
        self._expect(TokenType.RBRACE)
        return Weighing(
            left,
            right,
            branches[TokenType.LEFT],
            branches[TokenType.BALANCE],
            branches[TokenType.RIGHT],
        )

    def _branches(self, remaining: int | None) -> dict[TokenType, Strategy]:
        parsed: dict[TokenType, Strategy] = {}
        for _ in _BRANCH_LABELS:
            label = self._branch_label(parsed)
            self._expect(TokenType.COLON)
            parsed[label] = self._strategy(remaining)
            self._expect(TokenType.SEMICOLON)
        return parsed

    def _branch_label(self, parsed: dict[TokenType, Strategy]) -> TokenType:
        token = self._peek()
        if token.type not in _BRANCH_LABELS:
            raise ParseError(
                "expected a branch label (left>, balance, or right>)",
                token.line,
                token.column,
            )
        if token.type in parsed:
            raise ParseError(f"duplicate branch label {token.lexeme!r}", token.line, token.column)
        return self._advance().type

    def _pan(self) -> frozenset[int]:
        self._expect(TokenType.LBRACE)
        coins = [self._coin()]
        while self._peek().type == TokenType.COMMA:
            self._advance()
            coins.append(self._coin())
        self._expect(TokenType.RBRACE)
        return frozenset(coins)

    def _conclusion(self) -> Conclusion:
        if self._peek().type == TokenType.GENUINE:
            self._advance()
            return Genuine()
        self._expect(TokenType.FAKE)
        self._expect(TokenType.LPAREN)
        coin = self._coin()
        self._expect(TokenType.COMMA)
        direction = self._direction()
        self._expect(TokenType.RPAREN)
        return Fake(coin, direction)

    def _direction(self) -> Direction:
        token = self._peek()
        if token.type == TokenType.HEAVIER:
            self._advance()
            return Direction.HEAVIER
        if token.type == TokenType.LIGHTER:
            self._advance()
            return Direction.LIGHTER
        raise ParseError("expected a direction (heavier or lighter)", token.line, token.column)

    def _coin(self) -> int:
        return int(self._expect(TokenType.INT).lexeme)

    def _peek(self) -> Token:
        return self._tokens[self._index]

    def _advance(self) -> Token:
        token = self._tokens[self._index]
        self._index += 1
        return token

    def _expect(self, token_type: TokenType) -> Token:
        token = self._peek()
        if token.type != token_type:
            raise ParseError(
                f"expected {token_type.name} but found {token.type.name}",
                token.line,
                token.column,
            )
        return self._advance()


def parse(text: str, max_weighings: int | None = None) -> Strategy:
    """Tokenize and parse ``text`` into a :class:`Strategy` AST."""
    return Parser(tokenize(text), max_weighings).parse()
