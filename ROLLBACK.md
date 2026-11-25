# Rollback

Detail: [`docs/UNINSTALL_AND_RECOVERY.md`](docs/UNINSTALL_AND_RECOVERY.md).

## Restore a settings backup

```zsh
scy-shell backup list
scy-shell backup restore <tag>
```

Backups are directories under `~/.local/share/scy-shell/backups/<tag>/` containing the
files plus a `manifest.json` describing origin paths and SHA-256 digests. Restore verifies
digests before writing and writes atomically.

## Recover from a corrupted `config.toml`

Scy-Shell handles this automatically on load:

1. Unreadable `config.toml` is copied to `~/.config/scy-shell/corrupt/config.toml.corrupted`.
2. `config.toml.last-good` is tried next.
3. If neither is usable, settings are rebuilt from the 14 native engine files
   (`prefs.json`, `blur.json`, `mandara/config.toml`, …).
4. Dock ownership is recovered from Mandara's durable `[scy_gates]`, so a rail dock does
   not silently revert to the Lucid dock.

## Undo an install

```zsh
./uninstall.sh
```

Removes the installed runtime, systemd user units and the Hyprland drop-in, and restores
the `install-<timestamp>` backup taken at install time.

## Undo an engine edit

```zsh
python3 scripts/regen-adapter-patch.py --engine lucid --check   # is the patch current?
git checkout -- engines/lucid && scy-shell provenance
```

If `provenance` reports a reverse-patch failure, an engine file was edited without
updating its adapter patch. Revert the file or regenerate the patch.
