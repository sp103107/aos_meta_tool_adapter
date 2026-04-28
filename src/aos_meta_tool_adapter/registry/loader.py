from __future__ import annotations

import json
from importlib import resources
from pathlib import Path
from typing import Any

from aos_meta_tool_adapter.contracts.models import (
    EnvelopeAdapterDescriptor,
    RegisteredTool,
    ToolDescriptor,
    ToolExecutionPolicy,
    ToolRuntimeBinding,
)


def load_registry_records(path: str | Path | None = None) -> list[dict[str, Any]]:
    if path is None:
        text = resources.files("aos_meta_tool_adapter.resources").joinpath("registry/tool_registry.jsonl").read_text(encoding="utf-8")
    else:
        text = Path(path).read_text(encoding='utf-8')
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def load_registry(path: str | Path | None = None) -> list[RegisteredTool]:
    tools: list[RegisteredTool] = []
    for record in load_registry_records(path):
        env = record.get('envelope_adapter')
        tools.append(
            RegisteredTool(
                descriptor=ToolDescriptor(**record['descriptor']),
                runtime_binding=ToolRuntimeBinding(**record['runtime_binding']),
                execution_policy=ToolExecutionPolicy(**record['execution_policy']),
                envelope_adapter=EnvelopeAdapterDescriptor(**env) if env else None,
                extra={k: v for k, v in record.items() if k not in {'descriptor', 'runtime_binding', 'execution_policy', 'envelope_adapter'}},
            )
        )
    return tools
