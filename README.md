# AoS Meta Tool Adapter v1.1.0

AoS Meta Tool Adapter is a publish-ready standalone Python wheel and repo for **generic tool registration, runtime binding resolution, execution, license propagation, and canonical one-in/one-out envelope adaptation**.

## Design law

- registry-first
- generic by default
- nothing baked in unless needed
- one canonical input envelope
- one canonical output envelope
- license files propagated in runtime emits

## What v1.1.0 adds

- writable registry bootstrap via `init-registry`
- generic tool registration for `wheel`, `local_path`, and `python_callable`
- registry manifest emission
- tool resolution with availability detection
- canonical input/output envelope adaptation
- licensed run bundles containing:
  - `LICENSE.txt`
  - `NOTICE.txt`
  - `metadata/license_manifest.json`
  - `metadata/tool_run_receipt.json`
  - `canonical_input_envelope.json`
  - `canonical_output_envelope.json`

## Install

```bash
pip install aos_meta_tool_adapter-1.1.0-py3-none-any.whl
```

## CLI

```bash
aos-tools inspect-reference

aos-tools init-registry --out ./tool_registry.jsonl
aos-tools registry list --registry-path ./tool_registry.jsonl
aos-tools registry validate --registry-path ./tool_registry.jsonl
aos-tools registry manifest --registry-path ./tool_registry.jsonl
aos-tools registry resolve atomizer --registry-path ./tool_registry.jsonl

aos-tools register wheel --registry-path ./tool_registry.jsonl --tool-id mytool --package my-tool
aos-tools register local --registry-path ./tool_registry.jsonl --tool-id atomizer --path ./atomizer
aos-tools register callable --registry-path ./tool_registry.jsonl --tool-id demo --callable demo.module:run

aos-tools tools status --registry-path ./tool_registry.jsonl

aos-tools envelope adapt-in shredder --registry-path ./tool_registry.jsonl --input ./external_payload.json
aos-tools envelope adapt-out shredder --registry-path ./tool_registry.jsonl --input ./canonical_output_payload.json

aos-tools run shredder --registry-path ./tool_registry.jsonl --input ./split.zip --out ./out --allow-stub
aos-tools chain shredder,atomizer,rag_molecule_db_generator --registry-path ./tool_registry.jsonl --input ./repo --out ./chain --allow-stub
```

## Reference grounding

The bundled reference files mirror the uploaded AoS contract-pack reference set:
- `pack_jsonl_manifest.json`
- `app_tool_schema_inventory.v1.jsonl`
- `factory_request.schema.json`
- `schema_record.schema.json`

## Development

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
python -m pip wheel . -w dist --no-deps
```
