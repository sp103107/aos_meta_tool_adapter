from __future__ import annotations

from pathlib import Path
from typing import Iterable

from aos_meta_tool_adapter.contracts.models import RegisteredTool


def write_registry(path: str | Path, tools: Iterable[RegisteredTool]) -> Path:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    for tool in sorted(tools, key=lambda item: item.descriptor.tool_id):
        import json
        lines.append(json.dumps(tool.to_dict(), sort_keys=True))
    out.write_text("\n".join(lines) + ("\n" if lines else ""), encoding='utf-8')
    return out
