# Feature Parity Matrix

Source inventory: `docs/stage0/03-feature-inventory.json` (41 features) and
`docs/stage0/03-FEATURE-COMPARISON-MATRIX.md`. Every feature in the audit is accounted for
below; none is silently dropped.

Status vocabulary:

- **verified** — exercised by an automated test or a CLI check in this workspace.
- **implemented; live-session unverified** — code, settings and routing exist and are
  wired to a consumer, but the behaviour needs a Hyprland/Quickshell session to confirm.
- **partial** — implemented with an external dependency or a known gap, stated in the row.

| ID | Feature | Source | Class | Scy-Shell status |
|---|---|---|---|---|
| A-01 | Lumen File Manager & XDG FileChooser Portal | Lucid | Class A | implemented; live-session unverified |
| A-02 | Lens Image Viewer & Quick Editor | Lucid | Class A | implemented; live-session unverified |
| A-03 | Lucid Standalone Clock App | Lucid | Class A | implemented; live-session unverified |
| A-04 | Desktop File & Folder Icons Canvas (~/Desktop) | Lucid | Class A | implemented; live-session unverified |
| A-05 | Jelly Squash-and-Stretch Physics & MaterialShape Organic Polygons | Lucid | Class A | implemented; live-session unverified |
| A-06 | On-Screen Virtual Keyboard (lucidkeys) | Lucid | Class A | implemented; live-session unverified |
| A-07 | SDDM Theme Synced with Per-User Lock Layout | Lucid | Class A | implemented; live-session unverified |
| A-08 | Hyprland Solo Mode, Cursor Tilt & Shake-to-Find Pointer | Lucid | Class A | implemented; live-session unverified |
| A-09 | Bluetooth OBEX File Receiver Daemon & Toast Inbox | Lucid | Class A | implemented; live-session unverified |
| B-01 | Sandboxed WASM Plugin Host (wasm32-wasip2) & 88 Built-in Plugins | Mandara | Class B | implemented; live-session unverified |
| B-02 | Local AI Command Agent (FunctionGemma-270M / Qwen3-0.6B) & Whisper Voice Input | Mandara | Class B | partial — needs local model files |
| B-03 | Wallgen Procedural GPU/CPU Wallpaper & Video Generator (13 Styles) | Mandara | Class B | implemented; live-session unverified |
| B-04 | 19 Complete Architectural Looks & Surface Grain / Chromatic Glass | Mandara | Class B | implemented; live-session unverified |
| B-05 | Multi-Compositor Backend Abstraction (11 Wayland Compositors) | Mandara | Class B | implemented; live-session unverified |
| B-06 | Screen Time & Per-App Focus Analytics | Mandara | Class B | implemented; live-session unverified |
| B-07 | CalDAV / Google / Microsoft OAuth2 Cloud Calendar & Mail Sync | Mandara | Class B | partial — needs OAuth credentials |
| B-08 | 3D Steam / Lutris / Heroic Game Shelf | Mandara | Class B | implemented; live-session unverified |
| B-09 | greetd Native Wayland Login Greeter (`mandara-greeter`) | Mandara | Class B | implemented; live-session unverified |
| B-10 | Edge Drawers, Side Bars, Hot Corners & Screen Bezel Corners | Mandara | Class B | implemented; live-session unverified |
| B-11 | 24-App Tamper-Safe Theme Ledger & `Config doctor` | Mandara | Class B/F | verified (provenance + theme ledger tests) |
| D-01 | Top / Side / Bottom Status Bar | Both (Materially Different) | Class D | implemented; live-session unverified |
| D-02 | Application Dock | Both (Materially Different) | Class D | verified (routing + single-owner tests) |
| D-03 | Application Launcher & Command Palette | Both (Materially Different) | Class D | implemented; live-session unverified |
| D-04 | Quick Settings / Control Centre | Both (Materially Different) | Class D | implemented; live-session unverified |
| D-05 | Notifications Daemon, Toasts & Notification Centre | Both (Exclusive D-Bus Bus Name) | Class D + Class F | implemented; live-session unverified |
| C-01 | On-Screen Display (OSD: Volume, Brightness, Mic, Caps/Layout) | Both (Equivalent Role) | Class C | implemented; live-session unverified |
| D-06 | Desktop Widgets Canvas | Both (Materially Different) | Class D | partial — widgets render, drag placement unverified |
| D-07 | Wallpaper Engine (Static, Transitions, Video, Shaders & Wallgen) | Both (Materially Different) | Class D + Class F | implemented; live-session unverified |
| D-08 | Wayland Session Lock (`ext-session-lock-v1`) | Both (Exclusive Wayland Protocol) | Class D + Class F | implemented; live-session unverified |
| D-09 | Screenshot, OCR, Annotation & Screen Recording | Both (Materially Different) | Class D | partial — OCR/recording need tesseract/wf-recorder |
| D-10 | Workspace Overview, Exposé & Window Switcher (Alt-Tab) | Both (Materially Different) | Class D | implemented; live-session unverified |
| C-02 | Clipboard History Manager | Both | Class C + Class F | implemented; live-session unverified |
| F-01 | Polkit Authentication Agent (`unix-session`) | Both | Class F | implemented; live-session unverified |
| F-02 | Night Light / Display Gamma Control (`zwlr_gamma_control_v1`) | Both | Class F | implemented; live-session unverified |
| F-03 | System Tray (`org.kde.StatusNotifierWatcher` & `Host`) | Both | Class F | implemented; live-session unverified |
| F-04 | Bluetooth Pairing Agent (`org.bluez.Agent1`) | Both | Class F | implemented; live-session unverified |
| F-05 | Idle Management & DPMS (`ext-idle-notify-v1` / `hypridle`) | Both | Class F | implemented; live-session unverified |
| F-06 | Hyprland Configuration, Rules, Monitors & Keybind Generation | Both | Class F + Class E | verified (keybind merge + emit tests) |
| E-01 | Scy-Shell Unified Core Daemon, State Bus & Provider Arbitrator (`scy-daemon`) | Neither (Scy-Shell Native) | Class E | verified (daemon/IPC tests) |
| E-02 | Unified Scy-Shell Studio (Material 3 Expressive Central Settings & Conflict UI) | Neither (Scy-Shell Native) | Class E | verified (schema + 15-section routing tests) |
| E-03 | Pre-Activation External & Internal Conflict Detector (`scy-shell conflicts`) | Neither (Scy-Shell Native) | Class E | verified (conflict scan CLI) |

## Notes on overlap resolution

- **Dock (D-02)**: one owner at a time. Lucid supplies the glass styles, Mandara supplies
  the rail. Edge placement routes to the rail engine; this was previously broken and is
  now covered by `tests/test_phase15_dock_placement_and_keybind_merge.py`.
- **Hyprland coordinator (F-06)**: Scy-Shell owns keybind generation. Emission merges the
  template with the user's live keybinds instead of overwriting them.
- **Studio (E-02)**: settings are rendered from the 2,026-entry schema per section, so a
  catalogue entry automatically becomes a control; bespoke decks sit on top.
- **Notifications, lock, clipboard, polkit, night light, tray, Bluetooth agent, idle**
  are exclusive-resource features arbitrated through `active_providers` and mirrored into
  Mandara's `[scy_gates]`.
