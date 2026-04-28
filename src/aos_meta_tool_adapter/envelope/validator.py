from __future__ import annotations

from typing import Any


def validate_canonical_input_envelope(envelope: dict[str, Any]) -> dict[str, Any]:
    required = {'envelope_type', 'version', 'request_id', 'tool_id', 'binding_type', 'input_payload'}
    missing = sorted(required - set(envelope))
    return {'ok': not missing, 'missing': missing}


def validate_canonical_output_envelope(envelope: dict[str, Any]) -> dict[str, Any]:
    required = {'envelope_type', 'version', 'request_id', 'tool_id', 'status', 'output_payload'}
    missing = sorted(required - set(envelope))
    return {'ok': not missing, 'missing': missing}
