#!/usr/bin/env bash
# Build and verify the distributable Scy-Shell source archive.
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec python3 "$ROOT_DIR/scripts/package_release.py"
