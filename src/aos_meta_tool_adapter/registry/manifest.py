from __future__ import annotations

from typing import Any

from aos_meta_tool_adapter.contracts.models import RegisteredTool


def build_registry_manifest(tools: list[RegisteredTool]) -> dict[str, Any]:
    return {
        'record_type': 'tool_registry_manifest',
        'artifact_family': 'tool_registry_manifest',
        'registered_tools': [tool.descriptor.tool_id for tool in sorted(tools, key=lambda item: item.descriptor.tool_id)],
        'count': len(tools),
    }
