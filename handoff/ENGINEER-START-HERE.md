# Engineer handoff: current Launch Factory build

This is the technical handoff for maintaining this repository. Read it before the older
SOP files in this directory; those are superseded, and each says so. No credentials or
approval events are included in this handoff.

See [docs/HUMAN-GAPS.md](../docs/HUMAN-GAPS.md) for what still needs a human, in plain language. The supplied
brief sets no numeric social-video duration cap; this project uses its own 30-second
target.

## What is available

The full repository is an agent-operated launch workflow: a Codex/Claude operator,
specialist roles, local validators, two importable n8n preparation workflows, and the
`build_package.py` script that assembles a review package from a release folder. No
pre-built example package ships in this repository; see [docs/REFERENCE.md](../docs/REFERENCE.md)
for the exact package shape and `packages/README.md` for where a built package lands.

The review web page a built package generates displays real local content and saves
review notes tied to a file version, in the browser. It does not run a model, and it does
not authenticate who wrote a note. The n8n workflows prepare source-bound work packets;
they do not dispatch a provider worker, resume long jobs, or apply approval events.
Building those pieces is the next engineering work.

## Operate it through Codex

Open the full checkout as the project and follow [Codex installation](../docs/INSTALL-CODEX.md). The operator entry is [launch-factory](../codex/launch-factory/SKILL.md). Generated role wrappers live in `.agents/skills/` and `.codex/agents/`; copying a single skill folder omits its engine and references.

For a new product, create a campaign workspace. Ingest its source documents, retain
immutable source bytes and source revision, extract claim spans, select its voice
reference, and identify the human reviewer. Reviewer is the required approver for the
target product's work.

Where native role delegation is available, the host invokes the selected specialist.
Otherwise the operator reads the same role protocol and performs the work inline,
reporting that path. Role discovery and schema validation are recorded separately from
provider execution.

## Prepare the four n8n lanes

```bash
.venv/bin/python automation/n8n/channel-production/load_requests.py \
  --workspace RELEASE_WORKSPACE \
  --batch-id my-channels-v1 \
  --requests \
    RELEASE_WORKSPACE/requests/blog.json \
    RELEASE_WORKSPACE/requests/email_segments.json \
    RELEASE_WORKSPACE/requests/changelog.json \
    RELEASE_WORKSPACE/requests/in_app_popup.json \
  --output /tmp/channel-input.json
node automation/n8n/channel-production/run.mjs \
  /tmp/channel-input.json /tmp/channel-work-packets.json
```

Import [Four Channels Prepare](../automation/n8n/channel-production/workflow.json) into your n8n instance. A parent calls it with Execute Sub-workflow and passes the validated batch. Follow the [workflow README](../automation/n8n/channel-production/README.md) for the envelope, source checks, revision rules and required `crypto` built-in. Leave it inactive until a controlled host test passes.

The separate [UGC App Reveal preparation](../automation/n8n/ugc-app-reveal/README.md) supplies the video lead's five prompts. A prior build used ChatCut performances and assembly, HyperFrames scenes, and one Higgsfield enhancement to fill this route. An in-house HeyGen/HyperFrames/Remotion adapter is an implementation direction. It must establish its own working output before anyone describes it as equivalent to that route.

## Credentials and configuration for the next stage

An engineer configures the recipient's own accounts once. Routine operators should then use the app without handling keys.

| Component | Configuration owner | Where it belongs |
| --- | --- | --- |
| n8n | Recipient instance URL, access credentials, workflow IDs | Backend secrets and n8n credential store |
| Language model | Recipient provider key and selected model | Worker secret store |
| Video / animation | Verified provider access, templates, render worker and job callbacks | Worker adapters; never assumed from an installed MCP |
| Voice | Direct ElevenLabs account key and selected voice ID, or verified organic provider audio | Worker secret store; choose the voice for the actual speaker |
| Artifacts | Storage location, access policy and retention | Backend configuration |
| Human review | Auth provider, reviewer assignment and durable event store | Backend configuration and database |
| Delivery | CMS/ESP credentials only when export adapters are implemented | Server-side draft/export adapters |

A project owner's own cloned voice is for that person's own founder or educator dialogue, never for a fictional UGC speaker. Fictional UGC speakers use a separately chosen voice. The reusable instructions retain this preference. The handoff includes no account keys or implicit access to anyone's paid subscriptions.

Missing configuration should produce a useful setup state in the app. Do not present a silent chat as a working integration. Provider account identity, access and cost must be verified before each paid generation route is first used.

## Next implementation slice

Build one working app-to-worker path before adding every output to the UI:

1. Intake a source URL and brief through an authenticated app endpoint. Retrieve the actual source and record its revision. Return a campaign ID.
2. Dispatch the blog packet to the worker. Save job status and the actual draft, then show the full content in the app.
3. Persist the assigned human's decision against the campaign, asset, version, content hash and source/voice context. Validate ownership and reject stale or duplicate transitions.
4. Request a small revision. Retry only the affected asset, preserve its history and return the new version for review. Confirm the state survives a browser reload.
5. Extend the verified path to five emails, changelog and popup, then asynchronous media jobs. Apply bounded retries and a cost ceiling before spending.
6. Export only the exact reviewed package. Version 1 does not auto-publish.

Replit or Base44 can supply the user interface and application host after a thin slice verifies authenticated requests, background work, callbacks and persistent state. The repository's [app scope decision](../docs/adr/0019-testable-app-and-next-milestone.md) remains the product target. The latest user instruction authorizes setup and testing next; it does not establish that those runtime paths are already implemented.

## Acceptance for a new build

The operator must complete source ingest, the required human decisions, output previews,
and a package build end to end. A refresh must preserve progress. Errors must name the
failed step and a recoverable action. Record provider job receipts and actual output
hashes for any real generation run.

## Verification commands

```bash
.venv/bin/pytest -q
python3 scripts/sync_specialists.py --check
node automation/n8n/ugc-app-reveal/test.mjs
node automation/n8n/channel-production/test.mjs
.venv/bin/python automation/n8n/channel-production/test_loader.py
python3 automation/n8n/channel-production/build_workflow.py --check
./run.sh engine/fixtures/demo-release
```

A structural pass does not grade copy, authenticate a reviewer, or prove an external API
worked.
