# Degraded-capability operation

Use when product-root `engine/` is not reachable, Python/jsonschema is
unavailable, or the host cannot persist files (skill-folder-only install,
Claude ZIP alone, plain chat host).

## What degrades

- Structural validators (`validate_ledger.py`, `validate_campaign.py`,
  `build_package.py`) **cannot run**. Do not claim they ran. Do not invent a
  path to them. Do not fabricate validator output.
- File packaging (slot folders, MANIFEST.json, package zip) **cannot be
  produced**. Everything stays in-chat.

## What never degrades

- **Claims Lock before fan-out.** The run still stops at the claims gate.
- **Writer ≠ Reviewer.** Approval still requires Reviewer's written lock on a card.
- **No invented claims, features, limits, or pricing.** Evidence gaps stay
  gaps: a missing source narrows the draft, it never licenses invention.
- **HELD honesty for slots 1/5/6.** Held slots stay named and held.
- **No auto-publish / no auto-send.** Drafting is not publishing in any mode.

## Chat-only Claims Lock draft shape

When degraded, produce this portable card in chat for Reviewer to copy:

```
CLAIMS LOCK (draft — chat-only mode; structural validators NOT run)
Campaign: <id / title>
Mode: degraded — no engine/, no Python. Fail closed on structural proof.
Sources ingested: <file list as pasted/provided by user>

ALLOWED claims (each with evidence span):
  - claim: <text>
    evidence: <source name + quote/span>

FORBIDDEN (never drafted):
  - <claim> — reason: <no evidence / pricing invention / ADR 0001>

GAPS for Reviewer:
  - <claim someone wants but no source supports — held, not invented>

Kill-switch: armed / not armed
Held slots: 1 (social video), 5 (login animation), 6 (in-app popup) — HELD

Decision: [ ] Approve Claims Lock  [ ] Reject / needs source fix
Slack thumbs ≠ approve. Written lock on this card only.
```

## Re-entry

Tell the user what would restore full capability: keep the product root on
disk so `engine/` is reachable, and a host with Python + jsonschema. Until
then, state the mode at the top of every run output: degraded runs must be
visibly degraded.
