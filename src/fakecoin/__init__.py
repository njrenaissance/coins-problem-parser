"""Recursive-descent parser and evaluator for the fake-coin DSL.

Public API::

    from fakecoin import parse, solves_all
    strategy = parse(source_text)
    report = solves_all(strategy)
    assert report.solved
"""

from __future__ import annotations

from .ast_nodes import Conclusion, Direction, Fake, Genuine, Strategy, Weighing
from .errors import FakeCoinError, LexError, ParseError, SourceError
from .evaluator import (
    Report,
    World,
    WorldResult,
    all_worlds,
    coins_in,
    depth,
    simulate,
    solves_all,
)
from .parser import parse

__all__ = [
    "Conclusion",
    "Direction",
    "Fake",
    "FakeCoinError",
    "Genuine",
    "LexError",
    "ParseError",
    "Report",
    "SourceError",
    "Strategy",
    "Weighing",
    "World",
    "WorldResult",
    "all_worlds",
    "coins_in",
    "depth",
    "parse",
    "simulate",
    "solves_all",
]
