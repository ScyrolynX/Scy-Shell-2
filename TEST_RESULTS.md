# Test Results — 2026-11-25

Environment: Debian 13 (trixie) container, non-root user, no Hyprland and no Quickshell.
Python 3.13, PySide6 6.12 (pip), `qmllint` from PySide6. Nothing below was run against a
live compositor.

## Automated suite

```
PYTHONPATH=src python3 -m unittest discover -s tests -p "test_phase*.py"
Ran 59 tests in 36.1s
OK (skipped=1)
```

| Phase | File | Result |
|---|---|---|
| 1 | `test_phase1_provenance_audit.py` | pass |
| 2 | `test_phase2_schema_config_ipc.py` | pass (2,026-setting round-trip, native-only reload) |
| 3 | `test_phase3_conflicts_and_gates.py` | pass (upstream SHA-256 + reverse patch) |
| 4–13 | schema, profiles, native services, installer, final corrections | pass |
| 14 | `test_phase14_v2_evolution_and_regressions.py` | pass |
| 15 | `test_phase15_dock_placement_and_keybind_merge.py` | pass (10 regressions, incl. no-dead-setting check) |

The one skip is a host-dependent check (no compositor available).

## QML static analysis

```
./scripts/lint-qml.sh
qmllint PASS: 28 QML files verified with 0 errors (fatal mode).
```

The only tolerated diagnostic is qmllint's structural notice that a standalone
`pragma Singleton` file is not listed in a `qmldir` — which is how Quickshell loads
`ScyBridge` and `ScyDesignTokens`.

## Provenance

```
scy-shell provenance
ok: true
lucid:   770 untouched verified, 6 modified (all reverse-verified), 31 adapter files
mandara: 2434 untouched verified, 6 modified (all reverse-verified), 1 adapter file
hash_mismatches: []
reverse_errors: []
```

## Manual CLI checks

| Check | Result |
|---|---|
| `config set` then `config get` | value persists to `config.toml` |
| `dock status` after `placement=left` | `owner=mandara`, `mode=rail`, `configured_mode=island`, `placement=left` |
| `dock status` after `placement=bottom` | `owner=lucid`, `mode=island` |
| `hypr emit` with a custom bind | custom bind preserved, present in `scy-shell.conf`, 69 binds, 0 collisions |
| `hypr emit` twice | idempotent, 0 duplicate ids |
| `preview stage/diff/revert` | reverted value equals original (`42`) |
| `install.sh --dry-run` and real install to a temp `$HOME` | both succeed |
| `scy-shell conflicts` | 0 conflicts |
| `scripts/check-studio-settings.py` | 169 exact, 23 namespace prefix, 0 unknown |
| DND toggle read-back | live `prefs.json` edit surfaces as `dnd: true` in the control-centre snapshot, and `false` after toggling back |

## Release archive

```
make package   # scripts/package_release.py
Archive: dist/Scy-Shell-v2.0.0-20261125.zip
Files:   3432
Size:    45.8 MiB
Verification: OK (required files present, no bytecode, executables preserved)
```

Verified from a fresh extraction of that archive (not the working tree):

| Check | Result |
|---|---|
| Full suite in the extracted tree | 59 tests, 1 skipped, 0 failed |
| `scripts/lint-qml.sh` in the extracted tree | 28 files, 0 errors |
| `./install.sh --profile balanced --with-hypr` | finished cleanly, backup created |
| `scy-shell status` from `~/.local/bin` | reports v2.0.0, 2,026 settings |
| `scy-shell provenance` in the extracted tree | `ok: true` |
| `./uninstall.sh` afterwards | binaries, units and Hyprland drop-in removed; backups kept; `hyprland.conf` clean |

## Not run

- Any behaviour requiring Hyprland, Quickshell, a Wayland session, a display manager,
  audio/network hardware, or a real GPU. These remain unverified claims, not passes.
