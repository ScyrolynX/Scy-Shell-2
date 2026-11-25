# Known Limitations

Canonical platform notes: [`docs/KNOWN_LIMITATIONS.md`](docs/KNOWN_LIMITATIONS.md).
This file records what was **not** verified in the current audit environment and what
remains genuinely incomplete.

## Verification boundary

The audit ran in a Debian 13 container with **no Hyprland and no Quickshell**. Anything
that needs a live compositor is implemented and wired, but not observed running. It is
listed here rather than reported as passing:

- Bar, dock, Dynamic Island, widgets, notifications, OSD, overview and lock surfaces.
- Studio window rendering, live preview against a real shell, and drag-based dock resizing.
- SDDM / greetd login presentation.
- Audio, network, Bluetooth, battery, brightness and media integration.
- Hyprland keybind registration at runtime (emission and merge are tested; actual key
  handling is not).
- Multi-monitor behaviour and per-display settings.

## Functional gaps

1. **`floating` dock placement** is accepted by the schema but maps to the Lucid glass
   dock. Neither engine implements a freely floating, draggable dock surface. Left/right
   placement is served by the Mandara rail; bottom by the Lucid dock.
2. **Dock resize by dragging an edge** is only meaningful on the rail; the Lucid dock
   sizes from its settings. No fake handle is shown where resizing is unsupported.
3. **Studio mode selector at a side edge**: because routing is derived, choosing an
   island/notch/split style while placement is `left`/`right` keeps the rail active. The
   Studio reports `configured_mode` and the effective `mode` so the state is visible; it
   does not silently rewrite the stored style.
4. **Local AI agent (B-02)** requires model weights that are not bundled.
5. **Calendar/mail sync (B-07)** requires OAuth credentials.
6. **OCR and screen recording** require `tesseract` and `wf-recorder`.
7. **Greeter installation** stages configs under `~/.local/state/scy-shell/`; applying
   them to `/etc/sddm.conf.d/` needs root and is left to the user with the printed helper.
8. **Mandara full build** needs ≥ 4 GiB RAM; use `--skip-engine-build` on small machines.

## Tooling notes

- `scripts/lint-qml.sh` needs a `qmllint` (system Qt6 or PySide6). It tolerates exactly
  one structural warning: a standalone `pragma Singleton` file not listed in a `qmldir`,
  which is how Quickshell loads `ScyBridge` and `ScyDesignTokens`.
- `scripts/regen-adapter-patch.py` is required whenever a file inside `engines/` changes;
  `scy-shell provenance` fails otherwise, by design.
