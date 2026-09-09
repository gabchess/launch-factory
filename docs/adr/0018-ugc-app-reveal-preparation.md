# ADR 0018: reusable UGC app reveal and n8n preparation

Date: 8 September 2026. Status: implemented for Gabe's request to save the approved film recipe and add it to Launch Factory's n8n setup.

The `ugc-app-reveal` recipe captures the approved actor-and-product-film production method. It belongs to the existing video lead and local `product-heygen-pipeline` skill. Its five named prompts and binding requirements remain in one canonical directory. Each new product supplies its own brand, facts, assets and human decisions. The approved example's media, live account IDs and private conversation are excluded from the portable recipe.

Add an importable n8n preparation subworkflow under `automation/n8n/ugc-app-reveal/`. It embeds the canonical recipe, checks the supplied brief and returns the full prompts, source content, provenance fields and review requirements. The caller receives `needs_inputs` or `ready_for_operator`. It does not submit a provider job, authenticate an approval, pause for a callback or publish. No ChatCut HTTP API or transferable desktop OAuth session is assumed.

The parent app and provider worker remain separate implementation work. They must resolve actual human authority, check file bytes, enforce spend limits and commit idempotent dispatch through a durable store. Existing production-job validators retain their scope. This preparation step never writes a legacy human-confirmed flag or manufactures approval events.

The standalone recipe can describe a film up to 60 seconds. the target social slot remains capped at 30 seconds. A finished product-vision film does not establish live product functionality or live transaction execution. Production provenance and presentation notes retain those facts without forcing unrequested on-screen labels.

Local and n8n test evidence belongs to each installation. A successful preparation run proves that inputs became a consistent work packet. The six-output app and paid video rendering require their own end-to-end evidence.
