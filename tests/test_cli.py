"""Tests for the command-line tool."""

import pytest

from fakecoin.cli import main

pytestmark = pytest.mark.unit

_EXIT_OK = 0
_EXIT_ERROR = 1


def test_evaluates_sample_solution(sample_path, capsys):
    exit_code = main([str(sample_path), "--evaluate"])
    captured = capsys.readouterr()
    assert exit_code == _EXIT_OK
    assert "Solves all 24 worlds" in captured.out


def test_summarises_without_evaluating(sample_path, capsys):
    exit_code = main([str(sample_path)])
    assert exit_code == _EXIT_OK
    assert "Parsed OK" in capsys.readouterr().out


def test_reports_missing_file(tmp_path, capsys):
    exit_code = main([str(tmp_path / "nope.txt")])
    assert exit_code == _EXIT_ERROR
    assert "cannot read" in capsys.readouterr().err


def test_reports_parse_error(tmp_path, capsys):
    bad = tmp_path / "bad.txt"
    bad.write_text("weigh(", encoding="utf-8")
    exit_code = main([str(bad)])
    assert exit_code == _EXIT_ERROR
    assert "error:" in capsys.readouterr().err


def test_reports_unsolved_solution(tmp_path, capsys):
    wrong = tmp_path / "wrong.txt"
    # A deliberately broken solution: coin 1 heavy is misreported as fake(2,...),
    # and coin 1 light is wrongly called genuine — exercising both verdict kinds
    # in the failure report.
    wrong.write_text(
        "weigh({1} vs {2}){ left>: fake(2,heavier); balance: genuine; right>: genuine; }",
        encoding="utf-8",
    )
    exit_code = main([str(wrong), "--evaluate"])
    captured = capsys.readouterr()
    assert exit_code == _EXIT_ERROR
    assert "FAILS" in captured.err
    assert "genuine" in captured.err
    assert "fake(" in captured.err
