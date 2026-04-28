# Reference files (ChatGPT / validation)

Files here support offline authors and GPT Actions. **Canonical JSONL contracts** live in the standard pack:

`standard_aos_app_tool_contract_pack_v1_freeze_ready_patch-1/standard_aos_app_tool_contract_pack_v1_freeze_ready_patch/jsonl/`

| File | Role |
|------|------|
| `pack_jsonl_manifest.json` | Lists every `jsonl/master/*.jsonl` and `jsonl/split/*.jsonl` basename; includes `canonical_inner_pack_relative`. |
| `app_tool_schema_inventory.v1.jsonl` | One row per Sorcer `incoming/` family: `artifact_family`, `schema_id`, `relative_path` (schema file under inner pack). |
| `factory_request.schema.json` | JSON Schema for `factory_request.json` (factory validator shape). |
| `schema_record.schema.json` | JSON Schema for one line of `app_tool_schema_inventory.v1.jsonl`. |

Regenerate the first two from the workspace with:

`python scripts/sync_contract_pack_reference.py`
