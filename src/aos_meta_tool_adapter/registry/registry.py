from __future__ import annotations

from pathlib import Path

from aos_meta_tool_adapter.contracts.models import RegisteredTool
from aos_meta_tool_adapter.registry.loader import load_registry
from aos_meta_tool_adapter.registry.writer import write_registry


class ToolRegistry:
    def __init__(self, registry_path: str | Path | None = None) -> None:
        self.registry_path = Path(registry_path) if registry_path else None
        self._tools = {tool.descriptor.tool_id: tool for tool in load_registry(self.registry_path)}

    def list(self) -> list[RegisteredTool]:
        return [self._tools[key] for key in sorted(self._tools)]

    def get(self, tool_id: str) -> RegisteredTool:
        if tool_id not in self._tools:
            raise KeyError(f'Unknown tool_id: {tool_id}')
        return self._tools[tool_id]

    def upsert(self, tool: RegisteredTool) -> None:
        self._tools[tool.descriptor.tool_id] = tool

    def save(self, path: str | Path | None = None) -> Path:
        target = Path(path) if path else self.registry_path
        if target is None:
            raise ValueError('No writable registry path supplied')
        return write_registry(target, self.list())
