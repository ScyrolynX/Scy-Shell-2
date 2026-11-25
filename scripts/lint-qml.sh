#!/usr/bin/env bash
# Static QML check for the Scy-Shell Studio and Lucid engine.
#
# Fails on any syntax, import, unresolved-type, missing-property or duplicate-binding
# diagnostic. One structural notice is tolerated: qmllint reports that a standalone
# `pragma Singleton` file is not listed in a qmldir, which is how Quickshell loads
# ScyBridge and ScyDesignTokens at runtime.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LUCID_DIR="${SCY_LUCID_DIR:-${ROOT_DIR}/engines/lucid}"

# pip-installed Qt ships its own QtQuick tree; find it so qmllint resolves QtQuick even
# when no system Qt6 declarative package is installed. Candidates are probed by running
# them, because a PySide6 wrapper can exist on PATH while the interpreter behind it
# cannot import PySide6 (a different $HOME, for example).
find_pyside_site() {
  local d
  for d in "${HOME:-/nonexistent}"/.local/lib/python3*/site-packages \
           /home/*/.local/lib/python3*/site-packages \
           /usr/local/lib/python3*/site-packages \
           /usr/lib/python3/dist-packages; do
    [[ -d "$d/PySide6" ]] && { printf '%s\n' "$d"; return 0; }
  done
  return 1
}

PYSIDE_SITE="$(find_pyside_site || true)"

with_pyside() {
  PYTHONPATH="${PYSIDE_SITE}${PYTHONPATH:+:$PYTHONPATH}" "$@"
}

QMLLINT=()
for candidate in qmllint /usr/lib/qt6/bin/qmllint /usr/lib64/qt6/bin/qmllint; do
  if command -v "$candidate" >/dev/null 2>&1 && with_pyside "$candidate" --version >/dev/null 2>&1; then
    QMLLINT=("$(command -v "$candidate")")
    break
  fi
done

if [[ "${#QMLLINT[@]}" -eq 0 ]]; then
  for candidate in pyside6-qmllint \
                   "${HOME:-/nonexistent}/.local/bin/pyside6-qmllint" \
                   /home/*/.local/bin/pyside6-qmllint \
                   /usr/bin/pyside6-qmllint; do
    if [[ -x "$candidate" ]] && with_pyside "$candidate" --version >/dev/null 2>&1; then
      QMLLINT=("$candidate")
      break
    fi
  done
fi

if [[ "${#QMLLINT[@]}" -eq 0 ]]; then
  echo "FATAL: no working Qt6 qmllint found (install qt6-declarative-dev-tools or PySide6)." >&2
  exit 127
fi

IMPORT_ARGS=(-I "${ROOT_DIR}/scripts/qml-stubs" -I "${ROOT_DIR}/studio")
for sys_qml in /usr/lib/qt6/qml /usr/lib/*-linux-gnu/qt6/qml /usr/lib64/qt6/qml; do
  [[ -d "$sys_qml" ]] && IMPORT_ARGS+=(-I "$sys_qml")
done
if [[ -n "$PYSIDE_SITE" ]]; then
  PY_QML="$(python3 -c 'import PySide6, pathlib; print(pathlib.Path(PySide6.__file__).parent / "Qt" / "qml")' 2>/dev/null || true)"
  [[ -n "$PY_QML" && -d "$PY_QML" ]] && IMPORT_ARGS+=(-I "$PY_QML")
fi

if [[ "$#" -gt 0 ]]; then
  TARGETS=("$@")
else
  if [[ ! -d "$LUCID_DIR" ]]; then
    echo "FATAL: Lucid QML directory not found at ${LUCID_DIR}" >&2
    exit 1
  fi
  IMPORT_ARGS+=(-I "${LUCID_DIR}/lucidprefs")
  TARGETS=(
    "${LUCID_DIR}/ScyBridge.qml"
    "${LUCID_DIR}/ScyDesignTokens.qml"
    "${LUCID_DIR}/lucidbar/ScyPluginPill.qml"
    "${LUCID_DIR}/lucidbar/ScyDynamicIsland.qml"
    "${LUCID_DIR}/lucidprefs/ScyStudioSectionBase.qml"
    "${LUCID_DIR}/lucidprefs/ScySec01Personalization.qml"
    "${LUCID_DIR}/lucidprefs/ScySec02Desktop.qml"
    "${LUCID_DIR}/lucidprefs/ScySec03Dock.qml"
    "${LUCID_DIR}/lucidprefs/ScySec04Effects.qml"
    "${LUCID_DIR}/lucidprefs/ScySec05Layout.qml"
    "${LUCID_DIR}/lucidprefs/ScySec06Widgets.qml"
    "${LUCID_DIR}/lucidprefs/ScySec07Windows.qml"
    "${LUCID_DIR}/lucidprefs/ScySec08Interactions.qml"
    "${LUCID_DIR}/lucidprefs/ScySec09Notifications.qml"
    "${LUCID_DIR}/lucidprefs/ScySec10System.qml"
    "${LUCID_DIR}/lucidprefs/ScySec11LockScreen.qml"
    "${LUCID_DIR}/lucidprefs/ScySec12Login.qml"
    "${LUCID_DIR}/lucidprefs/ScySec13Productivity.qml"
    "${LUCID_DIR}/lucidprefs/ScySec14Profiles.qml"
    "${LUCID_DIR}/lucidprefs/ScySec15Advanced.qml"
    "${LUCID_DIR}/lucidprefs/ScyAiPage.qml"
    "${LUCID_DIR}/lucidprefs/ScyConflictsPage.qml"
    "${LUCID_DIR}/lucidprefs/ScyLooksPage.qml"
    "${LUCID_DIR}/lucidprefs/ScyPluginsPage.qml"
    "${LUCID_DIR}/lucidprefs/ScyPreAuthPage.qml"
    "${LUCID_DIR}/lucidprefs/ScyProvidersPage.qml"
    "${LUCID_DIR}/lucidprefs/ScyVaultPage.qml"
    "${LUCID_DIR}/lucidprefs/ScyWallgenPage.qml"
  )
fi

export LC_ALL=C.UTF-8
LINT_LOG="$(mktemp)"
trap 'rm -f "$LINT_LOG"' EXIT

with_pyside "${QMLLINT[@]}" --bare -W 0 "${IMPORT_ARGS[@]}" "${TARGETS[@]}" >"$LINT_LOG" 2>&1 || true

if grep -v "not declared as singleton in qmldir but using pragma Singleton" "$LINT_LOG" | grep -qE "Error:|Warning:"; then
  cat "$LINT_LOG"
  echo "qmllint FAIL: diagnostics in ${#TARGETS[@]} QML files" >&2
  exit 1
fi

echo "qmllint PASS: ${#TARGETS[@]} QML files verified with 0 errors (fatal mode)."
