# recursive-parser

A recursive-descent parser and evaluator for a small domain-specific language
(DSL) that describes strategies for the **fake-coin (counterfeit-coin) balance
puzzle**. You write a weighing strategy in the DSL; the parser reads it into a
decision tree, and the evaluator checks whether that strategy actually solves
*every* possible case.

A minimal Python project, managed with [uv](https://docs.astral.sh/uv/).

## The fake-coin problem

You have **N** visually identical coins. Exactly one is a **fake**: it weighs
slightly more or slightly less than a genuine coin — and you don't know which.
Your only tool is a **two-pan balance**, which tells you only whether the left
pan is heavier, the right pan is heavier, or the two balance. You may use it at
most **X** times. Identify the fake coin *and* say whether it is heavier or
lighter.

The classic instance is **N = 12, X = 3**: twelve coins, three weighings. It is
famous because three weighings is exactly enough — each weighing has three
outcomes, so three of them distinguish 3³ = 27 situations, and there are only
2 × 12 = 24 "which coin, which direction" cases to tell apart.

A *strategy* is a decision tree. Each weighing you choose splits the remaining
possibilities three ways (left-heavy / balance / right-heavy); for each outcome
you either announce a verdict or perform another weighing. `spec/sample_solution.txt`
is a complete, correct strategy for the 12/3 instance.

## The DSL

The grammar lives in [`spec/grammar.ebnf`](spec/grammar.ebnf). It is
*parametrized* by `k`, the number of weighings still allowed — at `k = 0` you
must conclude. The grammar defines `solution`, `strategy`, and `weighing` and
leaves `pan` and `conclusion` implied; the sample fixes those, and the parser
implements the completed grammar below:

```ebnf
solution   = strategy ;
strategy   = conclusion | weighing ;          (* <k> weighings-remaining is a
                                                 semantic budget, not syntax *)
weighing   = "weigh" "(" pan "vs" pan ")"
             "{"
                "left>"   ":" strategy ";"
                "balance" ":" strategy ";"
                "right>"  ":" strategy ";"
             "}" ;
pan        = "{" coin { "," coin } "}" ;
conclusion = fake | "genuine" ;
fake       = "fake" "(" coin "," direction ")" ;
direction  = "heavier" | "lighter" ;
coin       = integer ;
```

`(* ... *)` comments may appear between any tokens and are ignored.

A `weighing` puts two pans (sets of coin labels) on the balance and gives a
sub-strategy for each of the three outcomes: `left>` (left pan heavier),
`balance`, and `right>` (right pan heavier). A leaf is a `conclusion`: either
`fake(coin, heavier|lighter)` naming the counterfeit, or `genuine`.

Reading the top of the sample:

```text
weigh( {1,2,3,4} vs {5,6,7,8} ) {   (* first weighing *)
  balance:                          (* pans equal -> fake is among 9..12 *)
    weigh( {9,10,11} vs {1,2,3} ) { (* 1,2,3 are now known-genuine references *)
      left>:  ...                   (* one of 9,10,11 is heavy *)
      balance: ...                  (* fake must be 12 *)
      right>: ...                   (* one of 9,10,11 is light *)
    } ;
  left>:  ...                       (* {1,2,3,4} heavy or {5,6,7,8} light *)
  right>: ...                       (* the mirror image *)
}
```

> **Branch order.** The EBNF writes the three branches `left> / balance /
> right>`, but real solutions — including the sample's outermost weighing —
> order them freely. The parser therefore accepts the three outcome branches in
> **any order**, requiring each to appear exactly once.

## The recursive-descent parser

The parser (in `src/fakecoin/`) is a textbook recursive-descent pipeline, one
concern per module:

| Stage | Module | What it does |
|-------|--------|--------------|
| Lex | `lexer.py` | Scans source text into a flat list of `Token`s, skipping whitespace and comments. |
| Parse | `parser.py` | One method per grammar production (`_strategy`, `_weighing`, `_pan`, `_conclusion`) consumes tokens and builds the tree. |
| Tree | `ast_nodes.py` | Immutable `Weighing` / `Fake` / `Genuine` nodes — the parsed `Strategy`. |
| Errors | `errors.py` | `FakeCoinError` hierarchy (`LexError`, `ParseError`) carrying the source line/column. |

Each production maps directly to a method, which is what makes the parser a
*recursive-descent* one: `_strategy` calls `_weighing`, which calls `_strategy`
again for each branch, mirroring the grammar's own recursion. An optional
`max_weighings` budget enforces the grammar's `<k>` parameter — once it hits
zero, a further `weigh(...)` is a parse error.

```python
from fakecoin import parse

strategy = parse(open("spec/sample_solution.txt").read())
```

## Running the parser (tool)

Parse a solution file and print a summary (how many coins it references and how
deep its weighing tree goes):

```bash
uv run fakecoin spec/sample_solution.txt
# Parsed OK: 12 coins, up to 3 weighings deep.
```

`uv run python -m fakecoin spec/sample_solution.txt` is equivalent. A malformed
solution exits non-zero with a `line, column` error message.

## Running an evaluation to check a solution

"Solving the puzzle" means the strategy resolves **every** case. The evaluator
infers the coin set from the solution, generates all `2N` worlds (each coin, as
heavier and as lighter), walks the decision tree for each — comparing pan weights
with exact `fractions.Fraction` arithmetic — and checks the verdict reached is
the right one.

Two ways to run it:

```bash
# 1. As a report from the CLI:
uv run fakecoin spec/sample_solution.txt --evaluate
# Parsed OK: 12 coins, up to 3 weighings deep.
# Solves all 24 worlds.

# 2. As a pytest sweep — one named case per world (e.g. coin7-lighter):
uv run pytest -m unit tests/test_evaluator.py -v
```

If a solution *fails* a case, both entry points report exactly which world it
mishandled and what verdict it wrongly reached, so you can see where the strategy
breaks. Programmatically:

```python
from fakecoin import parse, solves_all

report = solves_all(parse(source))
assert report.solved  # True only if all 2N worlds resolve correctly
print(report.failures)  # the worlds (if any) that went wrong
```

## Structure

```text
├── spec/
│   ├── grammar.ebnf          # the DSL grammar
│   └── sample_solution.txt   # a correct 12-coin / 3-weighing strategy
├── src/
│   └── fakecoin/
│       ├── lexer.py          # text  -> tokens
│       ├── parser.py         # tokens -> Strategy AST (recursive descent)
│       ├── ast_nodes.py      # Weighing / Fake / Genuine nodes
│       ├── evaluator.py      # simulate a strategy against every world
│       ├── cli.py            # `fakecoin` command-line tool
│       ├── errors.py         # FakeCoinError / LexError / ParseError
│       └── tokens.py         # Token + TokenType
├── tests/
│   ├── test_lexer.py
│   ├── test_parser.py
│   ├── test_evaluator.py     # the all-worlds sweep
│   └── test_cli.py
└── pyproject.toml
```

## Future work: an editor language server (LSP)

A natural next step is a [pygls](https://github.com/openlawlibrary/pygls)-based
language server for the DSL — reusing this parser to surface `ParseError`
positions as editor diagnostics and to offer keyword completion (`weigh`,
`left>`, `balance`, `right>`, `fake`, `genuine`, `heavier`, `lighter`). It is
deferred for now; adding it introduces a runtime dependency and is worth an ADR
when tackled.

## Setup

This project uses `uv` for package management, linting, and formatting. After
cloning, run setup once — it installs dependencies (including this package,
editable) and the local Git hooks:

```bash
make setup
```

(Equivalent to `uv sync && uv run pre-commit install && uv run pre-commit install --hook-type pre-push`.)

## Git hooks

Local quality gates run through the [`pre-commit`](https://pre-commit.com/)
framework (config in `.pre-commit-config.yaml`): `git commit` runs `ruff` and
`mypy`, and
`git push` runs `pytest`. `make setup` (above) installs them. Git can't
auto-install hooks on clone, so this one-time step is how they get wired up — but
CI (`.github/workflows/ci.yml`) runs the same checks regardless, so it stays the
real gate even when the local hooks aren't installed.

## Staying in sync with the template

This project was generated from the `basic` cookiecutter template and linked to it
with [`cruft`](https://cruft.github.io/cruft/). The link lives in `.cruft.json`
(template URL, the exact template commit, and the answers given at generation) — it
is what lets template improvements be pulled in later instead of the scaffold going
stale. Check whether the template has moved ahead:

```bash
uvx cruft check    # exit 0 = up to date; non-zero = behind
```

The **Template Sync** GitHub Actions workflow runs this check on demand (Actions tab
→ *Template Sync* → *Run workflow*); it is intentionally not part of the PR gate and
never blocks a merge. When the project is behind, run the `update-from-template`
skill (or `uvx cruft update` by hand) to apply the delta, resolve any `*.rej`
conflicts, and re-run the checks. See `.claude/standards/` and
`.claude/skills/update-from-template/` for the agent-run procedure.

## Wiki

This project keeps an `openwiki/` folder of generated codebase documentation
(produced by [OpenWiki](https://www.npmjs.com/package/openwiki)). It is
generated output — **never hand-edit it**; regenerate it and commit the result
alongside the code change that prompted it, so the wiki stays in step with
`main`.

OpenWiki is a per-machine global CLI, **not** a project dependency (it is never
added to `pyproject.toml`). Install and authenticate it once, then regenerate
before committing:

```bash
npm install -g openwiki    # one-time, per machine
openwiki auth <provider>   # one-time: sets up the LLM provider + API key
openwiki code --init       # first run in a fresh repo
openwiki code --update     # regenerate before committing a change
```

Regenerating calls a paid LLM provider. See `.claude/standards/wiki.md` for the
regenerate-before-commit rule agents follow.

## Test

```bash
uv run pytest -m unit
```

## Lint & format

```bash
uv run ruff check .
uv run ruff format .
```

## Type-check

```bash
uv run mypy src
```
