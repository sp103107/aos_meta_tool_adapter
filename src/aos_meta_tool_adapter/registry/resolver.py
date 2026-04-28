from __future__ import annotations

import importlib.util
import shutil
from pathlib import Path
from typing import Any

from aos_meta_tool_adapter.contracts.models import RegisteredTool


def detect_availability(tool: RegisteredTool) -> dict[str, Any]:
    binding = tool.runtime_binding
    available = False
    reason = 'unavailable'
    resolved = None
    if binding.binding_type == 'python_callable' and binding.entrypoint:
        module_name = binding.entrypoint.split(':', 1)[0]
        available = importlib.util.find_spec(module_name) is not None
        reason = 'python_callable' if available else 'python_callable_not_found'
        resolved = binding.entrypoint if available else None
    elif binding.binding_type == 'wheel' and binding.package_name:
        mod = binding.package_name.replace('-', '_')
        available = importlib.util.find_spec(mod) is not None
        reason = 'wheel' if available else 'wheel_not_installed'
        resolved = binding.package_name if available else None
    elif binding.binding_type == 'cli' and binding.command_template:
        cmd = binding.command_template.split()[0]
        available = shutil.which(cmd) is not None
        reason = 'cli' if available else 'cli_not_found'
        resolved = shutil.which(cmd) if available else None
    elif binding.binding_type == 'local_path' and binding.local_path:
        available = Path(binding.local_path).exists()
        reason = 'local_path' if available else 'local_path_missing'
        resolved = str(Path(binding.local_path).resolve()) if available else None
    return {
        'tool_id': tool.descriptor.tool_id,
        'available': available,
        'binding_type': binding.binding_type,
        'reason': reason,
        'resolved_target': resolved,
    }
