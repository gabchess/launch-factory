# Example 02: Blog adapter draft (fixture)

**Fixture-only walkthrough.** Product = Quorum Desk from the mock GTM ship
fixture (`engine/fixtures/mock-gtm-ship/`). Synthetic demo, not a real feature
of any live product. The draft shape below mirrors the real spine output
style seen in a real run's package output.

## Prerequisite

Claims Lock **approved in writing by Reviewer** on the fixture ledger
(see `examples/01-claims-lock-walkthrough.md`). Without that lock, the blog
adapter does not run. Slot 1 (social video) is HOLD, so **blog (slot 2) is the
first real draft and the spot-check target**.

## Draft skeleton (fixture claims only)

Header block, same discipline as the real spine:

```
# Blog — Quorum Desk (fixture insights draft)
Campaign: camp_mock_gtm_ship (FIXTURE)
Slot: 2 · blog · v1
Status: draft · NOT submitted to Reviewer · not published
Claims used: only allowed rows from the fixture claim ledger
Forbidden: pricing · seat counts · roadmap dates · win-probability
  scores · guaranteed outcomes · "slots 1/5/6 complete" claims
```

Body moves, each tied to an allowed claim:

1. **Hook**: approval queues and deal reviews hide the thing you must judge
   (paraphrase of the fixture transcript's framing, [00:20]).
2. **Mechanism**: Quorum Desk reconstructs the buyer's decision system from
   notes, email, and CRM exports *you provide* (transcript [00:20], fixture).
3. **Discipline**: every claim tagged observed / inferred / disputed…
   (transcript [00:45], fixture).
4. **Boundary paragraph, verbatim honest**: it does not send mail, update CRM,
   or schedule meetings without separate authorized tooling (transcript
   [01:35], fixture). No auto-publish language anywhere in the post.

## What the writer seat does after drafting

- Marks status `awaiting_reviewer`, fills the spot-check card
  (`reviewer/spot-check.md` shape) for Reviewer on **this** artifact.
- Never marks its own draft approved. Writer ≠ Reviewer.
- If a sentence cannot cite an allowed claim, the sentence is cut or the claim
  goes back to Reviewer as a gap. It is never "smoothed over."

**Failure shape:** inventing a Quorum Desk pricing tier, claiming it "closes
deals faster," or publishing language ("goes live Tuesday") instead of
draft/review language.
