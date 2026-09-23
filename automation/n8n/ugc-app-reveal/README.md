# UGC app reveal in n8n

This subworkflow packages the approved `ugc-app-reveal` recipe for the Launch Factory video lead. It runs input checks, includes the five complete prompts and carries source content alongside version/hash references. A marketing app can call it through its parent n8n workflow.

The current component prepares work. The agent host still performs the video work through its verified tools. An authenticated app approval store and an API worker are required before unattended provider dispatch can run. Desktop MCP sessions do not supply those credentials.

## Use the skill today

Invoke `product-heygen-pipeline` with recipe `ugc-app-reveal` and the new product source. Inside the full Launch Factory repository, the existing `lf-video-production` entry point routes to the same recipe. Read [the recipe](../../../engine/specialists/video-production/recipes/ugc-app-reveal/README.md) and its prompt index.

## Install or call the n8n step

1. Import `workflow.json` into your own n8n project. It contains no account IDs, credentials or real production assets. The import starts inactive.
2. From the parent workflow, add Execute Sub-workflow and select **Launch Factory | UGC App Reveal | Prepare**. Send one request per input item, shaped like `request.example.json`.
3. Replace all fictional example bindings with the release's actual source text, workspace-relative or HTTPS reference, version and SHA256. Do not send API keys, cookies, private chat transcripts or wallet secrets. Bindings carry evidence; a field named `approved_scope` does not establish approval.
4. Branch on the returned `status`. Show `needs_inputs.issues` to the operator when inputs are missing. For `ready_for_operator`, use `run_context`, `bindings` and the five prompts as planning context. The operator prepares the applicable `specialist-request/v1` campaign packet or `production-job/v1` film packet before invoking the video lead. This preparation result is not a replacement for those existing contracts. Keep the source text separate from the prompt instructions.
5. The operator resolves the named review stages against actual human decisions. Show the asset itself and its source/history at each applicable gate. Record decisions against the exact file hash. The review queue describes required gates; it does not suspend an n8n execution or authenticate a decision.

The input needs `campaign_id`, `request_id`, `recipe_id`, `deliverable_scope`, `product`, `format`, `brief` and `bindings`. `standalone_product_film` allows up to 60 seconds. `campaign_social_video` is this recipe's enum name for the 30-second social target, defined in `engine/specialists/video-production/recipes/ugc-app-reveal/recipe.json`. Eight required content bindings come from `recipe.json`. Stage-specific inputs, such as dialogue timestamps or a listing manifest, are resolved before that prompt runs.

The result always sets `execution_authorized` and `publishing_authorized` to false. Hash fields receive syntax checks here; the operator must verify actual bytes and claims. Supplied booleans cannot approve a render. The bundle hash identifies the embedded recipe and prompts; it does not authenticate the caller.

## Connect the later worker

The parent app must authenticate the reviewer and keep one durable authority store. Before paid dispatch, verify current input hashes, the permitted review schedule, the selected provider account and the current quote. Deduplicate submissions using the request and bound inputs; commit approval, state and dispatch intent atomically. Reconcile an uncertain submitted job before retrying it. Use the provider's actual supported API or MCP worker, recording which tool produced each asset. Do not invent a ChatCut HTTP endpoint.

Receive the rendered asset, source lineage and job receipt in the same campaign. Show the full playable result for review. A rejection returns to the affected prompt with feedback; preserve accepted actors, speech and unrelated scenes. The final waitlist CTA remains a brief field. Nothing publishes automatically.

## Rebuild and check

From the repository root:

```bash
python3 automation/n8n/ugc-app-reveal/build_workflow.py
node automation/n8n/ugc-app-reveal/test.mjs
```

The builder embeds the canonical recipe and prompts in `workflow.json` and `workflow.sdk.js`. Rebuild after a recipe edit and update the installed n8n workflow. The SDK source can be validated with n8n's `validate_workflow` tool before creation. Pin only the trigger for an n8n test; the Code node must run. Tests consume no video or language-model credits. Importing the JSON does not prove a provider call, a human review or a finished app.
