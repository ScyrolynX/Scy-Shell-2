#!/usr/bin/env python3
"""Regenerate an engine adapter patch after editing files inside a vendored engine.

Scy-Shell keeps its upstream engines byte-identical apart from one declared patch per
engine (``adapters/<engine>/<engine>-scy-adapter.patch``). ``scy-shell provenance``
verifies this by reverse-applying the patch and comparing SHA-256 against the upstream
manifest. Editing a vendored file without updating the patch breaks that guarantee.

This tool reconstructs the pristine upstream tree by reverse-applying the current patch
to the committed (HEAD) engine tree, then rewrites the patch as the diff between that
upstream tree and the working tree.

Usage:
    python3 scripts/regen-adapter-patch.py --engine lucid [--check]
"""
from __future__ import annotations

import argparse
import difflib
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from scy_core.provenance import parse_patch_touched_files  # noqa: E402


def git_show(rel: str) -> bytes | None:
    proc = subprocess.run(
        ["git", "show", f"HEAD:engines/{ENGINE}/{rel}"],
        cwd=ROOT, capture_output=True,
    )
    return proc.stdout if proc.returncode == 0 else None


def render_patch(upstream: dict[str, str | None], current: dict[str, str | None]) -> str:
    out: list[str] = []
    for rel in sorted(set(upstream) | set(current)):
        up = upstream.get(rel)
        cur = current.get(rel)
        if up == cur:
            continue
        up_lines = (up or "").splitlines(keepends=True)
        cur_lines = (cur or "").splitlines(keepends=True)
        out.append(f"diff --git a/{rel} b/{rel}\n")
        if up is None:
            out.append("new file mode 100644\n")
            fromfile, tofile = "/dev/null", f"b/{rel}"
        else:
            fromfile, tofile = f"a/{rel}", f"b/{rel}"
        diff = difflib.unified_diff(up_lines, cur_lines, fromfile=fromfile, tofile=tofile, n=3)
        for line in diff:
            out.append(line if line.endswith("\n") else line + "\n")
    return "".join(out)


def main() -> int:
    global ENGINE
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", required=True)
    ap.add_argument("--check", action="store_true", help="only report whether the patch is current")
    args = ap.parse_args()
    ENGINE = args.engine

    engine_dir = ROOT / "engines" / ENGINE
    patch_path = ROOT / "adapters" / ENGINE / f"{ENGINE}-scy-adapter.patch"
    modified, added = parse_patch_touched_files(patch_path)
    touched = sorted(modified | added)

    # Reconstruct upstream: added files did not exist upstream; modified files are
    # recovered by reverse-applying their own hunk block to the working copy.
    patch_text = patch_path.read_text(encoding="utf-8")
    blocks: dict[str, str] = {}
    for chunk in patch_text.split("diff --git ")[1:]:
        first = chunk.splitlines()[0]
        m = re.match(r"a/(.+?) b/(.+)$", first)
        if m:
            blocks[m.group(2)] = "diff --git " + chunk

    with tempfile.TemporaryDirectory() as tmp:
        up_root = Path(tmp)
        for rel in touched:
            src = engine_dir / rel
            if rel in added:
                continue
            if not src.exists() or rel not in blocks:
                print(f"FATAL: cannot reconstruct upstream for {rel}", file=sys.stderr)
                return 1
            dst = up_root / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            block_file = up_root / (rel.replace("/", "_") + ".patch")
            block_file.write_text(blocks[rel], encoding="utf-8")
            proc = subprocess.run(
                ["patch", "-p1", "-R", "--batch", "--silent", "-i", str(block_file)],
                cwd=up_root, capture_output=True, text=True,
            )
            if proc.returncode != 0:
                print(f"FATAL: cannot reverse {rel}: {proc.stderr or proc.stdout}", file=sys.stderr)
                return 1
            block_file.unlink()
        upstream = {
            rel: ((up_root / rel).read_text(encoding="utf-8") if (up_root / rel).exists() else None)
            for rel in touched
        }

    current = {}
    for rel in touched:
        p = engine_dir / rel
        current[rel] = p.read_text(encoding="utf-8") if p.exists() else None

    new_patch = render_patch(upstream, current)
    old_patch = patch_path.read_text(encoding="utf-8")
    if new_patch == old_patch:
        print(f"{ENGINE}: adapter patch already current ({len(touched)} files).")
        return 0
    if args.check:
        print(f"{ENGINE}: adapter patch is STALE; run without --check to regenerate.", file=sys.stderr)
        return 2
    patch_path.write_text(new_patch, encoding="utf-8")
    print(f"{ENGINE}: adapter patch regenerated ({len(touched)} files, {len(new_patch)} bytes).")
    return 0


ENGINE = ""
if __name__ == "__main__":
    raise SystemExit(main())
