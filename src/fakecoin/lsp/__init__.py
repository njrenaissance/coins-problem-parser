"""LSP language server for the fake-coin DSL.

Requires the optional ``lsp`` extra (``pip install 'recursive-parser[lsp]'``),
which pulls in pygls. Importing this sub-package without pygls installed raises
``ImportError`` — the core ``fakecoin`` parser has no such dependency.
"""

from __future__ import annotations

from .features import KEYWORDS, completion_items, diagnostics_for
from .server import create_server, main

__all__ = [
    "KEYWORDS",
    "completion_items",
    "create_server",
    "diagnostics_for",
    "main",
]
