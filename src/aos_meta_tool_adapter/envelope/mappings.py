from __future__ import annotations

from typing import Any

from aos_meta_tool_adapter.contracts.models import EnvelopeAdapterDescriptor


def _apply_map(payload: dict[str, Any], mapping: dict[str, str]) -> dict[str, Any]:
    if not mapping:
        return dict(payload)
    out: dict[str, Any] = {}
    for src, value in payload.items():
        out[mapping.get(src, src)] = value
    return out


def adapt_inbound_payload(payload: dict[str, Any], adapter: EnvelopeAdapterDescriptor | None) -> dict[str, Any]:
    if adapter is None:
        return dict(payload)
    return _apply_map(payload, adapter.input_field_map)


def adapt_outbound_payload(payload: dict[str, Any], adapter: EnvelopeAdapterDescriptor | None) -> dict[str, Any]:
    if adapter is None:
        return dict(payload)
    return _apply_map(payload, adapter.output_field_map)
