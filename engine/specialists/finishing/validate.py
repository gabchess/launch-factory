#!/usr/bin/env python3
"""Offline finishing JSON/reference checks. No providers, rendering or approval authority."""
import argparse
import hashlib
import json
import math
from pathlib import Path

import jsonschema

HERE = Path(__file__).resolve().parent
SCHEMAS = {"captions": "captions", "cues": "cue-sheet", "manifest": "generation-manifest"}


def reject_nonfinite(value):
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("Non-finite numbers are not valid finishing JSON")
    if isinstance(value, dict):
        for child in value.values():
            reject_nonfinite(child)
    elif isinstance(value, list):
        for child in value:
            reject_nonfinite(child)


def read_json(path):
    def invalid_constant(_):
        raise ValueError("Non-finite numbers are not valid finishing JSON")
    value = json.loads(path.read_text(), parse_constant=invalid_constant)
    reject_nonfinite(value)
    return value


def verify_file(record, workspace):
    workspace = Path(workspace).resolve()
    relative = Path(record["path"])
    path = (workspace / relative).resolve()
    if relative.is_absolute() or not path.is_relative_to(workspace):
        raise ValueError("Media path must stay within the supplied workspace")
    if hashlib.sha256(path.read_bytes()).hexdigest() != record["sha256"]:
        raise ValueError("Media hash mismatch")


def validate(kind, value, workspace, manifest=None):
    reject_nonfinite(value)
    schema = json.loads((HERE / "schemas" / (SCHEMAS[kind] + ".schema.json")).read_text())
    jsonschema.Draft202012Validator(schema).validate(value)
    if kind == "captions":
        verify_file(value["audio"], workspace)
        previous_start = -1
        for caption in value["captions"]:
            if caption["endMs"] <= caption["startMs"] or caption["startMs"] < previous_start:
                raise ValueError("Caption timing must be ordered with positive spans")
            previous_start = caption["startMs"]
    elif kind == "cues":
        if len({cue["id"] for cue in value["cues"]}) != len(value["cues"]):
            raise ValueError("Duplicate cue ID")
        if value["audio_mode"] == "silent" and value["cues"]:
            raise ValueError("Silent mode cannot contain audio cues")
        for cue in value["cues"]:
            span = cue["end_ms"] - cue["start_ms"]
            if span <= 0 or cue["end_ms"] > value["duration_ms"]:
                raise ValueError("Cue is outside the edit duration")
            if cue["fade_in_ms"] + cue["fade_out_ms"] > span:
                raise ValueError("Cue fades exceed its duration")
            if value["audio_mode"] == "music_sfx" and cue["kind"] == "speech":
                raise ValueError("Music/SFX mode cannot add a speech cue")
        if value["status"] == "resolved":
            if manifest is None:
                raise ValueError("Resolved cues require their media manifest")
            validate("manifest", manifest, workspace)
            materialized = {asset["id"] for asset in manifest["assets"] if asset["status"] == "materialized"}
            if any(cue["asset_id"] not in materialized for cue in value["cues"]):
                raise ValueError("Resolved cue names unavailable media")
    else:
        assets = {asset["id"]: asset for asset in value["assets"]}
        if len(assets) != len(value["assets"]):
            raise ValueError("Duplicate media asset ID")
        for asset in assets.values():
            if asset["status"] == "materialized" and asset["media"] is None:
                raise ValueError("Materialized media requires a file and hash")
            if asset["media"] is not None:
                verify_file(asset["media"], workspace)
            receipt = asset["provider_receipt"]
            if receipt and (receipt["provider"] != asset["provider"] or receipt["job_id"] != asset["job_id"]):
                raise ValueError("Provider/job label conflicts with its recorded receipt")
            if asset["license"]["status"] == "verified" and not (asset["license"]["reference"] or "").strip():
                raise ValueError("Verified license needs its evidence reference")
            if not set(asset["input_asset_ids"]) <= set(assets):
                raise ValueError("Unknown input asset")
        active, visited = set(), set()

        def visit(asset_id):
            if asset_id in active:
                raise ValueError("Media lineage cycle")
            if asset_id in visited:
                return
            active.add(asset_id)
            for parent in assets[asset_id]["input_asset_ids"]:
                visit(parent)
            active.remove(asset_id)
            visited.add(asset_id)

        for asset_id in assets:
            visit(asset_id)
        seen_checks = set()
        for check in value["checks"]:
            identity = (check["kind"], check["asset_id"])
            if identity in seen_checks:
                raise ValueError("Ambiguous duplicate check for an asset")
            seen_checks.add(identity)
            if check["status"] in {"pass", "fail"}:
                asset = assets.get(check["asset_id"])
                if not asset or asset["status"] != "materialized" or asset["media"] is None:
                    raise ValueError("A performed check needs a materialized subject")
                if asset["media"]["sha256"] != check["sha256"] or not (check["reference"] or "").strip():
                    raise ValueError("Check evidence must bind the exact current media hash and reference")
    return {"status": "passed", "kind": kind, "human_approval_granted": False,
            "scope": "JSON structure, temporal/lineage consistency and referenced hashes only; provider receipts, rights, transcription accuracy, listening and human identity are not authenticated"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kind", choices=SCHEMAS)
    parser.add_argument("input", type=Path)
    parser.add_argument("--workspace", required=True, type=Path)
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args()
    try:
        manifest = read_json(args.manifest) if args.manifest else None
        print(json.dumps(validate(args.kind, read_json(args.input), args.workspace, manifest), indent=2))
        return 0
    except (ValueError, OSError, jsonschema.ValidationError) as error:
        print(json.dumps({"status": "refused", "error": str(error).split("\n")[0], "human_approval_granted": False}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
