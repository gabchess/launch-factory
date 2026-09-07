#!/usr/bin/env python3
# STRUCTURAL_INTEGRITY_ONLY — initializes a release workspace and a
# release-record skeleton from a release folder. Hashes input files; never
# publishes, never invents claims, never overwrites an existing record.
"""init_release RELEASE_FOLDER [--workspace DIR]

Creates DIR (default: runs/<folder-name>/ relative to cwd) containing
release-record.json — the canonical per-release state artifact. Refuses to
overwrite an existing record.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

RECORD_FILENAME = "release-record.json"

# Default HOLD reasons for the slots held until spine ships (ADR 0013).
DEFAULT_HOLDS = {
    1: "social video — no real footage; HOLD until encode track (ADR 0013)",
    5: "login animation — no real Lottie/asset source; HOLD (ADR 0013)",
    6: "in-app popup — no real popup source; HOLD (ADR 0013)",
}

SLOT_NAMES = [
    "social_video",
    "blog",
    "email_segments",
    "changelog",
    "login_animation",
    "in_app_popup",
    "campaign_plan",
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def hash_files(release_folder: Path) -> list[dict[str, Any]]:
    out = []
    for p in sorted(release_folder.rglob("*")):
        if p.is_file() and p.name != ".DS_Store":
            data = p.read_bytes()
            out.append(
                {
                    "path": str(p.relative_to(release_folder)),
                    "sha256": hashlib.sha256(data).hexdigest(),
                    "bytes": len(data),
                }
            )
    return out


def record_skeleton(release_folder: Path) -> dict[str, Any]:
    slots = []
    for i, name in enumerate(SLOT_NAMES, start=1):
        held_reason = DEFAULT_HOLDS.get(i, "not yet drafted — set by run")
        slots.append({"slot": i, "name": name, "state": "held", "hold_reason": held_reason})
    return {
        "record_id": f"rec_{release_folder.name}",
        "schema_version": "release-record/v1",
        "release_folder": {
            "path": str(release_folder),
            "files": hash_files(release_folder),
        },
        "ingest": {"state": "complete", "at": _now()},
        "claims": {"allowed": [], "forbidden": [], "held": []},
        "claims_lock": {"state": "drafted", "locked_at": None},
        "slots": slots,
        "voice_check": {
            "brief": "knowledge/voice-bank-brief.md (interim — ADR 0015)",
            "label": "interim",
            "results": [],
        },
        "validations": [],
        "gates": [],
        "package_path": None,
        "run_log": [{"at": _now(), "entry": f"init_release: ingested {release_folder}"}],
    }


def init_release(release_folder: Path, workspace: Path) -> Path:
    release_folder = release_folder.resolve()
    if not release_folder.is_dir():
        raise SystemExit(f"release folder not found: {release_folder}")
    record_path = workspace / RECORD_FILENAME
    if record_path.exists():
        raise SystemExit(
            f"refusing to overwrite existing record: {record_path} "
            "(resume from it instead; delete it only if you mean to re-ingest)"
        )
    workspace.mkdir(parents=True, exist_ok=True)
    record_path.write_text(
        json.dumps(record_skeleton(release_folder), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return record_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Initialize a release workspace + record skeleton")
    parser.add_argument("release_folder", type=Path)
    parser.add_argument("--workspace", type=Path, default=None,
                        help="workspace dir (default: runs/<folder-name>/)")
    args = parser.parse_args(argv)
    workspace = args.workspace or Path("runs") / args.release_folder.name
    record_path = init_release(args.release_folder, workspace)
    print(record_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
