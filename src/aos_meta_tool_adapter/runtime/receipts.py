from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from aos_meta_tool_adapter.contracts.models import RegisteredTool
from aos_meta_tool_adapter.utils.json import write_json
from aos_meta_tool_adapter.utils.paths import ensure_dir


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def emit_run_receipt(tool: RegisteredTool, out_dir: Path, status: str, input_summary: dict[str, Any], output_summary: dict[str, Any], binding_resolution: dict[str, Any] | None = None) -> str:
    metadata_dir = ensure_dir(out_dir / 'metadata')
    payload = {
        'record_type': 'tool_run_receipt',
        'artifact_family': 'tool_run_receipt',
        'run_id': f"run_{tool.descriptor.tool_id}_{int(datetime.now(timezone.utc).timestamp())}",
        'tool_id': tool.descriptor.tool_id,
        'tool_version': tool.descriptor.tool_version,
        'binding_type': tool.runtime_binding.binding_type,
        'start_time': _now(),
        'end_time': _now(),
        'status': status,
        'input_summary': input_summary,
        'output_summary': output_summary,
        'license_context': {'propagated': True, 'license': 'MIT'},
        'binding_resolution': binding_resolution or {},
        'errors': [],
    }
    receipt_path = metadata_dir / 'tool_run_receipt.json'
    write_json(receipt_path, payload)
    return str(receipt_path)
