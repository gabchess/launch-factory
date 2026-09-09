# Reviewer: Claims Lock (once per campaign)

**Campaign:** {{campaign_id}}: {{title}}
**Seat:** Reviewer VP Marketing (writer ≠ Reviewer)
**Surface:** approval card + linked ledger

## Ledger summary
- Allowed claims: {{allowed_count}}
- Forbidden list present: yes/no
- Kill-switch armed: {{kill_switch.armed}}

## Decision
- [ ] **Approve Claims Lock**: adapters may run
- [ ] **Reject / kill-switch**: fix source; do not draft

## Rules
- Every allowed claim must show evidence span (transcript or outline).
- No pricing / limits invention.
- Slack thumbs ≠ Claims Lock.
- On reject: status → `needs_source_fix`; adapters stay cold.
