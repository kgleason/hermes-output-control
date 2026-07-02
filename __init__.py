"""Trim noisy Hermes CLI progress lines."""

from __future__ import annotations

import builtins
from typing import Any

_SUPPRESS = ("┊ ⚡ preparing", "🔧 Auto-repaired tool name")


def _drop(text: str) -> bool:
    return any(needle in text for needle in _SUPPRESS)


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
    # ponytail: global print shim; replace with a core display hook if Hermes adds one.
    _patch_print()
    _patch_cli_cprint()


def _self_check() -> None:
    import contextlib
    import io

    _patch_print()
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        print("  ┊ ⚡ preparing mcp__hermes___terminal…")
        print("🔧 Auto-repaired tool name: '_terminal' -> 'terminal'")
        print("  ┊ 💻 $         gh pr close 2655")
    assert "⚡ preparing" not in buf.getvalue()
    assert "Auto-repaired" not in buf.getvalue()
    assert "gh pr close" in buf.getvalue()


if __name__ == "__main__":
    _self_check()
