#!/usr/bin/env python3
"""Offline specialist projection. No provider calls, state writes or approval authority."""
import argparse
import hashlib
import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
BANK = ROOT / "engine" / "specialists"
REGISTRY = json.loads((BANK / "registry.json").read_text())


def digest(data):
    return hashlib.sha256(data).hexdigest()


def validate_schema(value, name):
    jsonschema.Draft202012Validator(json.loads((BANK / name).read_text())).validate(value)


def unique_by(items, field="id"):
    result = {item[field]: item for item in items}
    if len(result) != len(items):
        raise ValueError(f"Duplicate {field}")
    return result


def checked_file(workspace, item):
    relative = Path(item["path"])
    path = (workspace / relative).resolve()
    if relative.is_absolute() or not path.is_relative_to(workspace):
        raise ValueError(f"Path outside release workspace: {item['id']}")
    data = path.read_bytes()
    if digest(data) != item["sha256"]:
        raise ValueError(f"SHA-256 mismatch: {item['id']}")
    return data


def affected_closure(sources, artifacts, changed):
    nodes = set(sources) | set(artifacts)
    graph = {key: item["depends_on"] for key, item in artifacts.items()}
    if set(sources) & set(artifacts):
        raise ValueError("Source and artifact IDs must be distinct")
    if any(dep not in nodes for deps in graph.values() for dep in deps):
        raise ValueError("Unknown dependency")
    active, visited = set(), set()

    def visit(node):
        if node in active:
            raise ValueError("Dependency cycle")
        if node in visited:
            return
        active.add(node)
        for dep in graph.get(node, []):
            visit(dep)
        active.remove(node)
        visited.add(node)

    for node in graph:
        visit(node)
    affected = set(changed)
    if not affected <= nodes:
        raise ValueError("Unknown changed ID")
    while True:
        expanded = affected | {key for key, deps in graph.items() if affected.intersection(deps)}
        if expanded == affected:
            return sorted(affected & set(artifacts))
        affected = expanded


def dependency_bindings(target_id, sources, artifacts):
    """Bind only this target's transitive inputs, after graph validation."""
    selected = set()

    def visit(node):
        for dependency in artifacts.get(node, {}).get("depends_on", []):
            if dependency not in selected:
                selected.add(dependency)
                visit(dependency)

    visit(target_id)
    return [{"id": node, "sha256": (artifacts.get(node) or sources[node])["sha256"],
             **({"version": artifacts[node]["version"]} if node in artifacts else {})}
            for node in sorted(selected)]


def route_request(request, workspace):
    validate_schema(request, "request.schema.json")
    workspace = Path(workspace).resolve()
    route = REGISTRY["routes"].get(request["deliverable"])
    if route is None:
        raise ValueError("Unknown deliverable")
    if route.get("opt_in") and not request.get("carousel_opt_in", False):
        raise ValueError("Carousel requires explicit opt-in")
    sources = unique_by(request["sources"])
    claims = unique_by(request["claims"])
    artifacts = unique_by(request["artifacts"])
    data = {}
    for item in [*sources.values(), *artifacts.values()]:
        if item["product_id"] != request["product_id"]:
            raise ValueError(f"Wrong-product context: {item['id']}")
        data[item["id"]] = checked_file(workspace, item)
    for claim in claims.values():
        source = sources.get(claim["source_id"])
        if source is None or source["kind"] != "fact":
            raise ValueError(f"Missing fact evidence: {claim['id']}")
        text = data[source["id"]].decode("utf-8")
        if not 0 <= claim["start"] < claim["end"] <= len(text) or text[claim["start"]:claim["end"]] != claim["quote"]:
            raise ValueError(f"Source span mismatch: {claim['id']}")
    voice_ids = request["voice_source_ids"]
    if any(sid not in sources or sources[sid]["kind"] != "voice" for sid in voice_ids):
        raise ValueError("Voice references must select voice sources")
    affected = affected_closure(sources, artifacts, request.get("changed_ids", []))
    target_id = request.get("target_asset_id")
    if target_id is not None and target_id not in artifacts:
        raise ValueError("Unknown target artifact")
    holds = []
    if not any(source["kind"] == "fact" for source in sources.values()):
        holds.append("Supply product fact evidence for the source gate")
    if request["stage"] != "source" and not claims:
        holds.append("Select product claims with exact source spans before drafting")
    if request["stage"] != "source" and not voice_ids:
        holds.append("Select voice evidence for this product")
    if request["stage"] in {"review", "package"} and target_id is None:
        holds.append("Review requires an actual artifact with version and SHA-256")
    if request["stage"] == "render" and route.get("capability"):
        capabilities = unique_by(request.get("capabilities", []), "name")
        capability = capabilities.get(route["capability"], {})
        if capability.get("state") != "verified" or not capability.get("receipt", "").strip():
            holds.append(f"Verify {route['capability']} access and supply a current receipt")
    context = {key: request[key] for key in (
        "product_id", "campaign_id", "source_revision", "voice_profile", "sources", "claims", "voice_source_ids"
    )}
    context_digest = digest(json.dumps(context, sort_keys=True, separators=(",", ":")).encode())
    roles = ["evidence_editor"] if request["stage"] == "source" else [route["role"]]
    if request["stage"] in {"review", "package"}:
        roles.append("quality_reviewer")
    read_ids = sorted({c["source_id"] for c in claims.values()} | set(voice_ids))
    if request["stage"] == "source":
        read_ids = sorted(sources)
    specialists = [{"role": role, **REGISTRY["roles"][role],
                    "skill_path": f".agents/skills/{REGISTRY['roles'][role]['skill']}/SKILL.md"} for role in roles]
    support_ids = sorted({support_id for role in roles
                          for support_id in REGISTRY["roles"][role].get("support_skills", [])
                          if request["stage"] in REGISTRY["support_skills"][support_id]["stages"]})
    support_skills = [{**REGISTRY["support_skills"][support_id],
                      "skill_path": f".agents/skills/{REGISTRY['support_skills'][support_id]['skill']}/SKILL.md"}
                     for support_id in support_ids]
    target = artifacts.get(target_id)
    dependencies = dependency_bindings(target_id, sources, artifacts) if target else []
    review_digest = digest(json.dumps({"context": context_digest, "dependencies": dependencies},
                                      sort_keys=True, separators=(",", ":")).encode())
    subject = None if target is None else {
        "campaign_id": request["campaign_id"], "product_id": request["product_id"],
        "asset_id": target_id, "version": target["version"], "sha256": target["sha256"],
        "context_digest": review_digest,
    }
    preview = None
    if target:
        path = Path(target["path"])
        preview = {"path": str(workspace / path), "sha256": target["sha256"]}
        if path.suffix.lower() in {".md", ".txt", ".json", ".csv", ".srt", ".vtt"}:
            preview["content"] = data[target_id].decode("utf-8")
        else:
            preview["inspection_required"] = "Open the actual media; a path is not an inspection"
    return {
        "schema_version": "specialist-route/v1", "status": "held" if holds else "ready_for_protocol",
        "task_id": request["task_id"], "deliverable": request["deliverable"], "stage": request["stage"],
        "specialists": specialists, "support_skills": support_skills, "shared_contract": REGISTRY["shared_contract"],
        "rubric": route["rubric"], "segments": route.get("segments", []),
        "workspace_root": str(workspace),
        "read_set": [{**sources[sid], "resolved_path": str((workspace / sources[sid]["path"]).resolve())}
                     for sid in read_ids], "context_digest": context_digest,
        "affected_artifacts": affected, "dependency_bindings": dependencies, "subject": subject, "preview": preview,
        "requested_reviewer": request["requested_reviewer"], "holds": holds,
        "human_gates": ["claims_lock", "exact_script_copy_sketch", "each_rendition", "final_package"],
        "human_approval_granted": False, "generation_authorized": False,
        "evidence_boundary": "Offline projection only; host invocation, semantic truth, authentication and media quality are unverified",
    }


