from __future__ import annotations

import importlib
import subprocess
from pathlib import Path
from typing import Any

from aos_meta_tool_adapter.contracts.models import RegisteredTool


class ToolExecutionError(RuntimeError):
    pass


def execute_tool_binding(tool: RegisteredTool, canonical_input_envelope: dict[str, Any], allow_stub: bool = False) -> dict[str, Any]:
    binding = tool.runtime_binding
    payload = canonical_input_envelope['input_payload']

    if binding.binding_type == 'python_callable' and binding.entrypoint:
        module_name, callable_name = binding.entrypoint.split(':', 1)
        module = importlib.import_module(module_name)
        func = getattr(module, callable_name)
        return func(payload)

    if binding.binding_type == 'cli' and binding.command_template:
        input_value = str(payload.get('input', canonical_input_envelope.get('request_id', '')))
        out_value = str(payload.get('out', ''))
        command = binding.command_template.format(input=input_value, output=out_value)
        result = subprocess.run(command, shell=True, text=True, capture_output=True)
        if result.returncode != 0:
            raise ToolExecutionError(result.stderr.strip() or result.stdout.strip() or f'CLI failed: {command}')
        return {
            'status': 'ok',
            'binding': 'cli',
            'stdout': result.stdout,
            'stderr': result.stderr,
            'command': command,
        }

    if binding.binding_type == 'local_path' and binding.local_path:
        path = Path(binding.local_path)
        if path.exists():
            return {
                'status': 'ok',
                'binding': 'local_path',
                'path': str(path.resolve()),
                'note': 'Local path tool acknowledged; execution delegated externally in v1.1.0.',
            }

    if allow_stub:
        return {
            'status': 'stubbed',
            'binding': binding.binding_type,
            'note': f"Tool {tool.descriptor.tool_id} is not currently installed; emitted stub-safe result.",
            'artifacts_emitted': [],
        }

    raise ToolExecutionError(f"Tool {tool.descriptor.tool_id} is unavailable for binding_type={binding.binding_type}")
