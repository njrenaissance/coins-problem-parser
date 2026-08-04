# 1. Adopt pygls for the fake-coin DSL language server

- Date: 2026-08-04
- Status: Accepted
- Issue: [#4](https://github.com/njrenaissance/coins-problem-parser/issues/4)

## Context

The `fakecoin` package parses and evaluates DSL solutions but offers no editor
support. Issue #4 asks for a Language Server Protocol (LSP) server that reuses the
existing parser to give editors live diagnostics and keyword completion. That
requires (a) implementing the LSP wire protocol and lifecycle, and (b) deciding
whether — and how — to take on a dependency for it. Adopting a dependency for a
whole subsystem is a decision the project records as an ADR
(`.claude/standards/decisions.md`).

## Options considered

1. **Hand-roll JSON-RPC over stdio.** Zero dependencies and full control, but it
   reimplements protocol plumbing (message framing, `initialize`/`shutdown`
   lifecycle, capability advertisement, position types) that is entirely
   incidental to our value — the parser. High surface area for bugs.
2. **`python-lsp-server` (pylsp) internals.** A full Python-language server with a
   plugin system; heavy and oriented toward Python tooling, not toward hosting a
   small custom-language server.
3. **`pygls`.** A focused, maintained framework for writing LSP servers in Python.
   It handles framing, lifecycle, and capabilities; ships typed protocol values
   via `lsprotocol` (both carry `py.typed`); and reduces our job to registering a
   few feature handlers. Cost: adds `pygls` (plus `lsprotocol`, `attrs`,
   `cattrs`) to the dependency graph.

## Decision

Use **pygls**, pinned **`>=1.3,<2`** to stay on the stable 1.x API and avoid the
2.0 breaking changes to server construction and feature registration.

Keep it **behind an optional `lsp` extra** so the core parser/evaluator remain
dependency-free; it is also listed in the dev dependency group so tests and CI
exercise it. Isolate the two concerns: pure, unit-tested feature logic lives in
`src/fakecoin/lsp/features.py`; the thin pygls wiring lives in
`src/fakecoin/lsp/server.py`.

## Consequences

- The core package still installs with **zero runtime dependencies**; LSP users
  opt in with `pip install '.[lsp]'` / `uv sync --extra lsp`.
- We inherit pygls's protocol handling and typing — less code to own and test.
- The server reuses `parse` and the `SourceError` position data directly, so any
  parser improvement flows into diagnostics for free.
- We are pinned to pygls 1.x; moving to 2.x is a deliberate future task (its
  `LanguageServer` import path and feature-registration API changed), not an
  automatic upgrade.
- **Follow-up:** no `adr` skill is installed, so this record uses the Markdown
  fallback described in `.claude/standards/decisions.md`. Adding an `adr` skill
  to standardise numbering/format is recommended.
