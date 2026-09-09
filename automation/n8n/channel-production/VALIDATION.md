# Preparation validation

Observed locally on 2026-09-08. This evidence covers preparation and file validation. It establishes no native specialist invocation, content quality, provider execution or authenticated human decision.

| Check | Result |
| --- | --- |
| `node automation/n8n/channel-production/test.mjs` | 23 cases passed, including execution of the built workflow's Code node. |
| `.venv/bin/python automation/n8n/channel-production/test_loader.py` | 5 cases passed using temporary files and the existing specialist router. |
| `python3 automation/n8n/channel-production/build_workflow.py --check` | Generated workflow matches its code, registry and schema. |
| Current four internal-test-product requests through loader, then `run.mjs` | `ready_for_operator`; four lanes; three selected source records per lane. |
| Human assignment / schedule | the requested reviewer's identifier / `consolidated_end`; review remains pending actual artifacts and the human. |
| Authority | Execution, publication, human approval and authentication remain false. |
| Independent review | One reviewer rechecked feedback/count/authority; a second rechecked schema and revision routing. Both bounded reviews passed after fixes. |
| n8n cloud execution | Not run. Importable workflow is inactive and has no credentials or provider node. |

The real input came from a since-removed example package's request folder. Source revision was `27826b0332fd1582108ac0081165a7dd360e7aa6`. Preparation digest was `119a9371be48dba104027d3eb3bc349b23af690de8da6bfe380aac34f2080a11`. The temporary inline-source payload was discarded after this check; the portable example remains fictional.

The test-first baseline returned `not_implemented` and failed the first assignment assertion. Loader fixtures also failed before implementation. Later focused checks reproduced malformed collection crashes, an uncaught schema error and an unrouted affected artifact. Independent review then found prototype-named field acceptance, changed-artifact drafts bypassing revision handling, and extra revision fields echoing caller authority flags. Each has a regression and the corrected cases pass.

## Change and review map

- `prepare.js` consumes the batch without external effects. Its tests target product/source isolation, actual inline source hashes, Unicode spans, voice/fact separation, revision subjects and authority flags.
- `load_requests.py` reuses `engine/scripts/specialist_route.py` on actual workspace files. The loader tests cover changed bytes, missing claims, wrong lane count and structured refusal.
- `build_workflow.py` embeds current route/schema data in inactive `workflow.json`. `--check` detects a stale generated file. The JavaScript suite executes the embedded node.
- `run.mjs` provides a local entry that runs that node; the real-batch smoke test exercised it. It exposes only Node crypto to the Code node.
- `request.example.json` contains invented text and no runtime IDs or credentials. The two READMEs explain the operator entry and future app/worker boundary. `PLAN.md` records the bounded implementation steps.

Existing engine code, role registry, host wrappers, global manifests and source packets were read but not changed. Root and the other specialists own the four prompt texts and output drafts. The durable retry counter and human authority store remain outside this preparation layer.
