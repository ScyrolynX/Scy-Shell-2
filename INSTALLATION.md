# Installation

Target: **CachyOS / Arch**, Hyprland **0.57+**, Quickshell **0.3.2+**, Zsh. The installer
verifies versions instead of assuming them.

Detailed guide: [`docs/INSTALLATION.md`](docs/INSTALLATION.md).
Dependency list: [`docs/DEPENDENCIES.md`](docs/DEPENDENCIES.md).

## 1. Inspect before touching anything

```zsh
./install.sh --check-env      # reports missing packages, Hyprland/Quickshell versions
./install.sh --dry-run --profile balanced --with-hypr
```

`--dry-run` prints every planned write and leaves `$HOME` unchanged.

## 2. Install

```zsh
./install.sh --install-packages --profile balanced --with-hypr --enable-services
```

What it does, in order:

1. Snapshots existing `~/.config/{scy-shell,lucid,mandara,hypr,quickshell}` into
   `~/.local/share/scy-shell/backups/install-<timestamp>/` with a `manifest.json`.
2. Copies `src/`, `schema/`, `studio/`, `bin/` into
   `~/.local/share/scy-shell/runtime/` and links the launchers into `~/.local/bin/`.
3. Installs the patched Quickshell tree and the 15 Studio sections into
   `~/.config/quickshell/lucid/`.
4. Imports any existing standalone Lucid/Mandara preferences without overwriting them.
5. With `--with-hypr`, emits `~/.config/hypr/scy-shell/scy-shell.conf` and adds one
   `source =` line to your backed-up `hyprland.conf`.
6. With `--enable-services`, enables `scy-daemon.service`, `scy-lucid.service`,
   `scy-mandara.service` (each single-instance via `flock`).

## 3. After install

```zsh
scy-shell doctor          # environment diagnostics
scy-shell status          # settings, sections, single-owner state
scy-shell studio          # open the Studio
```

Make sure `~/.local/bin` is on `PATH` and the Zsh completion directory is on `fpath`
(see `docs/INSTALLATION.md` §2.3).

## Uninstall

```zsh
./uninstall.sh
```

Removes installed runtime, units and Hyprland drop-in, restoring the pre-install backup.
