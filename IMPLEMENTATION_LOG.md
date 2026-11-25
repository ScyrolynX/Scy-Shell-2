# Implementation Log

## 2026-11-25 — Audit and repair pass

### 1. Dock edge placement had no runtime consumer

**Symptom.** `scy-shell config set scy.dock.placement left` stored the value and the CLI
reported it, but `scy-shell dock status` still showed `owner=lucid` and the dock stayed at
the bottom. The Lucid glass dock (`engines/lucid/luciddocks/Dock.qml`) only implements a
bottom-edge surface; only the Mandara Rail dock can sit on a side edge.

**Fix.** `ScyConfigStore._sync_dock_single_owner_state()` now computes an *effective* mode:
when placement is `left`/`right` and the configured style is one of the bottom-edge styles
(`island`/`notch`/`split`), routing uses `rail`. `_build_design_tokens_doc()` reports both
`mode` (effective) and `configured_mode` (stored), so the Studio and CLI tell the truth.

**Deliberately not done.** The routing does **not** rewrite `scy.dock.mode` or
`scy.dock.placement`. The project invariant is that every setting round-trips unchanged
through provider switches (`tests/test_phase2...::test_02`); cross-setting mutation broke
it. Routing is derived at read time instead.

### 2. `hypr emit` destroyed user keybinds

**Symptom.** With a custom bind in `~/.config/lucid/keybinds.json`, running `hypr emit`
replaced the file with the 67 template binds. Any later emit (install, profile apply,
performance tier, dock change) silently discarded the user's shortcuts.

**Fix.** `ScyHyprCoordinator.build_unified_keybinds()` loads the live user file and merges
by `id`: template order is preserved, user entries override template entries, and
user-only ids are appended. Repeated emits are idempotent and produce no duplicate ids.
Command rewrites (`SHARED_CMD_REWRITES`) still apply to shared exec binds.

### 3. Numbered Studio navigation

Titles such as `01 — Personalization` were replaced with plain names in
`schema/settings_catalogue.json`, `engines/lucid/scy-schema/settings_catalogue.json`,
`engines/lucid/Prefs.qml` and the dock page description. Internal page keys
(`01-personalization`) are unchanged because they are identifiers, not UI text.

### 4. Dock ownership recovery

When `config.toml` is lost, the loader imports native engine files. It now also reads
Mandara's `[scy_gates].dock_mode` and `/dock/position`, so a rail dock is not silently
reverted to the Lucid dock on recovery.

### 5. Provenance-preserving engine edits

Editing `engines/lucid/Prefs.qml` and `lucidprefs/ScySec03Dock.qml` broke
`scy-shell provenance` (the reverse-patch check failed). Rather than weakening the check,
`scripts/regen-adapter-patch.py` reconstructs the pristine upstream tree by reverse-applying
the current per-file hunk and rewrites `adapters/lucid/lucid-scy-adapter.patch`. Provenance
is green again, and future engine edits have a supported path.

### 6. Tooling and hygiene

- `scripts/lint-qml.sh`: discovers `pyside6-qmllint`, adds PySide6's Qt QML import path,
  and fails only on genuine diagnostics.
- `scripts/qml-stubs/qs/PrefsStub.qml`: declares `dockEnabled`/`dockStyle` used by
  `ScyBridge.qml`.
- `.gitignore` added; 17 tracked `__pycache__` files removed from the index.
- `tests/test_phase15_dock_placement_and_keybind_merge.py`: 8 regression tests.

### 7. Dead setting references found by a new checker

`scripts/check-studio-settings.py` extracts every `scy.*` literal from QML and Python and
classifies it as exact (matches a schema ID), namespace prefix (a valid prefix used with
`indexOf`/`slice`) or unknown. It found four:

| Reference | Reality | Fix |
|---|---|---|
| `scy.dock.engine` (IPC `setting.set`) | No such setting; the dock only reloaded for `dockEnabled` | Reload on any `scy.dock.*` change, so live dock edits apply |
| `scy.providers.lucid.prefs.reduceMotion` (×2 profiles) | No such setting; profiles silently changed nothing | Replaced with the real `motionScale` (1.0, 1.0, 0.5 for performance) |
| `scy.providers.lucid.prefs.notifDnd` (control centre) | No such setting, behind an `in schema.by_id` guard that was always false, so DND always read `False` | Reads the real `doNotDisturb`, and the snapshot reconciles live QML edits first |
| `scy.design.effects.` (startswith) | Dead prefix, no IDs match | Removed |

Result: 169 exact, 23 prefix, **0 unknown**. Wired into `make check-settings` and covered
by a Phase 15 test so it cannot regress.
