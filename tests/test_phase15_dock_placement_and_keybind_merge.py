"""Phase 15 — Dock edge-placement routing and non-destructive keybind emission.

These regressions cover two defects found in the v2.0.0 tree:

1. ``scy.dock.placement = left|right`` was stored and reported by the CLI while the
   bottom-only Lucid glass dock kept owning the dock, so the setting had no visible
   effect. Edge placement must route to the Rail dock engine that can honour it.
2. ``hypr emit`` rebuilt ``~/.config/lucid/keybinds.json`` from the upstream template
   and silently discarded every shortcut the user had recorded.
"""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scy_core.config_store import ScyConfigStore
from scy_core.hypr_coordinator import ScyHyprCoordinator
from scy_core.native_services import ScyDockController
from scy_core.toml_io import load_toml


class TestDockPlacementRouting(unittest.TestCase):
    def _store(self, home: Path) -> ScyConfigStore:
        return ScyConfigStore(home_dir=home)

    def test_edge_placement_moves_dock_to_rail_engine(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = self._store(Path(tmp))
            for edge in ("left", "right"):
                store.set_setting("scy.dock.placement", edge)
                self.assertEqual(store.doc["active_providers"]["dock"], "mandara", edge)
                self.assertFalse(store.get_setting("scy.providers.lucid.prefs.dockEnabled"), edge)
                m_cfg = load_toml(store.mandara_config_path)
                self.assertTrue(m_cfg["dock"]["enabled"], edge)
                self.assertEqual(m_cfg["dock"]["position"], edge)
                self.assertEqual(ScyDockController(store).status()["mode"], "rail", edge)

    def test_edge_placement_never_rewrites_user_settings(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = self._store(Path(tmp))
            store.set_setting("scy.dock.placement", "left")
            # The style the user picked is preserved verbatim; routing is derived, not stored.
            self.assertEqual(store.get_setting("scy.dock.mode"), "island")
            self.assertEqual(store.get_setting("scy.dock.placement"), "left")
            store.set_setting("scy.dock.mode", "notch")
            self.assertEqual(store.get_setting("scy.dock.mode"), "notch")
            self.assertEqual(store.get_setting("scy.dock.placement"), "left")

    def test_returning_to_bottom_restores_glass_dock(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = self._store(Path(tmp))
            store.set_setting("scy.dock.placement", "left")
            store.set_setting("scy.dock.placement", "bottom")
            self.assertEqual(store.doc["active_providers"]["dock"], "lucid")
            self.assertTrue(store.get_setting("scy.providers.lucid.prefs.dockEnabled"))
            self.assertEqual(ScyDockController(store).status()["mode"], "island")

    def test_floating_keeps_glass_dock(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = self._store(Path(tmp))
            store.set_setting("scy.dock.placement", "floating")
            self.assertEqual(store.doc["active_providers"]["dock"], "lucid")
            self.assertEqual(store.get_setting("scy.dock.placement"), "floating")
            self.assertTrue(store.get_setting("scy.providers.lucid.prefs.dockEnabled"))

    def test_provider_switch_does_not_mutate_placement(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = self._store(Path(tmp))
            store.set_setting("scy.dock.placement", "left")
            ok, _ = store.set_provider("dock", "lucid")
            self.assertTrue(ok)
            self.assertEqual(store.get_setting("scy.dock.placement"), "left")
            # A left-edge request is still served by the rail engine, whichever provider was asked for.
            self.assertEqual(store.doc["active_providers"]["dock"], "mandara")


class TestKeybindEmissionIsNonDestructive(unittest.TestCase):
    def _seed(self, home: Path) -> Path:
        kb = home / ".config" / "lucid" / "keybinds.json"
        kb.parent.mkdir(parents=True, exist_ok=True)
        kb.write_text(json.dumps({"version": 1, "binds": [
            {"id": "my-custom", "keys": "SUPER + F9", "desc": "Mine",
             "category": "Custom", "type": "exec", "cmd": "my-thing"},
            {"id": "terminal", "keys": "SUPER + RETURN", "desc": "Terminal",
             "category": "Apps", "type": "exec", "cmd": "kitty"},
        ]}), encoding="utf-8")
        return kb

    def test_emit_preserves_custom_bind_and_override(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            kb = self._seed(home)
            store = ScyConfigStore(home_dir=home)
            ScyHyprCoordinator(store).emit_modular_configs()

            binds = {b["id"]: b for b in json.loads(kb.read_text())["binds"]}
            self.assertIn("my-custom", binds)
            self.assertEqual(binds["my-custom"]["cmd"], "my-thing")
            self.assertEqual(binds["terminal"]["cmd"], "kitty")

    def test_repeated_emit_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            kb = self._seed(home)
            store = ScyConfigStore(home_dir=home)
            coord = ScyHyprCoordinator(store)
            coord.emit_modular_configs()
            first = json.loads(kb.read_text())["binds"]
            coord.emit_modular_configs()
            second = json.loads(kb.read_text())["binds"]
            self.assertEqual(len(first), len(second))
            ids = [b["id"] for b in second]
            self.assertEqual(len(ids), len(set(ids)))

    def test_custom_bind_reaches_hyprland_dropin(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            self._seed(home)
            store = ScyConfigStore(home_dir=home)
            ScyHyprCoordinator(store).emit_modular_configs()
            conf = (home / ".config" / "hypr" / "scy-shell" / "scy-shell.conf").read_text()
            self.assertIn("my-thing", conf)


class TestStudioNavigationLabels(unittest.TestCase):
    def test_no_numbered_navigation_titles(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = ScyConfigStore(home_dir=Path(tmp))
            self.assertEqual(len(store.schema.studio_sections), 15)
            for sec in store.schema.studio_sections:
                title = str(sec.get("title") or "")
                self.assertTrue(title, sec)
                self.assertFalse(title[:2].isdigit(), f"numbered navigation title: {title!r}")


if __name__ == "__main__":
    unittest.main()


class TestNoDeadSettingReferences(unittest.TestCase):
    """Every setting ID the shell references must exist in the schema.

    A literal that is a namespace prefix (e.g. ``scy.providers.lucid.prefs.`` used with
    ``indexOf``/``slice``) is valid; anything else is a dead or mistyped setting that
    would silently do nothing at runtime.
    """

    def test_all_referenced_setting_ids_resolve(self):
        import subprocess
        import sys

        root = Path(__file__).resolve().parents[1]
        proc = subprocess.run(
            [sys.executable, str(root / "scripts" / "check-studio-settings.py")],
            capture_output=True, text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
