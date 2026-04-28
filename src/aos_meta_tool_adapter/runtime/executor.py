from __future__ import annotations

from pathlib import Path
from typing import Any

from aos_meta_tool_adapter.contracts.models import RegisteredTool
from aos_meta_tool_adapter.envelope.canonical import build_canonical_input_envelope
from aos_meta_tool_adapter.envelope.validator import validate_canonical_input_envelope, validate_canonical_output_envelope
from aos_meta_tool_adapter.registry.resolver import detect_availability
from aos_meta_tool_adapter.runtime.binder import execute_tool_binding
from aos_meta_tool_adapter.runtime.licensing import emit_license_files
from aos_meta_tool_adapter.runtime.normalizer import normalize_output
from aos_meta_tool_adapter.runtime.receipts import emit_run_receipt
from aos_meta_tool_adapter.utils.json import write_json
from aos_meta_tool_adapter.utils.paths import ensure_dir


def run_registered_tool(tool: RegisteredTool, external_input_payload: dict[str, Any], out_dir: Path, allow_stub: bool = False) -> dict[str, Any]:
    out_dir = ensure_dir(out_dir)
    binding_resolution = detect_availability(tool)
    canonical_input = build_canonical_input_envelope(tool, external_input_payload)
    input_validation = validate_canonical_input_envelope(canonical_input)
    if not input_validation['ok']:
        raise ValueError(f"Invalid canonical input envelope: {input_validation['missing']}")

    license_files = emit_license_files(out_dir)
    raw_output = execute_tool_binding(tool, canonical_input, allow_stub=allow_stub)

    receipt_path = emit_run_receipt(
        tool,
        out_dir,
        status=raw_output.get('status', 'ok'),
        input_summary={'request_id': canonical_input['request_id'], 'source_system': canonical_input['source_system']},
        output_summary={'status': raw_output.get('status', 'ok')},
        binding_resolution=binding_resolution,
    )

    normalized = normalize_output(
        tool,
        external_input_payload,
        raw_output,
        receipt_relpath=str(Path(receipt_path).relative_to(out_dir)),
        license_relpath=str(Path(license_files['license_manifest_path']).relative_to(out_dir)),
    )
    output_validation = validate_canonical_output_envelope(normalized['canonical_output_envelope'])
    if not output_validation['ok']:
        raise ValueError(f"Invalid canonical output envelope: {output_validation['missing']}")

    normalized_path = out_dir / 'normalized_output.json'
    write_json(normalized_path, normalized)
    write_json(out_dir / 'canonical_input_envelope.json', normalized['canonical_input_envelope'])
    write_json(out_dir / 'canonical_output_envelope.json', normalized['canonical_output_envelope'])
    return {
        'normalized': normalized,
        'emitted': {
            'out_dir': str(out_dir),
            'receipt_path': receipt_path,
            'license_manifest_path': license_files['license_manifest_path'],
            'normalized_output_path': str(normalized_path),
            'canonical_input_envelope_path': str(out_dir / 'canonical_input_envelope.json'),
            'canonical_output_envelope_path': str(out_dir / 'canonical_output_envelope.json'),
        },
        'binding_resolution': binding_resolution,
    }
