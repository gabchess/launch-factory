# ADR 0019: testable app after completing the output method

Date: 8 September 2026. Status: accepted planning direction from the user's latest request; app implementation and deployment are unfinished.

The user asked to complete the four remaining output categories, connect the complete n8n workflow and then create an app on Base44 or Replit that the client can test without an engineer in the loop. This updates the earlier disposable, presenter-only app assumption. The production interface must return useful status and configuration guidance rather than silently failing when an API key is absent.

Keep the sequence: validate content and media methods with internal product inputs; encode the reviewed methods as portable skills/prompts; implement worker dispatch and durable review state; expose the flow through the selected app; verify a full operator journey and record the demonstration. One thin app-to-worker slice is required before expanding the entire UI, so host and callback limitations surface early in the app phase.

An initial engineer configures own-account credentials and infrastructure. A marketing, product or development operator must then complete routine intake, preview, correction, approval and package download without an engineer acting behind the chat. The provider worker runs outside browser requests when jobs are long. Progress and pending human decisions survive reloads.

The six-output trial and a coherent campaign remain the target. Two approved creative renditions from an earlier internal run establish two creative methods. They do not prove all target format requirements or an end-to-end run. Historical fixture and sample approvals remain historical.

Keep trial access bounded by explicit account, time and cost controls. The existing budget ceiling does not grant unlimited hosting or retries. Pick Base44 or Replit after checking a real authenticated request, background job, callback and persisted review against the intended deployment. The current request authorizes planning, checkpointing and repository push; it does not activate providers or deploy the app during this checkpoint.

The handoff remains the full reusable repository/augment, n8n setup and own-account instructions. Final app packaging, hosting and support commitments must be stated separately when delivered. Never represent a provider-assisted demo as an independently implemented provider service.
