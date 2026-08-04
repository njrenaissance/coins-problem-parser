"""Pure LSP feature logic — diagnostics and completion — with no server involved.

These functions turn DSL source text into `lsprotocol` values, so they can be
unit-tested directly without standing up a language server.
"""

from __future__ import annotations

from lsprotocol import types

from ..errors import SourceError
from ..parser import parse

# The DSL's keywords, offered to the editor as completions.
KEYWORDS: tuple[str, ...] = (
    "weigh",
    "vs",
    "fake",
    "genuine",
    "heavier",
    "lighter",
    "left>",
    "balance",
    "right>",
)


def diagnostics_for(text: str) -> list[types.Diagnostic]:
    """Report any lex/parse error in ``text`` as a single diagnostic.

    An empty list means the text parsed cleanly, which tells the editor to clear
    any diagnostics it was showing.
    """
    try:
        parse(text)
    except SourceError as error:
        return [_diagnostic(error)]
    return []


def completion_items() -> list[types.CompletionItem]:
    """Return the DSL keywords as completion items."""
    return [types.CompletionItem(label=keyword, kind=types.CompletionItemKind.Keyword) for keyword in KEYWORDS]


def _diagnostic(error: SourceError) -> types.Diagnostic:
    # The parser reports 1-based line/column; LSP positions are 0-based.
    line = error.line - 1
    start = types.Position(line=line, character=max(error.column - 1, 0))
    end = types.Position(line=line, character=error.column)
    return types.Diagnostic(
        range=types.Range(start=start, end=end),
        message=error.raw_message,
        severity=types.DiagnosticSeverity.Error,
        source="fakecoin",
    )
