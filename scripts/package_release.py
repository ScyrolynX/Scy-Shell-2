#!/usr/bin/env python3
"""Build and verify the distributable Scy-Shell source archive.

Uses only the standard library so it works on hosts without `zip`.
"""
from __future__ import annotations

import sys
import time
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from scy_core import __version__  # noqa: E402

EXCLUDE_DIRS = {".git", "dist", "__pycache__", ".venv", "venv", "build", "node_modules"}
EXCLUDE_SUFFIXES = {".pyc", ".rej", ".orig"}
EXCLUDE_NAMES = {"bin/scy-shell-ipc"}  # built at install time
REQUIRED = [
    "README.md", "LICENSE", "install.sh", "uninstall.sh",
    "bin/scy-shell", "bin/scy-daemon",
    "src/scy_core/config_store.py", "schema/settings_catalogue.json",
    "adapters/lucid/lucid-scy-adapter.patch", "engines/lucid/shell.qml",
    "PROJECT_STATUS.md", "TEST_RESULTS.md", "ARCHITECTURE.md", "KNOWN_LIMITATIONS.md",
]
EXECUTABLE = ("install.sh", "uninstall.sh", "bin/scy-shell", "bin/scy-daemon")


def build(archive: Path) -> None:
    archive.unlink(missing_ok=True)
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in sorted(ROOT.rglob("*")):
            rel = path.relative_to(ROOT)
            if any(part in EXCLUDE_DIRS for part in rel.parts):
                continue
            if path.is_dir() or path.suffix in EXCLUDE_SUFFIXES:
                continue
            if rel.as_posix() in EXCLUDE_NAMES:
                continue
            info = zipfile.ZipInfo.from_file(path, rel.as_posix())
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (path.stat().st_mode & 0o777) << 16
            with path.open("rb") as src, zf.open(info, "w") as dst:
                while chunk := src.read(1 << 20):
                    dst.write(chunk)


def verify(archive: Path) -> list[str]:
    problems: list[str] = []
    with zipfile.ZipFile(archive) as zf:
        names = zf.namelist()
        infos = {i.filename: i for i in zf.infolist()}
    problems += [f"missing: {r}" for r in REQUIRED if r not in infos]
    problems += [f"bytecode: {n}" for n in names if "__pycache__" in n or n.endswith(".pyc")]
    for rel in EXECUTABLE:
        if rel in infos and not (infos[rel].external_attr >> 16) & 0o111:
            problems.append(f"lost executable bit: {rel}")
    return problems


def main() -> int:
    out_dir = ROOT / "dist"
    out_dir.mkdir(exist_ok=True)
    archive = out_dir / f"Scy-Shell-v{__version__}-{time.strftime('%Y%m%d')}.zip"
    build(archive)
    problems = verify(archive)
    if problems:
        print("Archive verification FAILED:", file=sys.stderr)
        for p in problems:
            print("  " + p, file=sys.stderr)
        return 1
    with zipfile.ZipFile(archive) as zf:
        count = len(zf.namelist())
    print(f"Archive: {archive}")
    print(f"Files:   {count}")
    print(f"Size:    {archive.stat().st_size / (1024 * 1024):.1f} MiB")
    print("Verification: OK (required files present, no bytecode, executables preserved)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
