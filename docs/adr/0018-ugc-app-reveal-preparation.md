# ADR 0018: UGC app reveal preparation

Date: 2026-09-08. Status: implemented as an optional preparation workflow.

The `ugc-app-reveal` recipe gives the video lead a reusable actor-and-product-film method. Its prompts and binding requirements live in one canonical directory. Each product supplies its own facts, brand assets and review decisions.

The n8n subworkflow under `automation/n8n/ugc-app-reveal/` embeds that recipe. It checks a supplied brief and returns prompts, source content and review requirements with `needs_inputs` or `ready_for_operator` status. It does not submit provider jobs or publish assets.

A provider worker would need authenticated human decisions, verified media, spend limits and durable job dispatch. Those services remain outside this preparation workflow.

The standalone recipe supports films up to 60 seconds. The v2 social-video builder has a separate 30-second limit. Each installation must verify its own rendering and review flow; a successful preparation run establishes only that it produced a consistent work packet.
