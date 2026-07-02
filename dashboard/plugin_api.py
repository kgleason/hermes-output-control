import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

try:
    from hermes_constants import get_hermes_home
except Exception:  # pragma: no cover
    get_hermes_home = lambda: Path.home() / ".hermes"  # type: ignore

router = APIRouter()

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


def _rules_path() -> Path:
    return get_hermes_home() / "plugins" / PLUGIN_NAME / RULES_FILE


def _merge_rules(saved: Any) -> list[dict[str, Any]]:
    by_id = {r["id"]: dict(r) for r in DEFAULT_RULES}
    if isinstance(saved, list):
        for row in saved:
            if not isinstance(row, dict):
                continue
            rid = row.get("id")
            if rid in by_id and isinstance(row.get("enabled"), bool):
                by_id[rid]["enabled"] = row["enabled"]
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


class RuleUpdate(BaseModel):
    id: str
    enabled: bool


class RulesUpdate(BaseModel):
    rules: list[RuleUpdate]


@router.get("/rules")
def get_rules():
    return {"rules": load_rules()}


@router.put("/rules")
def put_rules(payload: RulesUpdate):
    return {"rules": save_rules([r.model_dump() for r in payload.rules])}


@router.post("/reset")
def post_reset():
    return {"rules": reset_rules()}
