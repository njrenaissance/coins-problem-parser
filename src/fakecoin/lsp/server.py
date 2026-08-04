"""pygls server wiring: connect editor events to the pure feature logic.

This module is deliberately thin — it registers handlers and delegates every
decision to :mod:`fakecoin.lsp.features`, which is where the testable logic lives.
"""

from __future__ import annotations

from lsprotocol import types
from pygls.server import LanguageServer

from .features import completion_items, diagnostics_for

_SERVER_NAME = "fakecoin-lsp"
_SERVER_VERSION = "v0.1"


def create_server() -> LanguageServer:
    """Build a language server for the fake-coin DSL with its features registered."""
    server = LanguageServer(_SERVER_NAME, _SERVER_VERSION)

    @server.feature(types.TEXT_DOCUMENT_DID_OPEN)
    def did_open(ls: LanguageServer, params: types.DidOpenTextDocumentParams) -> None:
        _publish_diagnostics(ls, params.text_document.uri)

    @server.feature(types.TEXT_DOCUMENT_DID_CHANGE)
    def did_change(ls: LanguageServer, params: types.DidChangeTextDocumentParams) -> None:
        _publish_diagnostics(ls, params.text_document.uri)

    # pygls calls the handler with (ls, params); static keyword completion needs neither.
    @server.feature(types.TEXT_DOCUMENT_COMPLETION)
    def completion(ls: LanguageServer, params: types.CompletionParams) -> types.CompletionList:  # noqa: ARG001
        return types.CompletionList(is_incomplete=False, items=completion_items())

    return server


def _publish_diagnostics(ls: LanguageServer, uri: str) -> None:
    document = ls.workspace.get_text_document(uri)
    ls.publish_diagnostics(uri, diagnostics_for(document.source))


def main() -> None:
    """Console-script / ``python -m`` entry point: serve over stdio."""
    create_server().start_io()
