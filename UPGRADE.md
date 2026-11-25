# Upgrade

Detail: [`docs/UPGRADING_AND_MIGRATION.md`](docs/UPGRADING_AND_MIGRATION.md).

## Procedure

1. **Back up first.**
   ```zsh
   scy-shell backup create pre-upgrade
   ```
   Backups land in `~/.local/share/scy-shell/backups/<tag>/`.

2. **Extract the new release beside the old one** — do not overwrite a working tree.

3. **Check environment compatibility** before writing:
   ```zsh
   ./install.sh --check-env
   ./install.sh --dry-run
   ```

4. **Install over the existing setup.**
   ```zsh
   PROFILE="$(scy-shell status | jq -r .active_profile)"
   ./install.sh --profile "$PROFILE" --with-hypr --enable-services
   ```
   `scy-shell status` prints JSON. The installer snapshots the current state again before
   writing, so this step is itself reversible.

5. **Migrate settings.** `config.toml` carries a `schema_version`; on load Scy-Shell runs
   reversible migrations and records them in the change history. New settings take their
   defaults; existing values are preserved.

6. **Verify.**
   ```zsh
   scy-shell provenance     # upstream baseline + adapter patches intact
   scy-shell doctor
   scy-shell conflicts
   ```

## Notes

- The vendored engines are upgraded by replacing the engine directory and its adapter
  patch together. `scy-shell provenance` fails loudly if the pair does not match.
- If the keybind template gains binds, they are merged into your existing
  `~/.config/lucid/keybinds.json`; your own binds and overrides are kept.
