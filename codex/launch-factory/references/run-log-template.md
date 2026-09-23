# Run log template

One log per Launch Factory run. The skill fills this in as the run proceeds:
inputs, outputs, failures, retries, and approvals in one place. Copy the
template below; never backfill from memory, fill each field at the moment it
happens. Save per team convention (e.g. alongside the package, or pasted into
the run record). In degraded/chat-only mode, produce this log in chat and tell
the user to save it: do not claim it was persisted.

```
# Launch Factory run log

run_id:            <campaign-id>-<yyyymmdd>-<seq>
timestamp_start:   <ISO 8601>
timestamp_end:     <ISO 8601 or "open">
mode:              full (engine + Python) | degraded chat-only (fail closed)
host:              <codex | claude | other chat host>

## Inputs
input_folder:      <path or "pasted in chat">
files_ingested:
  - path: <file>
    sha256: <hash if computable, else "not computed (degraded mode)">
    bytes: <n or "n/a">
fixture_label:     <"LABELLED_FIXTURE…" / "live sources" / "n/a">

## Claims Lock
state:             draft | approved | rejected | kill-switch armed
card_ref:          <reviewer/claims-lock.md copy location>
allowed_claims:    <count + claim ids>
forbidden_claims:  <count + claim ids>
gaps_escalated:    <claims held for missing evidence — never invented>
decision_by:       <Reviewer / delegate name>
decision_when:     <ISO 8601>
decision_form:     written lock on card (Slack thumbs NOT accepted)

## Adapter outputs
| slot | type | state | draft path/ref | validation result |
|------|------|-------|----------------|-------------------|
| 1 | social_video | HELD — <reason> | stub | n/a |
| 2 | blog | draft/approved/changes | <ref> | pass / fail(round n) |
| 3 | email_segments | … | … | … |
| 4 | changelog | … | … | … |
| 5 | login_animation | HELD — <reason> | stub | n/a |
| 6 | in_app_popup | HELD — <reason> | stub | n/a |
| — | cadence binder | … | … | … |

## Validation
rounds_used:       <n> (cap 2, then escalate)
failures:
  - artifact: <slot>
    finding: <unsupported claim / forbidden phrase / auto-publish language>
    action:  <regenerated | escalated to Reviewer as gap>
retries:           <count per artifact>

## Gate decisions
spot_check:        pass / request-changes(<slots>) — <who, when, written?>
pack_approve:      approved / request-changes(<slots>) — <who, when, written?>

## Final package
package_path:      <path or "in-chat only (degraded mode)">
honesty_doc:       <ref — still-needs-human list included?>
held_slots_named:  yes/no (must be yes)
published:         NOTHING — this pack never publishes or sends
notes:             <anything a reviewer must know>
```

## Rules

- A run with no Claims Lock decision logged stops at `claims_gate`: the log
  says so plainly.
- HELD slots always appear with reasons; never omit rows.
- `published:` is always NOTHING for this pack; publishing happens outside it.
- Gate decisions record the written form only; note any Slack reaction as
  "not a gate decision."
