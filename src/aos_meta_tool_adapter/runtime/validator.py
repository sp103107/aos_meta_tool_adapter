from __future__ import annotations

from typing import Any


def validate_registry_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []
    seen: set[str] = set()
    required_top = {'descriptor', 'runtime_binding', 'execution_policy'}
    for idx, record in enumerate(records):
        missing = sorted(required_top - set(record))
        if missing:
            issues.append({'severity': 'error', 'code': 'REG-001', 'index': idx, 'message': f'Missing top-level sections: {missing}'})
            continue
        tool_id = record['descriptor'].get('tool_id')
        if not tool_id:
            issues.append({'severity': 'error', 'code': 'REG-002', 'index': idx, 'message': 'descriptor.tool_id is required'})
        elif tool_id in seen:
            issues.append({'severity': 'error', 'code': 'REG-003', 'index': idx, 'message': f'Duplicate tool_id: {tool_id}'})
        else:
            seen.add(tool_id)
        if 'envelope_adapter' in record and record['envelope_adapter'].get('tool_id') not in {None, tool_id}:
            issues.append({'severity': 'error', 'code': 'REG-004', 'index': idx, 'message': 'envelope_adapter.tool_id must match descriptor.tool_id'})
    return {'ok': not any(i['severity'] == 'error' for i in issues), 'issues': issues, 'count': len(records)}


def validate_runtime_config(config: dict[str, Any]) -> dict[str, Any]:
    required = {'version', 'license_propagation', 'default_mode', 'tool_overrides'}
    missing = sorted(required - set(config))
    return {'ok': not missing, 'missing': missing}
