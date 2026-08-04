"""Tests for the LSP feature logic (diagnostics and completion)."""

import pytest
from lsprotocol import types
from pygls.server import LanguageServer

from fakecoin.lsp import KEYWORDS, completion_items, create_server, diagnostics_for
from fakecoin.lsp import server as lsp_server

pytestmark = pytest.mark.unit


def test_valid_source_has_no_diagnostics(sample_path):
    assert diagnostics_for(sample_path.read_text(encoding="utf-8")) == []


@pytest.mark.parametrize(
    ("source", "line", "start_char", "end_char"),
    [
        pytest.param("  @", 0, 2, 3, id="column_offset"),
        pytest.param("genuine\n@", 1, 0, 1, id="second_line"),
    ],
)
def test_malformed_source_reports_one_positioned_diagnostic(source, line, start_char, end_char):
    [diagnostic] = diagnostics_for(source)  # exactly one, or the unpack fails
    assert diagnostic.severity == types.DiagnosticSeverity.Error
    assert diagnostic.source == "fakecoin"
    assert diagnostic.range.start == types.Position(line=line, character=start_char)
    assert diagnostic.range.end == types.Position(line=line, character=end_char)


def test_completion_items_are_the_keywords():
    items = completion_items()
    assert {item.label for item in items} == set(KEYWORDS)
    assert all(item.kind == types.CompletionItemKind.Keyword for item in items)


def test_create_server_builds_a_language_server():
    assert isinstance(create_server(), LanguageServer)


def test_publish_diagnostics_reports_parser_errors(mocker):
    uri = "file:///bad.coin"
    server = mocker.Mock()
    server.workspace.get_text_document.return_value.source = "  @"

    lsp_server._publish_diagnostics(server, uri)

    published_uri, diagnostics = server.publish_diagnostics.call_args.args
    assert published_uri == uri
    [diagnostic] = diagnostics  # the single lex error for "@"
    assert diagnostic.source == "fakecoin"
