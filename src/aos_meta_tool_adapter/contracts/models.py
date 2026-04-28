from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class ToolDescriptor:
    tool_id: str
    tool_name: str
    tool_version: str
    tool_kind: str
    execution_style: str
    capability_tags: list[str]
    supported_modes: list[str]
    produces_families: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ToolRuntimeBinding:
    tool_id: str
    binding_type: str
    package_name: str | None = None
    entrypoint: str | None = None
    command_template: str | None = None
    availability: str = "auto_detect"
    local_path: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ToolExecutionPolicy:
    tool_id: str
    llm_allowed: bool
    deterministic_only: bool
    hybrid_allowed: bool
    requires_retrieval_context: bool = False
    requires_validation_after_run: bool = True
    failure_policy: str = "halt_or_quarantine"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class EnvelopeAdapterDescriptor:
    tool_id: str
    canonical_input_version: str = "1.0.0"
    canonical_output_version: str = "1.0.0"
    passthrough_input_payload: bool = True
    passthrough_output_payload: bool = True
    input_field_map: dict[str, str] = field(default_factory=dict)
    output_field_map: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class RegisteredTool:
    descriptor: ToolDescriptor
    runtime_binding: ToolRuntimeBinding
    execution_policy: ToolExecutionPolicy
    envelope_adapter: EnvelopeAdapterDescriptor | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = self.extra.copy()
        data.update({
            "descriptor": self.descriptor.to_dict(),
            "runtime_binding": self.runtime_binding.to_dict(),
            "execution_policy": self.execution_policy.to_dict(),
        })
        if self.envelope_adapter is not None:
            data["envelope_adapter"] = self.envelope_adapter.to_dict()
        return data
