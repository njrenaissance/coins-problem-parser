"""Command-line tool: parse a fake-coin solution and optionally evaluate it.

Usage::

    python -m fakecoin path/to/solution.txt            # parse and summarise
    python -m fakecoin path/to/solution.txt --evaluate  # also check all worlds

This module is the system boundary, so it is the one place that catches
:class:`FakeCoinError` broadly and turns it into an exit code; unexpected
exceptions are left to propagate. Its ``print`` calls are the tool's final
human-facing output, which is the one use of ``print`` the logging standard
allows.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .ast_nodes import Conclusion, Fake, Strategy
from .errors import FakeCoinError
from .evaluator import Report, coins_in, depth, solves_all
from .parser import parse


def main(argv: list[str] | None = None) -> int:
    """Parse the requested file and return a process exit code."""
    args = _parse_args(argv)
    try:
        source = Path(args.file).read_text(encoding="utf-8")
    except OSError as error:
        print(f"error: cannot read {args.file}: {error}", file=sys.stderr)
        return 1
    try:
        strategy = parse(source)
    except FakeCoinError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    _print_summary(strategy)
    if args.evaluate:
        return _report(solves_all(strategy))
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="fakecoin",
        description="Parse and check fake-coin DSL solutions.",
    )
    parser.add_argument("file", help="path to a solution written in the fake-coin DSL")
    parser.add_argument(
        "--evaluate",
        action="store_true",
        help="check the solution against every fake-coin world",
    )
    return parser.parse_args(argv)


def _print_summary(strategy: Strategy) -> None:
    coins = coins_in(strategy)
    print(f"Parsed OK: {len(coins)} coins, up to {depth(strategy)} weighings deep.")


def _report(report: Report) -> int:
    total = len(report.results)
    if report.solved:
        print(f"Solves all {total} worlds.")
        return 0
    failures = report.failures
    print(f"FAILS: {len(failures)} of {total} worlds unresolved:", file=sys.stderr)
    for result in failures:
        world = result.world
        print(
            f"  coin {world.coin} {world.direction.value}: got {_describe(result.verdict)}",
            file=sys.stderr,
        )
    return 1


def _describe(verdict: Conclusion) -> str:
    if isinstance(verdict, Fake):
        return f"fake({verdict.coin},{verdict.direction.value})"
    return "genuine"
