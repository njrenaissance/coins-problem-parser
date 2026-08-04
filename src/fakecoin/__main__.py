"""Enable ``python -m fakecoin`` to run the command-line tool."""

from __future__ import annotations

import sys

from .cli import main

raise SystemExit(main(sys.argv[1:]))
