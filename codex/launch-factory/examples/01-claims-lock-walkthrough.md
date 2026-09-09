# Example 01: Claims Lock walkthrough (fixture)

**All material below is the Quorum Desk mock GTM ship fixture**
(`engine/fixtures/mock-gtm-ship/`). Quorum Desk is a synthetic demo product,
**not** a real feature of any live product this runs for. Every claim shown
is labelled fixture.

## Input

One release folder, exactly as shipped in the fixture:

- `sources/loom_transcript.txt`: 2:25 walkthrough transcript (fixture)
- `sources/github_outline.md`: ship outline with contents and non-goals (fixture)
- `claim_hints.md`: allowed/forbidden seeds derived from sources only (fixture)
- `augment/` ZIP + one-pager, `emails/changelog-whats-new.md`, `footage_index.json` (fixture)

First ask: `Use Launch Factory. Run on this release folder.`

## What the run does before anything else

1. **Ingest.** List every file; note that footage pointers exist but no real
   video assets are shippable in this fixture.
2. **Retrieve.** Pull candidate claims from transcript + outline only.
   Demo assets (the ZIP, the one-pager) are **not** evidence: ADR 0001.
3. **Draft the Claims Lock card for Reviewer**, and stop. No adapter draft yet.

## The fixture Claims Lock draft (shape)

Allowed claims, each with an evidence span from fixture sources:

| Claim (fixture) | Evidence |
|---|---|
| Quorum Desk helps decide the next move on a live B2B opportunity (advance / validate / recover / hold / disqualify / exit) | transcript [00:45]-[01:10] |
| Every claim is tagged: observed, buyer-stated, inferred, assumed, unknown, disputed, disconfirmed | transcript [00:45] |
| It does not send mail, update CRM, or schedule meetings without separate authorized tooling | transcript [01:35] |
| Install doors: Codex skill folder + Claude ZIP | transcript [02:00], outline "Contents" |

Forbidden (from `claim_hints.md`, fixture):

- Any pricing, seat counts, or roadmap dates
- Win-probability scores or guaranteed outcomes
- That slots 1/5/6 Launch Factory outputs are complete from this fixture

Kill-switch: not armed. Slots 1/5/6: **HOLD**, named on the card.

## Expected stop point

The run hands Reviewer the card (`reviewer/claims-lock.md` shape) and waits. Adapters
fan out only after the written Claims Lock approve. A Slack thumbs-up does not
count.

**Failure shape (do not do):** drafting the blog before the lock; adding a
"Quorum Desk saves hours" claim with no span; treating the fixture ZIP's
existence as proof of anything.
