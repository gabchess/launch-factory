#!/usr/bin/env python3
# STRUCTURAL_INTEGRITY_ONLY — regenerates release-manifest.json and
# documentation-manifest.json file lists (sha256 + bytes). This script never
# publishes, never alters claim boundaries, and never touches content files.
#
# Inclusion policy (v0.2.0 — repo root IS the pack, ADR 0012):
#   - release-manifest.json: ALL shipped files under the repo root
#     (envelope + codex/ + claude/ ZIP + engine/ + reviewer/ + docs/ +
#     maintainer-source/ + voice-bank/ + this script), EXCLUDING:
#       * .git, .venv, .pytest_cache, __pycache__, .DS_Store
#       * runs/ and packages/ (run outputs, not pack surface)
#       * BOTH manifest files themselves (self-reference fix, 0.1.1 —
#         circular hashes cannot validate).
#     Dev-harness files at root (tests/, pytest.ini, requirements.txt,
#     run.sh, SHOW-ME.md, AGENTS.md) ARE included: the repo-link door
#     ships the whole working tree.
#   - documentation-manifest.json: documentation surface only — .md/.txt files
#     anywhere in the included tree, EXCLUDING .git, both manifest files,
#     engine/ internals other than engine/README.md and engine/adapters/*.md,
#     and dev-history docs (docs/2026-09-07-*.md are design/plan copies and
#     stay release-manifest-only). Non-doc files (json, zip, py, yaml,
#     .gitkeep) are not listed here.
#
# Run from anywhere:  python3 scripts/regen_manifests.py

import hashlib
import json
import os
import sys

PACK_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFESTS = ("release-manifest.json", "documentation-manifest.json")
EXCLUDE_DIRS = {
    ".git", ".venv", ".pytest_cache", "__pycache__", "runs", "packages",
}

EVIDENCE_BOUNDARY = (
    "Proves pack file integrity and includes the specialist 0.3.1 project "
    "entry points, protocols and offline routing checks (ADR 0017). Does not "
    "prove host invocation, provider access, human authentication, semantic "
    "quality or customer outcomes. Historical fixtures and the Claude 0.2.0 "
    "ZIP retain their legacy scope. Voice-bank content remains interim (ADR 0015). "
    "See HOST-MATRIX.md."
)


def walk_files():
    out = []
    for dirpath, dirnames, filenames in os.walk(PACK_ROOT):
        dirnames[:] = sorted(d for d in dirnames if d not in EXCLUDE_DIRS)
        for fn in sorted(filenames):
            if fn == ".DS_Store":
                continue
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, PACK_ROOT)
            if rel in MANIFESTS:
                continue  # self-reference fix: manifests never list themselves
            out.append(rel)
    return sorted(out)


def digest(rel):
    with open(os.path.join(PACK_ROOT, rel), "rb") as f:
        data = f.read()
    return hashlib.sha256(data).hexdigest(), len(data)


def is_doc(rel):
    if not rel.endswith((".md", ".txt")):
        return False
    if rel.startswith("engine/") and not (
        rel == "engine/README.md" or rel.startswith(("engine/adapters/", "engine/specialists/"))
    ):
        return False
    return True


def main():
    files = walk_files()
    doc_files = [f for f in files if is_doc(f)]

    rel_path = os.path.join(PACK_ROOT, "release-manifest.json")
    doc_path = os.path.join(PACK_ROOT, "documentation-manifest.json")
    with open(rel_path) as f:
        release = json.load(f)
    with open(doc_path) as f:
        docs = json.load(f)

    release["version"] = "0.2.0"
    release["evidence_boundary"] = EVIDENCE_BOUNDARY
    release["notes"] = (
        "v0.2.0: pack envelope at repo root (ADR 0012 repo-link door); "
        "engine/ = single SoT (Option B); one release record + loop-shaped "
        "skill; Campaign Plan slot 7 (ADR 0016); interim Voice Bank "
        "(ADR 0015); legacy run.sh door (ADR 0014). Specialist layer 0.3.1 "
        "adds native project entry points and offline routing (ADR 0017); "
        "the retained Claude ZIP is not refreshed. Manifests exclude "
        "themselves, runs/, and packages/; regenerate with "
        "scripts/regen_manifests.py (STRUCTURAL_INTEGRITY_ONLY)."
    )
    release["files"] = [
        {"path": p, "sha256": s, "bytes": b} for p in files for s, b in [digest(p)]
    ]

    docs["version"] = "0.2.0"
    docs["files"] = [
        {"path": p, "sha256": s} for p in doc_files for s, _ in [digest(p)]
    ]

    for path, obj in ((rel_path, release), (doc_path, docs)):
        with open(path, "w") as f:
            json.dump(obj, f, indent=2, ensure_ascii=False)
            f.write("\n")

    print(
        f"release-manifest.json: {len(release['files'])} files; "
        f"documentation-manifest.json: {len(docs['files'])} files; "
        f"version 0.2.0; manifests self-excluded."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
