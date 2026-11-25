#!/usr/bin/env python3
"""Verify every setting ID referenced by the shell exists in the schema.

Reports three kinds of reference:
  exact  - a literal that matches a schema ID
  prefix - a literal that is a namespace prefix of one or more schema IDs
           (e.g. "scy.providers.lucid.prefs." used with indexOf/slice)
  unknown - a literal that is neither, i.e. a dead or mistyped setting

Exits non-zero when any unknown reference is found.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from scy_core.schema import ScySchema  # noqa: E402

SEARCH_DIRS = [ROOT / "engines" / "lucid", ROOT / "studio", ROOT / "src"]
SUFFIXES = {".qml", ".py"}
ID_RE = re.compile(r"""["'](scy\.[A-Za-z0-9_.]+)["']""")


def collect() -> dict[str, set[str]]:
    refs: dict[str, set[str]] = {}
    for base in SEARCH_DIRS:
        for path in base.rglob("*"):
            if path.suffix not in SUFFIXES or not path.is_file():
                continue
            try:
                text = path.read_text(errors="ignore")
            except OSError:
                continue
            for match in ID_RE.finditer(text):
                refs.setdefault(match.group(1), set()).add(str(path.relative_to(ROOT)))
    return refs


def main() -> int:
    schema = ScySchema()
    ids = set(schema.by_id)
    unknown: dict[str, set[str]] = {}
    exact = prefix = 0
    for ref, files in sorted(collect().items()):
        if ref in ids:
            exact += 1
        elif ref.endswith(".") and any(i.startswith(ref) for i in ids):
            prefix += 1
        else:
            unknown[ref] = files

    print(f"setting references: {exact} exact, {prefix} namespace prefix, {len(unknown)} unknown")
    if unknown:
        for ref, files in unknown.items():
            print(f"  UNKNOWN {ref}  ({', '.join(sorted(files))})", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
