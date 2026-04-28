from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from aos_meta_tool_adapter.api import (
    adapt_in,
    emit_runtime_config,
    init_registry,
    inspect_reference,
    list_registry,
    register_local,
    registry_manifest,
    resolve_tool,
    run_chain,
    run_tool,
    tool_status,
    validate_registry,
)


class MetaToolAdapterSmokeTests(unittest.TestCase):
    def test_reference(self) -> None:
        info = inspect_reference()
        self.assertEqual(info["manifest_schema_version"], "1.0.0")
        self.assertGreaterEqual(info["inventory_count"], 10)

    def test_registry(self) -> None:
        records = list_registry()
        self.assertEqual(len(records), 4)
        self.assertTrue(validate_registry()["ok"])
        manifest = registry_manifest()
        self.assertEqual(manifest["count"], 4)

    def test_status_and_resolve(self) -> None:
        statuses = tool_status()
        self.assertEqual(len(statuses), 4)
        resolved = resolve_tool("shredder")
        self.assertEqual(resolved["tool"]["descriptor"]["tool_id"], "shredder")

    def test_init_register_and_validate_custom_registry(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            reg_path = Path(tmp) / "tool_registry.jsonl"
            init_registry(reg_path)
            result = register_local(reg_path, tool_id="demo_local", local_path=tmp, tool_name="Demo Local")
            self.assertTrue(result["ok"])
            records = list_registry(reg_path)
            self.assertEqual(len(records), 5)
            self.assertTrue(validate_registry(reg_path)["ok"])

    def test_envelope_and_run_stub(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            reg_path = Path(tmp) / "tool_registry.jsonl"
            init_registry(reg_path)
            ext_payload = {
                "request_id": "req_ext_001",
                "source_system": "vendor_demo",
                "input_payload": {"input": "split.zip", "out": str(Path(tmp) / "out")},
            }
            cin = adapt_in("shredder", ext_payload, reg_path)
            self.assertEqual(cin["envelope_type"], "canonical_tool_input")
            cfg = emit_runtime_config(Path(tmp) / "toolchain_runtime_config.json")
            self.assertTrue(cfg["ok"])
            result = run_tool("shredder", "split.zip", Path(tmp) / "out", allow_stub=True, registry_path=reg_path)
            emitted = result["emitted"]
            self.assertTrue(Path(emitted["license_manifest_path"]).exists())
            self.assertTrue(Path(emitted["canonical_input_envelope_path"]).exists())
            self.assertTrue(Path(emitted["canonical_output_envelope_path"]).exists())

    def test_chain_stub(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            reg_path = Path(tmp) / "tool_registry.jsonl"
            init_registry(reg_path)
            result = run_chain(["shredder", "atomizer", "rag_molecule_db_generator"], "repo", Path(tmp) / "chain", allow_stub=True, registry_path=reg_path)
            self.assertTrue(result["ok"])
            self.assertEqual(len(result["stages"]), 3)


if __name__ == "__main__":
    unittest.main()
