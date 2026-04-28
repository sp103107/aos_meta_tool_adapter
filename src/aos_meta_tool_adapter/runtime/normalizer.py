from __future__ import annotations

from typing import Any

from aos_meta_tool_adapter.contracts.models import RegisteredTool
from aos_meta_tool_adapter.envelope.canonical import build_canonical_input_envelope, build_canonical_output_envelope


def normalize_output(tool: RegisteredTool, external_input_payload: dict[str, Any], raw_output: dict[str, Any], receipt_relpath: str | None = None, license_relpath: str | None = None) -> dict[str, Any]:
    canonical_input = build_canonical_input_envelope(tool, external_input_payload)
    canonical_output = build_canonical_output_envelope(tool, canonical_input, raw_output, receipt_relpath=receipt_relpath, license_relpath=license_relpath)
    return {
        'tool_id': tool.descriptor.tool_id,
        'tool_name': tool.descriptor.tool_name,
        'canonical_input_envelope': canonical_input,
        'canonical_output_envelope': canonical_output,
        'produces_families': tool.descriptor.produces_families,
        'execution_style': tool.descriptor.execution_style,
    }
