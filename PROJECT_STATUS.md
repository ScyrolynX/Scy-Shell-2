# Scy-Shell v2.0.0 — Project Status

_Last updated: 2026-11-25_

## Verdict

The unified dotfile environment builds, installs, persists settings, lints cleanly and
passes its full automated suite on a headless Debian 13 host. It is **not** verified on a
live Hyprland/Quickshell session in this environment (no compositor available); see
`KNOWN_LIMITATIONS.md` for exactly which claims are untested.

## Verified in this workspace

| Area | State | Evidence |
|---|---|---|
| Unified settings schema | 2,026 settings, 15 Studio sections | `scy-shell status` |
| Settings persistence | round-trips through `config.toml` **and** 14 native engine stores | `tests/test_phase2_schema_config_ipc.py` |
| Upstream provenance | `ok: true` — 3,708 manifest files, 0 hash mismatches, all 12 patched files reverse-verify | `scy-shell provenance` |
| QML static analysis | 28/28 files, 0 errors | `scripts/lint-qml.sh` |
| Automated suite | 59 tests, 58 passed, 1 skipped, 0 failed | `python3 -m unittest discover -s tests` |
| Release archive | 3,432 files, 45.8 MiB, suite + install re-verified from extraction | `make package` |
| Installer | dry-run + real install into a throwaway `$HOME` | `./install.sh --dry-run`, `./install.sh` |
| Transactional preview | stage → diff → revert restores exact prior values | `scy-shell preview ...` |

## Work completed in this session

1. **Dock edge placement now actually moves the dock.** `scy.dock.placement=left|right`
   previously left the bottom-only Lucid glass dock in charge. Edge placement is now
   derived onto the Mandara Rail dock without rewriting any user setting.
2. **Keybind emission no longer destroys user shortcuts.** `hypr emit` rebuilt
   `~/.config/lucid/keybinds.json` from the template on every run. It now merges the
   template with the live user file, is idempotent, and still lands custom binds in the
   Hyprland drop-in.
3. **Studio navigation titles de-numbered** ("01 — Personalization" → "Personalization")
   across the schema catalogue and the Lucid nav definition.
4. **Dock ownership survives loss of `config.toml`** by recovering the owner from
   Mandara's durable `[scy_gates]`.
5. **Adapter-patch regeneration tooling** (`scripts/regen-adapter-patch.py`) so engine
   changes are carried by the declared patch instead of silently mutating vendored files.
6. **QML lint hardened**: finds PySide6's `qmllint`, resolves QtQuick from pip Qt, fails
   on real diagnostics, and tolerates only the documented `pragma Singleton` notice.
7. **Repository hygiene**: `.gitignore` added; 17 committed `__pycache__` artifacts and
   the committed `bin/scy-shell-ipc` binary untracked.
8. **Version metadata unified**: `__version__` was `1.0.0` while the CLI and IPC reported
   `2.0.0` in five hardcoded places. All now derive from `scy_core.__version__`.
9. **Installer no longer writes into the source tree**: the C IPC client is compiled into
   `~/.local/share/scy-shell/build/` and copied into the runtime, so an extracted archive
   can live on a read-only or root-owned path. The `scy-shell-ipc` symlink is created only
   when the binary exists, and uninstall removes the build directory.
10. **Tests no longer depend on a prebuilt binary**: the IPC test compiles
    `csrc/scy_ipc_client.c` itself (skipping cleanly without `gcc`), and the integrity
    test checks the source rather than the artifact. This is what made the suite pass from
    a fresh archive extraction.
11. **QML lint is independent of `$HOME`**: candidates are probed by execution and
    PySide6's site-packages are located explicitly, so the check works for any user, in
    the working tree or an extracted archive.
12. **Dead settings eliminated**: a new checker proved four setting references pointed at
    IDs that do not exist. All four now resolve; one of them (`scy.dock.engine`) meant the
    IPC dock reload never fired, and another (`notifDnd`) meant DND always read `False`.
13. **Reproducible packaging**: `make package` builds and self-verifies the release zip
    with `zipfile` (no `zip` binary needed), checking required files, absence of bytecode
    and preserved executable bits.

## Open work

- Live-session validation on CachyOS / Hyprland 0.57.2 / Quickshell 0.3.2.
- `floating` placement currently maps to the Lucid glass dock (neither engine implements
  a free-floating dock).
- Remaining dead-ish surface: settings whose runtime consumer is Hyprland-only cannot be
  observed from this container.

See `IMPLEMENTATION_LOG.md`, `TEST_RESULTS.md`, `FEATURE_PARITY_MATRIX.md`.
