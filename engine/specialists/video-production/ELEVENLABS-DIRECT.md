# Direct ElevenLabs speech adapter

Use the recipient's own ElevenLabs account when they request ElevenLabs speech. This preference selects an account route; it does not establish authentication, credits, voice access or an operational worker. The `inference.sh` wrapper is a separate service and billing route. A paid ElevenLabs account does not establish an inference.sh allowance. Use that wrapper only when the user selects it.

## Select speech for the role

| Requested role or branch | Speech source |
| --- | --- |
| The owner's educator or founder persona | Their existing approved clone, resolved by current account voice ID. Confirm ownership and the intended persona from the brief. |
| Fictional UGC actor | An appropriate licensed catalog voice on the selected account, or organic actor speech when the user explicitly permits it. |
| Approved organic provider audio | Preserve the returned actor speech and inspect its exact words. Do not synthesize a replacement by default. |
| Silent scene | No speech synthesis. Keep the separate whole-film audio plan intact. |

A person's clone is not the default voice for fictional customers. Keep personal voice preferences and actual IDs in the release workspace. The portable example supplies no owner's clone or live account requirement. A catalog name is a search hint; use the ID returned by the selected account. Organic video speech and a direct ElevenLabs track have different source records.

## Use the direct route

Use the current hosted ElevenLabs MCP at `https://api.elevenlabs.io/v1/mcp` with its OAuth flow for an interactive host, or a verified direct API adapter with the recipient's own key for automation. Confirm current controls and account access. The earlier local MCP package is deprecated; use that legacy package only if the user explicitly selects it. Record installation, host discovery, read-only account/voice access and a real synthesis output separately. A configured server alone proves no successful speech generation.

Resolve the requested voice from that account, keep the provider-specific voice ID and model/settings in the release workspace, and pass the exact already-approved text. Do not improve, abbreviate or rewrite the words. Preserve settled story, cast and voice decisions within their scope. A different voice or newly generated track is a new artifact to inspect; show every new video rendition to the actual human.

For an approved single-output run, explicitly send `generations_count: 1` to the hosted `creative_generate_speech` tool. Its live schema checked on 8 September 2026 defaults to four variations, with cost scaling by count. Keep the count at one for both an `estimate_only: true` quote and the separately authorized generation. Use the current hosted fields `prompt`, `model_id`, `voice_id` and `context`; the older wrapper's `text`/`voice` payload is a different tool shape. Read status with the returned flow/session IDs instead of submitting a second generation to retry.

Save the returned audio, request/job reference when supplied, actual producer, gateway, model and SHA-256. For a video provider's approved-audio branch, bind those exact bytes as `shot.speech_input`. Check that the selected video route accepts the audio reference, then keep the speech input in its output lineage. Never label direct ElevenLabs audio as inference.sh or organic ChatCut speech. Listen for pronunciation and exact spoken numbers before caption timing or lip-sync review.

Keep credentials in the host's approved secret mechanism. The augment ships no API key, account cookie, personal voice ID or account configuration. Inspect current price/credit evidence before spend and retain the job's existing ceiling. If direct access is unavailable, report that state; do not silently reroute paid synthesis through another service.

## Evidence status

The hosted endpoint and OAuth flow are documented in [ElevenLabs hosted MCP](https://elevenlabs.io/docs/eleven-agents/operate/hosted-mcp). The [official MCP repository](https://github.com/elevenlabs/elevenlabs-mcp) marks the earlier local package deprecated. Both were checked on 8 September 2026. This adapter is a portable instruction path. Current installation and runtime evidence belong to the recipient's separate preflight receipt. No synthesis was performed by this skill update. A later n8n worker must establish its own supported credentials and access; desktop MCP status is not transferable proof.

In the author's Codex session on that date, the `elevenlabs` connection and fresh tool discovery worked through `https://api.us.elevenlabs.io/v1/mcp`, with a matching `oauth_resource`. The discovered tools included `creative_list_voices` and `creative_generate_speech`; OAuth scopes included `convai_read`, `text_to_speech` and `speech_history_read`. This proves that session's connection and tool discovery, with zero synthesis performed. Each recipient still selects their account/region, keeps endpoint and OAuth resource aligned, and records their own setup and output evidence. No credentials or personal voice IDs are distributed here.
