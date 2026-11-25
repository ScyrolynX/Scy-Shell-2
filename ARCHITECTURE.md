# Architecture

Scy-Shell is a user-space desktop environment: Hyprland provides the compositor,
Quickshell runs the QML shell, and a Python control plane owns settings, routing,
integration and diagnostics.

```
bin/scy-shell            CLI (settings, dock, hypr, profiles, preview, doctor, install)
bin/scy-daemon           session daemon: IPC server, reconcile, supervision
bin/scy-launch-engine    single-instance engine launcher (flock per engine)
src/scy_core/
  schema.py              loads schema/settings_catalogue.json -> 2,026 SettingMeta
  config_store.py        single source of truth; writes config.toml + 14 native stores
  hypr_coordinator.py    emits Hyprland drop-ins, keybinds, autostart dedup
  native_services.py     dock controller, control center, performance, productivity
  process_guard.py       SingleInstanceLock, ProcessSupervisor
  provenance.py          SHA-256 baseline + reverse-patch verification
  profiles.py            built-in and user presets
  layout_and_lab.py      layout composer and component lab
  security_preauth.py    lock/login staging, pre-auth coordination
engines/lucid/           vendored Quickshell QML engine (upstream + declared patch)
engines/mandara/         vendored Rust engine (upstream + declared patch)
adapters/*/              the only sanctioned modifications to vendored engines
studio/                  Scy-Shell Studio shell and shared controls
schema/                  settings catalogue (generated, mirrored into Lucid)
systemd/                 user units
```

## Ownership rules

- **Settings**: `ScyConfigStore` is authoritative. `config.toml` is the primary record;
  each engine's native file is written from it. On startup the store reconciles live
  engine edits (`reconcile_live_engine_stores`) so a QML-side edit is never clobbered.
- **Dock**: exactly one engine owns the dock at a time. Ownership is recorded in
  Mandara's `[scy_gates]` and mirrored to `Prefs.dockEnabled`. Edge placement
  (`left`/`right`) is served by the Rail dock; bottom-edge styles by the Lucid dock.
- **Keybinds**: `~/.config/lucid/keybinds.json` is user data. Emission merges the
  template with the live file by bind id and never drops user entries.
- **Vendored engines**: byte-identical to upstream except for one patch per engine.
  `scy-shell provenance` reverse-applies that patch and compares SHA-256. Engine edits
  go through `scripts/regen-adapter-patch.py`.

## Data flow for a setting change

1. `scy-shell config set <id> <value>` (or Studio → `ScyBridge.setValue`).
2. `ScySchema.validate_and_coerce` rejects wrong types and out-of-range values.
3. `ScyConfigStore._write_meta_value` updates the document and any coupled native field.
4. `flush_all()` writes `config.toml`, the 14 native stores, design tokens and the
   change history, then applies exclusive engine gates.
5. Consumers read from the native files: Quickshell QML, Mandara Rust, Hyprland.
