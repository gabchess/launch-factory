# Reviewer seat (approval gate)

Reviewer is the VP Marketing HITL gate. This file defines **what the Reviewer gate
checks** and what counts as approval. The skill never acts as Reviewer: it
prepares cards for a human Reviewer (or delegated authorized human) to fill.

## The three gates (in order)

1. **Claims Lock** (`reviewer/claims-lock.md`): once per campaign, before any
   adapter fan-out.
2. **Spot-check** (`reviewer/spot-check.md`): on the first **real** (non-HELD)
   draft; with slots 1/5/6 held, that is the blog (slot 2).
3. **Pack approve** (`reviewer/pack-approve.md`): copy + creative for the whole
   package; WIP=1 in `awaiting_reviewer`.

## What the gate checks

### Claims traceability
- Every allowed claim carries an evidence span (transcript / outline /
  approved docs). Unsupported claims are forbidden or held, with the missing
  evidence named.
- Forbidden list present and honored in drafts (no pricing/limits/roadmap
  invention; no "saves $" without source; no auto-publish claims).
- Demo assets never used as evidence (ADR 0001). Fixture material stays
  labelled fixture.

### Voice
- Reads like the product's own brand wrote it: calm, precise, marketer-operable.
- No hype the evidence cannot carry; no competitive smear; claims match the
  locked wording.

### Forbidden list
- Any draft sentence matching a forbidden claim → Request Changes on that
  named artifact only. No silent rewrite-as-approve.

### Held-slot honesty
- Slots 1/5/6 appear as HELD stubs with reasons: never as approved assets,
  never quietly omitted.
- The package never claims "all six review-ready" while holds stand.

## What counts as approval

- **Approval = a written lock on the card.** Checkbox marked, decision line
  filled, dated, attributable to Reviewer (or named delegate).
- **Slack thumbs do not count.** Emoji, verbal "sounds good," or forwarded
  praise are not gate decisions; status stays `awaiting_reviewer`.
- **Request Changes** names the slot(s) to regenerate; the writer seat fixes
  only those, then re-submits.
- Kill-switch: Reviewer can arm it at Claims Lock, adapters stay cold, campaign
  status → `needs_source_fix`.

## What Reviewer's approval does NOT authorize

- Publishing to CMS, changelog, login, in-app, or social.
- Sending email or CRM/ESP campaigns (sandbox export only after pack approve,
  and only with separately authorized tooling).
- Treating held slots as done, or fixture claims as live product facts.

Approval means the copy and creative are review-ready and claim-safe. It does
not mean shipped. Nothing in this pack auto-publishes.
