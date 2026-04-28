from __future__ import annotations

from pathlib import Path
from typing import Any

from aos_meta_tool_adapter.contracts.models import EnvelopeAdapterDescriptor, RegisteredTool, ToolDescriptor, ToolExecutionPolicy, ToolRuntimeBinding
from aos_meta_tool_adapter.envelope.canonical import build_canonical_input_envelope, build_canonical_output_envelope
from aos_meta_tool_adapter.envelope.mappings import adapt_inbound_payload, adapt_outbound_payload
from aos_meta_tool_adapter.reference import load_reference
from aos_meta_tool_adapter.registry.loader import load_registry_records
from aos_meta_tool_adapter.registry.manifest import build_registry_manifest
from aos_meta_tool_adapter.registry.registry import ToolRegistry
from aos_meta_tool_adapter.registry.resolver import detect_availability
from aos_meta_tool_adapter.runtime.executor import run_registered_tool
from aos_meta_tool_adapter.runtime.validator import validate_registry_records, validate_runtime_config
from aos_meta_tool_adapter.utils.json import write_json


def inspect_reference() -> dict[str, Any]:
    ref = load_reference()
    manifest = ref['manifest']
    return {
        'manifest_schema_version': manifest.get('manifest_schema_version'),
        'jsonl_master_files': manifest.get('jsonl_master_files', []),
        'jsonl_split_files': manifest.get('jsonl_split_files', []),
        'inventory_count': len(ref['inventory']),
    }


def init_registry(out_path: str | Path) -> dict[str, Any]:
    records = load_registry_records()
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text('\n'.join(__import__('json').dumps(item, sort_keys=True) for item in records) + '\n', encoding='utf-8')
    return {'ok': True, 'written': str(out.resolve()), 'count': len(records)}


def list_registry(registry_path: str | Path | None = None) -> list[dict[str, Any]]:
    return [tool.to_dict() for tool in ToolRegistry(registry_path).list()]


def registry_manifest(registry_path: str | Path | None = None) -> dict[str, Any]:
    return build_registry_manifest(ToolRegistry(registry_path).list())


def validate_registry(registry_path: str | Path | None = None) -> dict[str, Any]:
    return validate_registry_records(load_registry_records(registry_path))


def resolve_tool(tool_id: str, registry_path: str | Path | None = None) -> dict[str, Any]:
    tool = ToolRegistry(registry_path).get(tool_id)
    return {'tool': tool.to_dict(), 'availability': detect_availability(tool)}


def tool_status(registry_path: str | Path | None = None) -> list[dict[str, Any]]:
    return [detect_availability(tool) for tool in ToolRegistry(registry_path).list()]


def emit_runtime_config(out_path: str | Path) -> dict[str, Any]:
    config = {
        'version': '1.1.0',
        'license_propagation': True,
        'default_mode': 'deterministic',
        'tool_overrides': {},
    }
    write_json(Path(out_path), config)
    return {'ok': True, 'written': str(Path(out_path).resolve()), 'validation': validate_runtime_config(config)}


def _default_policy(tool_id: str, execution_style: str) -> ToolExecutionPolicy:
    deterministic_only = execution_style == 'deterministic'
    hybrid_allowed = execution_style == 'hybrid'
    llm_allowed = execution_style in {'llm', 'hybrid'}
    return ToolExecutionPolicy(
        tool_id=tool_id,
        llm_allowed=llm_allowed,
        deterministic_only=deterministic_only,
        hybrid_allowed=hybrid_allowed,
        requires_retrieval_context=False,
        requires_validation_after_run=True,
        failure_policy='halt_or_quarantine',
    )


def register_tool(*, registry_path: str | Path, descriptor: ToolDescriptor, runtime_binding: ToolRuntimeBinding, execution_policy: ToolExecutionPolicy | None = None, envelope_adapter: EnvelopeAdapterDescriptor | None = None) -> dict[str, Any]:
    reg = ToolRegistry(registry_path)
    tool = RegisteredTool(
        descriptor=descriptor,
        runtime_binding=runtime_binding,
        execution_policy=execution_policy or _default_policy(descriptor.tool_id, descriptor.execution_style),
        envelope_adapter=envelope_adapter,
    )
    reg.upsert(tool)
    path = reg.save()
    return {'ok': True, 'written': str(path.resolve()), 'tool_id': descriptor.tool_id}


