from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from aos_meta_tool_adapter.contracts.models import RegisteredTool
from aos_meta_tool_adapter.envelope.mappings import adapt_inbound_payload, adapt_outbound_payload


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def build_canonical_input_envelope(tool: RegisteredTool, external_payload: dict[str, Any]) -> dict[str, Any]:
    normalized = adapt_inbound_payload(external_payload, tool.envelope_adapter)
    request_id = normalized.get('request_id') or f"req_{tool.descriptor.tool_id}_{int(datetime.now(timezone.utc).timestamp())}"
    source_system = normalized.get('source_system', 'external')
    attachments = normalized.get('attachments', [])
    input_payload = normalized.get('input_payload', normalized)
    return {
        'envelope_type': 'canonical_tool_input',
        'version': tool.envelope_adapter.canonical_input_version if tool.envelope_adapter else '1.0.0',
        'request_id': request_id,
        'tool_id': tool.descriptor.tool_id,
        'source_system': source_system,
        'binding_type': tool.runtime_binding.binding_type,
        'input_payload': input_payload,
        'attachments': attachments,
        'execution_policy': tool.execution_policy.to_dict(),
        'license_context': {'propagate': True, 'license': 'MIT'},
        'trace': {'adapted_at': _now()},
    }


def build_canonical_output_envelope(tool: RegisteredTool, canonical_input: dict[str, Any], raw_output: dict[str, Any], receipt_relpath: str | None = None, license_relpath: str | None = None) -> dict[str, Any]:
    output_payload = adapt_outbound_payload(raw_output, tool.envelope_adapter)
    return {
        'envelope_type': 'canonical_tool_output',
        'version': tool.envelope_adapter.canonical_output_version if tool.envelope_adapter else '1.0.0',
        'request_id': canonical_input['request_id'],
        'tool_id': tool.descriptor.tool_id,
        'status': raw_output.get('status', 'ok'),
        'output_payload': output_payload,
        'artifacts_emitted': raw_output.get('artifacts_emitted', []),
        'receipt_path': receipt_relpath,
        'license_manifest_path': license_relpath,
        'trace': {'completed_from_request_id': canonical_input['request_id']},
    }
