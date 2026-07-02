"""Configurable Hermes CLI output filter."""

from __future__ import annotations

import builtins
import json
from pathlib import Path
from typing import Any

try:
    from hermes_constants import get_hermes_home
except Exception:  # pragma: no cover - standalone self-check
    get_hermes_home = lambda: Path.home() / ".hermes"  # type: ignore

PLUGIN_NAME = "output-control"
RULES_FILE = "rules.local.json"

DEFAULT_RULES = [
    {
        "id": "tool.prepare.generic",
        "label": "Generic tool prepare line",
        "description": "Lines like: ┊ ⚡ preparing mcp__hermes___terminal…",
        "pattern": "┊ ⚡ preparing",
        "match": "contains",
        "enabled": False,
    },
    {
        "id": "tool.repair_name",
        "label": "Auto-repaired tool name",
        "description": "Lines like: 🔧 Auto-repaired tool name: '_terminal' -> 'terminal'",
        "pattern": "🔧 Auto-repaired tool name",
        "match": "contains",
        "enabled": False,
    },
    {
        "id": "plugin.ponytail.context_dump",
        "label": "Ponytail context dump",
        "description": "Suppress accidental PONYTAIL MODE ACTIVE instruction dumps.",
        "pattern": "PONYTAIL MODE ACTIVE",
        "match": "starts_with",
        "enabled": False,
    },
]


def _plugin_dir() -> Path:
    return get_hermes_home() / "plugins" / PLUGIN_NAME


def _rules_path() -> Path:
    return _plugin_dir() / RULES_FILE


def _merge_rules(saved: Any) -> list[dict[str, Any]]:
    by_id = {r["id"]: dict(r) for r in DEFAULT_RULES}
    if isinstance(saved, list):
        for row in saved:
            if not isinstance(row, dict):
                continue
            rid = row.get("id")
            if not isinstance(rid, str) or rid not in by_id:
                continue
            merged = dict(by_id[rid])
            if isinstance(row.get("enabled"), bool):
                merged["enabled"] = row["enabled"]
            by_id[rid] = merged
    return [by_id[r["id"]] for r in DEFAULT_RULES]


def load_rules() -> list[dict[str, Any]]:
    try:
        return _merge_rules(json.loads(_rules_path().read_text(encoding="utf-8")))
    except Exception:
        return _merge_rules(None)


def save_rules(rules: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged = _merge_rules(rules)
    path = _rules_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(merged, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return merged


def reset_rules() -> list[dict[str, Any]]:
    try:
        _rules_path().unlink()
    except FileNotFoundError:
        pass
    return load_rules()


def _drop(text: str) -> bool:
    for rule in load_rules():
        if rule.get("enabled", False):
            continue
        pattern = str(rule.get("pattern") or "")
        if not pattern:
            continue
        mode = rule.get("match")
        if mode == "starts_with" and text.lstrip().startswith(pattern):
            return True
        if mode == "contains" and pattern in text:
            return True
    return False


def _patch_print() -> None:
    old = builtins.print
    if getattr(old, "_output_control", False):
        return

    def quiet_print(*args: Any, **kwargs: Any) -> None:
        text = kwargs.get("sep", " ").join(str(a) for a in args)
        if _drop(text):
            return
        old(*args, **kwargs)

    quiet_print._output_control = True  # type: ignore[attr-defined]
    quiet_print._output_control_old = old  # type: ignore[attr-defined]
    builtins.print = quiet_print


def _patch_cli_cprint() -> None:
    try:
        import cli
    except Exception:
        return

    old = getattr(cli, "_cprint", None)
    if not callable(old) or getattr(old, "_output_control", False):
        return

    def quiet_cprint(text: str) -> None:
        if _drop(str(text)):
            return
        old(text)

    quiet_cprint._output_control = True  # type: ignore[attr-defined]
    quiet_cprint._output_control_old = old  # type: ignore[attr-defined]
    cli._cprint = quiet_cprint


def register(ctx) -> None:
    # ponytail: print shim until Hermes exposes stable display-event hooks.
    _patch_print()
    _patch_cli_cprint()


def _self_check() -> None:
    import contextlib
    import io
    import tempfile

    global get_hermes_home
    with tempfile.TemporaryDirectory(prefix="hermes-output-control-") as tmp:
        get_hermes_home = lambda: Path(tmp)  # type: ignore
        _patch_print()
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            print("  ┊ ⚡ preparing mcp__hermes___terminal…")
            print("🔧 Auto-repaired tool name: '_terminal' -> 'terminal'")
            print("PONYTAIL MODE ACTIVE — level: full\n# Ponytail")
            print("  ┊ 💻 $         gh pr close 2655")
        out = buf.getvalue()
        assert "⚡ preparing" not in out
        assert "Auto-repaired" not in out
        assert "PONYTAIL MODE" not in out
        assert "gh pr close" in out

        rules = load_rules()
        rules[0]["enabled"] = True
        save_rules(rules)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            print("  ┊ ⚡ preparing terminal…")
        assert "⚡ preparing" in buf.getvalue()


if __name__ == "__main__":
    _self_check()