def register_wheel(registry_path: str | Path, *, tool_id: str, package_name: str, entrypoint: str | None = None, tool_name: str | None = None, execution_style: str = 'deterministic', tool_kind: str = 'tool', capability_tags: list[str] | None = None) -> dict[str, Any]:
    descriptor = ToolDescriptor(
        tool_id=tool_id,
        tool_name=tool_name or tool_id,
        tool_version='0.1.0',
        tool_kind=tool_kind,
        execution_style=execution_style,
        capability_tags=capability_tags or [],
        supported_modes=['wheel'],
        produces_families=[],
    )
    binding = ToolRuntimeBinding(tool_id=tool_id, binding_type='wheel', package_name=package_name, entrypoint=entrypoint, availability='registered')
    envelope = EnvelopeAdapterDescriptor(tool_id=tool_id)
    return register_tool(registry_path=registry_path, descriptor=descriptor, runtime_binding=binding, envelope_adapter=envelope)


def register_local(registry_path: str | Path, *, tool_id: str, local_path: str, command_template: str | None = None, tool_name: str | None = None, execution_style: str = 'deterministic', tool_kind: str = 'tool', capability_tags: list[str] | None = None) -> dict[str, Any]:
    descriptor = ToolDescriptor(
        tool_id=tool_id,
        tool_name=tool_name or tool_id,
        tool_version='0.1.0',
        tool_kind=tool_kind,
        execution_style=execution_style,
        capability_tags=capability_tags or [],
        supported_modes=['local_path'],
        produces_families=[],
    )
    binding = ToolRuntimeBinding(tool_id=tool_id, binding_type='local_path', local_path=local_path, command_template=command_template, availability='registered')
    envelope = EnvelopeAdapterDescriptor(tool_id=tool_id)
    return register_tool(registry_path=registry_path, descriptor=descriptor, runtime_binding=binding, envelope_adapter=envelope)


def register_callable(registry_path: str | Path, *, tool_id: str, callable_path: str, tool_name: str | None = None, execution_style: str = 'deterministic', tool_kind: str = 'tool', capability_tags: list[str] | None = None) -> dict[str, Any]:
    descriptor = ToolDescriptor(
        tool_id=tool_id,
        tool_name=tool_name or tool_id,
        tool_version='0.1.0',
        tool_kind=tool_kind,
        execution_style=execution_style,
        capability_tags=capability_tags or [],
        supported_modes=['python_callable'],
        produces_families=[],
    )
    binding = ToolRuntimeBinding(tool_id=tool_id, binding_type='python_callable', entrypoint=callable_path, availability='registered')
    envelope = EnvelopeAdapterDescriptor(tool_id=tool_id)
    return register_tool(registry_path=registry_path, descriptor=descriptor, runtime_binding=binding, envelope_adapter=envelope)


def run_tool(tool_id: str, input_value: str, out_dir: str | Path, allow_stub: bool = False, registry_path: str | Path | None = None) -> dict[str, Any]:
    tool = ToolRegistry(registry_path).get(tool_id)
    payload = {'request_id': f'req_{tool_id}', 'source_system': 'cli', 'input_payload': {'input': input_value, 'out': str(Path(out_dir).resolve())}}
    return run_registered_tool(tool, payload, Path(out_dir), allow_stub=allow_stub)


def run_chain(tool_ids: list[str], input_value: str, out_dir: str | Path, allow_stub: bool = False, registry_path: str | Path | None = None) -> dict[str, Any]:
    root = Path(out_dir)
    current_input = input_value
    results: list[dict[str, Any]] = []
    for idx, tool_id in enumerate(tool_ids, start=1):
        stage_dir = root / f'stage_{idx:02d}_{tool_id}'
        result = run_tool(tool_id, current_input, stage_dir, allow_stub=allow_stub, registry_path=registry_path)
        current_input = result['emitted']['normalized_output_path']
        results.append({'tool_id': tool_id, **result})
    return {'ok': True, 'stages': results, 'final_output': current_input}


def adapt_in(tool_id: str, external_payload: dict[str, Any], registry_path: str | Path | None = None) -> dict[str, Any]:
    tool = ToolRegistry(registry_path).get(tool_id)
    return build_canonical_input_envelope(tool, external_payload)


def adapt_out(tool_id: str, canonical_output_payload: dict[str, Any], registry_path: str | Path | None = None) -> dict[str, Any]:
    tool = ToolRegistry(registry_path).get(tool_id)
    return adapt_outbound_payload(canonical_output_payload, tool.envelope_adapter)
