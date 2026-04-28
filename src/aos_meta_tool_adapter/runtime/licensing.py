from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from aos_meta_tool_adapter.reference import load_license_text, load_notice_text
from aos_meta_tool_adapter.utils.json import write_json
from aos_meta_tool_adapter.utils.paths import ensure_dir


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def emit_license_files(out_dir: Path) -> dict[str, str]:
    out_dir = ensure_dir(out_dir)
    metadata_dir = ensure_dir(out_dir / 'metadata')
    license_text = load_license_text()
    notice_text = load_notice_text()
    (out_dir / 'LICENSE.txt').write_text(license_text, encoding='utf-8')
    (out_dir / 'NOTICE.txt').write_text(notice_text, encoding='utf-8')
    manifest = {
        'license': 'MIT',
        'spdx_id': 'MIT',
        'propagated_at': _now(),
        'files': ['LICENSE.txt', 'NOTICE.txt'],
        'checksums': {
            'LICENSE.txt': _sha256_text(license_text),
            'NOTICE.txt': _sha256_text(notice_text),
        },
        'applies_to': ['wheel', 'repo', 'runtime_emits'],
    }
    write_json(metadata_dir / 'license_manifest.json', manifest)
    return {
        'license_path': str(out_dir / 'LICENSE.txt'),
        'notice_path': str(out_dir / 'NOTICE.txt'),
        'license_manifest_path': str(metadata_dir / 'license_manifest.json'),
    }
