# Universal copy/paste workflow

Host-agnostic manual run: the exact steps and prompts a marketer can paste
into **any** chat host to take one release folder through
Claims Lock → adapters → validation → Reviewer cards by hand. No engine, no
Python, no files required. Fail closed at every gate: if a step cannot be
completed honestly, stop and name the gap. Never invent through it.

## Step 0: Gather materials

Collect from the release folder: Loom/walkthrough transcript, feature outline,
any approved docs, footage index. Paste them into the chat, each labelled with
its source name.

## Step 1: Claims Lock draft

Paste:

> You are the Launch Factory writer seat. From ONLY the sources below, list
> every launch claim we could make. For each: the exact claim text and the
> source + quote/span that supports it. Separately list (a) claims people will
> want that the sources do NOT support: mark these FORBIDDEN or HELD with the
> missing evidence named, never invent support; (b) any pricing, seat counts,
> limits, or roadmap dates: these are always forbidden unless a live approved
> source states them. Do not draft any asset yet. Label demo/fixture material
> as fixture (demo assets are never claim evidence).
> Sources: <paste>

Copy the resulting table onto the Claims Lock card (`reviewer/claims-lock.md`
shape) and get **Reviewer's written approve**. Slack thumbs do not count. No
asset drafting before this lock.

## Step 2: First real adapter draft (blog when slot 1 is HELD)

Paste:

> Claims Lock is approved (attached). Using ONLY the allowed claims, draft the
> blog post. Every factual sentence must map to an allowed claim id. Name held
> slots 1/5/6 as HELD where relevant. No auto-publish language, no invented
> features/limits/pricing. Mark the draft "NOT submitted to Reviewer, not
> published."
> Approved claims: <paste locked list>

Give the draft to Reviewer on the spot-check card (`reviewer/spot-check.md`).
Request Changes = regenerate **that** artifact only.

## Step 3: Remaining adapters

After the spot-check passes, repeat step 2's prompt shape once per adapter:
email segments (slot 3), changelog (slot 4). Slots 1/5/6: write a one-line
HELD stub with the hold reason instead of an asset.

## Step 4: Manual validation (≤2 rounds, fail closed)

Paste, per artifact:

> Check this draft against the locked claims list. Report: (1) any sentence
> with no allowed claim behind it; (2) any forbidden claim present; (3) any
> auto-publish/auto-send language; (4) any pricing/limits/roadmap invention.
> List fixes. If a claim cannot be fixed from evidence, mark it for Reviewer as a
> gap. Do not rewrite it into something unsupported.
> Draft: <paste>  Locked claims: <paste>

Regenerate at most twice; if still failing, escalate to Reviewer with the gap
list instead of forcing a third rewrite.

## Step 5: Reviewer pack approve

Fill the pack-approve card (`reviewer/pack-approve.md` shape): slot table with
links/text per artifact, HELD-skip rows for 1/5/6, WIP=1. Reviewer marks
**Approve pack** or **Request Changes** (named slots only) in writing.

## Step 6: Honest package summary

Paste:

> Produce the final package summary: campaign id, each slot's state (real draft
> approved / HELD + reason), validation rounds used, Reviewer decisions with
> dates, and the still-needs-human list. State plainly that nothing was
> published or sent, and that slots 1/5/6 are held.

Save the summary wherever the team keeps run records (see
`references/run-log-template.md` for the fields). Do not say the pack was
validated by scripts: in this mode it was validated by hand, and the log must
say so.
