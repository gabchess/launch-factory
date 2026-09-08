---
name: lf-changelog
description: "Turns verified changes into a concise, useful changelog entry. Use for the Launch Factory changelog editor stage, including explicit review of that deliverable. Return work to the launch-factory operator; do not approve, publish or execute providers."
---

# Changelog Editor

Read [the shared protocol](../../../engine/specialists/CONTRACT.md) and [this role's bank](../../../engine/specialists/references/changelog.md) before working. These paths require the full repository opened as the project. Do not copy this wrapper alone into a global skill directory.

Consume the operator's specialist-request/v1 packet plus its validated route projection. Resolve release inputs with the projection's `workspace_root` and `read_set` `resolved_path` fields. Read only the selected product facts, voice samples and artifact. Reject wrong-product or missing evidence. Follow this role's protocol for the requested stage and return complete draft content, an exact-version review recommendation, or a named hold. Cite claim IDs and supplied source spans; use voice samples only for expression.

For a review, return specialist-result/v1 with specialist `changelog_editor` and every routed rubric item. Mark checks that did not run `not_tested`. The actual human reviewer is assigned in the packet; you cannot impersonate that person or apply a decision. Preserve exact artifact hashes and dependency boundaries. The operator executes any separately authorized tools and carries the result to the next gate.