def validate_result(request, result, workspace):
    projection = route_request(request, workspace)
    validate_schema(result, "result.schema.json")
    if projection["status"] == "held":
        raise ValueError("Request is held: " + "; ".join(projection["holds"]))
    for key in ("task_id", "campaign_id", "product_id", "deliverable"):
        if result[key] != request[key]:
            raise ValueError(f"Result {key} mismatch")
    if result["subject"] != projection["subject"]:
        raise ValueError("Stale or mismatched artifact/context subject")
    if result["specialist"] not in {r["role"] for r in projection["specialists"]}:
        raise ValueError("Result from an unselected specialist")
    checks = unique_by(result["checks"], "criterion_id")
    if set(checks) != set(projection["rubric"]):
        raise ValueError("Every selected rubric criterion requires one result")
    if result["verdict"] == "recommend_review" and any(c["outcome"] == "fail" for c in checks.values()):
        raise ValueError("Failed checks require revision or a hold")
    if not set(result["claims_used"]) <= {c["id"] for c in request["claims"]}:
        raise ValueError("Unknown claim in result")
    if not set(result["voice_refs"]) <= set(request["voice_source_ids"]):
        raise ValueError("Unselected voice evidence in result")
    return {"status": "recommendation_only", "verdict": result["verdict"], "subject": projection["subject"],
            "human_approval_granted": False, "authentication_verified": False,
            "untested_checks": [key for key, check in checks.items() if check["outcome"] == "not_tested"]}


def check_decision_binding(request, decision, workspace):
    """A matching envelope is not an authenticated or current human event."""
    if not isinstance(decision, dict):
        raise ValueError("Decision comparison requires an object")
    projection = route_request(request, workspace)
    matches = bool(projection["subject"]) and decision.get("subject") == projection["subject"]
    return {"binding_matches": matches, "human_approval_granted": False, "authentication_verified": False,
            "event_applied": False, "reason": "Comparison only. Actual human identity, latest decision and event ordering are not verified."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["route", "validate-result", "check-binding"])
    parser.add_argument("request", type=Path)
    parser.add_argument("--workspace", required=True, type=Path)
    parser.add_argument("--result", type=Path)
    args = parser.parse_args()
    try:
        request = json.loads(args.request.read_text())
        if args.command == "route":
            result = route_request(request, args.workspace)
        else:
            if args.result is None:
                raise ValueError("--result is required")
            value = json.loads(args.result.read_text())
            result = (validate_result if args.command == "validate-result" else check_decision_binding)(request, value, args.workspace)
        print(json.dumps(result, indent=2))
        return 0
    except (ValueError, OSError, UnicodeError, jsonschema.ValidationError) as exc:
        print(json.dumps({"status": "refused", "error": str(exc).split("\n")[0], "human_approval_granted": False}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
