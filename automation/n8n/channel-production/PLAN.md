# Channel preparation implementation plan

> Implement inline within the assigned directories. Current user authorization covers this preparation layer and drafting all four outputs before consolidated review.

**Goal:** Prepare one consistent batch for blog, five email segments, changelog and popup with verifiable source bindings and bounded revision instructions.

**Architecture:** A local loader calls the existing Python specialist router on each request and inlines only the selected text inputs. The n8n Code node checks the four request shapes, source bytes/spans and common campaign context, then returns operator assignments. It owns no provider connection or approval ledger.

**Stack:** Existing Python/jsonschema router, Node built-in crypto, inactive n8n subworkflow.

**Source contract:** `engine/specialists/request.schema.json` and `engine/specialists/CONTRACT.md`.

- [x] Add focused failing cases in `test.mjs` for missing/mixed packets, five segments, wrong hashes/spans, voice-as-fact, revision scope/ceiling and no authority escalation.
- [x] Implement `prepare.js`; generate its route/schema bundle from the existing registry in `build_workflow.py`.
- [x] Add `load_requests.py` and offline fixture checks that exercise `route_request` using real files.
- [x] Build inactive `workflow.json`; test its actual embedded Code node, with missing crypto returning a named hold.
- [x] Document exact input/output, prompt paths, consolidated review and future adapter/approval responsibilities in the assigned READMEs.
- [x] Run only these focused checks, inspect links and whitespace, and send the frozen files for independent review.

No provider calls, cloud creation, global manifests, board mutations, commit or push are part of this implementation.
