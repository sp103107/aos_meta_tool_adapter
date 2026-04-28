from __future__ import annotations

import json
from importlib import resources
from typing import Any

PACKAGE = "aos_meta_tool_adapter.resources"


def _read_text(resource: str) -> str:
    return resources.files(PACKAGE).joinpath(resource).read_text(encoding="utf-8")


def _read_json(resource: str) -> dict[str, Any]:
    return json.loads(_read_text(resource))


def _read_jsonl(resource: str) -> list[dict[str, Any]]:
    return [json.loads(line) for line in _read_text(resource).splitlines() if line.strip()]


def load_reference() -> dict[str, Any]:
    manifest = _read_json("reference/pack_jsonl_manifest.json")
    inventory = _read_jsonl("reference/app_tool_schema_inventory.v1.jsonl")
    return {
        "manifest": manifest,
        "inventory": inventory,
        "factory_request_schema": _read_json("reference/factory_request.schema.json"),
        "schema_record_schema": _read_json("reference/schema_record.schema.json"),
        "readme": _read_text("reference/README.md"),
    }


def load_license_text() -> str:
    return resources.files("aos_meta_tool_adapter").joinpath("LICENSE").read_text(encoding="utf-8")


def load_notice_text() -> str:
    return resources.files("aos_meta_tool_adapter").joinpath("NOTICE").read_text(encoding="utf-8")
