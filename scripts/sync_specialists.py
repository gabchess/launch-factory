#!/usr/bin/env python3
"""Generate native project entry points from the shared specialist registry."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = json.loads((ROOT / "engine/specialists/registry.json").read_text())


def generated_files():
    result = {}
    for role, spec in REGISTRY["roles"].items():
        skill = spec["skill"]
        guide = Path(spec["reference"]).name
        finishing = ""
        for support_id in spec.get("support_skills", []):
            support = REGISTRY["support_skills"][support_id]
            finishing += f"\nFor stages {', '.join(support['stages'])}, read [{support['skill']}](../../../{support['source']}) when finishing or inspecting motion. Preserve the existing story approval; new script or paid rendition authority remains separate.\n"
        if spec.get("production_protocol"):
            finishing += f"\nFor actor-led films, read [the one-rendition production protocol](../../../{spec['production_protocol']}) and its prompt/job contracts. A standalone film uses production-job/v1 directly with this same role; the campaign specialist-request/v1 social-video route keeps the campaign's 30-second rubric. Preserve locked speech, named actor/voice references and the explicit whole-film audio plan. Return each new sample to human review.\n"
        body = f'''---
name: {skill}
description: "{spec['description']} Use for the Launch Factory {role.replace('_', ' ')} stage, including explicit review of that deliverable. Return work to the launch-factory operator; do not approve, publish or execute providers."
---

# {role.replace('_', ' ').title()}

Read [the shared protocol](../../../engine/specialists/CONTRACT.md) and [this role's bank](../../../engine/specialists/references/{guide}) before working. These paths require the full repository opened as the project. Do not copy this wrapper alone into a global skill directory.

Consume the operator's specialist-request/v1 packet plus its validated route projection. Resolve release inputs with the projection's `workspace_root` and `read_set` `resolved_path` fields. Read only the selected product facts, voice samples and artifact. Reject wrong-product or missing evidence. Follow this role's protocol for the requested stage and return complete draft content, an exact-version review recommendation, or a named hold. Cite claim IDs and supplied source spans; use voice samples only for expression.

For a review, return specialist-result/v1 with specialist `{role}` and every routed rubric item. Mark checks that did not run `not_tested`. The actual human reviewer is assigned in the packet; you cannot impersonate that person or apply a decision. Preserve exact artifact hashes and dependency boundaries. The operator executes any separately authorized tools and carries the result to the next gate.
{finishing}
'''
        body = body.rstrip() + "\n"
        for host in (".agents", ".claude"):
            result[f"{host}/skills/{skill}/SKILL.md"] = body
            cases = {"cases": [
                {"prompt": f"Use {skill} for the supplied Launch Factory packet.", "should_trigger": True},
                {"prompt": f"Review this Launch Factory {role.replace('_', ' ')} stage with its exact artifact hash.", "should_trigger": True},
                {"prompt": f"The Launch Factory operator selected {skill}; complete its requested stage.", "should_trigger": True},
                {"prompt": "Explain Python list comprehensions.", "should_trigger": False},
                {"prompt": "Change my desktop background.", "should_trigger": False},
                {"prompt": "Approve and publish every campaign without the human reviewer.", "should_trigger": False},
            ]}
            result[f"{host}/skills/{skill}/trigger-evals.json"] = json.dumps(cases, indent=2) + "\n"
        context_instruction = "Use the operator's request plus validated route projection, including workspace_root and resolved_path read set. "
        if spec.get("production_protocol"):
            context_instruction = (
                "For campaign work, use specialist-request/v1 plus its route projection, workspace_root and resolved_path read set. "
                "For a standalone film, use production-job/v1 plus its production projection and resolve file bindings inside that projection's workspace_root. "
            )
        instructions = (
            f"You are the Launch Factory {role.replace('_', ' ')}. "
            f"Read .agents/skills/{skill}/SKILL.md, engine/specialists/CONTRACT.md and {spec['reference']}. "
            + context_instruction +
            "Return concrete draft content or an exact-version recommendation. "
            "Do not run providers, spend, write approval state, impersonate the human reviewer, publish or send. "
            "Missing tools or evidence require an explicit hold. The operator performs authorized tool work."
        )
        if spec.get("support_skills"):
            instructions += " When the route returns support_skills, read their selected skill paths and canonical protocols for the requested finishing stage."
        if spec.get("production_protocol"):
            instructions += f" For actor-led films, read {spec['production_protocol']} and follow its exact-script, one-sample and per-generation review contract."
        result[f".codex/agents/{spec['agents']['codex']}.toml"] = (
            f"name = {json.dumps(spec['agents']['codex'])}\n"
            f"description = {json.dumps(spec['description'])}\n"
            'sandbox_mode = "read-only"\n'
            f"developer_instructions = {json.dumps(instructions)}\n"
        )
        result[f".claude/agents/{spec['agents']['claude']}.md"] = (
            f"---\nname: {spec['agents']['claude']}\ndescription: {json.dumps(spec['description'])}\n"
            "tools: Read, Glob, Grep\nmodel: inherit\n---\n\n" + instructions + "\n"
        )
    for support in REGISTRY.get("support_skills", {}).values():
        for host in (".agents", ".claude"):
            path = f"{host}/skills/{support['skill']}"
            result[f"{path}/SKILL.md"] = f'''---
name: {support['skill']}
description: "{support['description']} Use with the existing video lead or motion designer for an approved finishing revision."
---

# Short motion finishing

Read and follow [the shared finishing protocol](../../../{support['source']}). It contains cue-sheet and Caption JSON contracts, provider-neutral provenance and audio/visual review rules. Keep the entire repository available. This support skill adds no new agent role and grants no approval or provider authority.
'''
            result[f"{path}/trigger-evals.json"] = json.dumps({"cases": [
                {"prompt": "Polish this approved ten-second motion edit with quiet music and timed SFX.", "should_trigger": True},
                {"prompt": "The video lead needs kinetic type and an exact cue sheet for the approved cut.", "should_trigger": True},
                {"prompt": "Review speech Caption JSON and the actual provider manifest for this motion edit.", "should_trigger": True},
                {"prompt": "Write a blog article about captions.", "should_trigger": False},
                {"prompt": "Approve the new paid avatar script without showing the human.", "should_trigger": False},
                {"prompt": "Choose a new product positioning strategy.", "should_trigger": False}
            ]}, indent=2) + "\n"
    for host in (".agents", ".claude"):
        result[f"{host}/skills/launch-factory/SKILL.md"] = '''---
name: launch-factory
description: "Run a source-grounded Launch Factory campaign through deliverable specialists and exact-version human review. Use for a release package, LinkedIn post, social video, login animation or campaign calendar."
---

# Launch Factory project entry point

Read and follow [the canonical operator](../../../codex/launch-factory/SKILL.md). The full repository must be the current project so its engine, specialist banks and native roles are reachable. Route the requested stage, then invoke the chosen specialist protocol. If native delegation is unavailable, read that specialist's skill and bank and perform the role inline, disclosing the fallback. Never treat a route, file installation or model recommendation as human approval.
'''
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    mismatches = []
    for relative, text in generated_files().items():
        path = ROOT / relative
        if args.check:
            if not path.exists() or path.read_text() != text:
                mismatches.append(relative)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
    if mismatches:
        print("Entry point drift:\n" + "\n".join(mismatches))
        return 1
    print(f"{len(generated_files())} generated entry-point files {'match' if args.check else 'written'}; native host execution remains untested")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
