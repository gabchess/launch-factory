# Reviewer: Pack approve (copy + creative)

**Campaign:** {{campaign_id}}  
**Prerequisite:** Claims Lock approved; spot-check on first real (non-HELD) slot done; validate ≤2 done  
**WIP:** **1** in `awaiting_reviewer` (no parallel packs in this state)

## Artifacts
| Slot | Type | Link | Note | Decision |
|---|---|---|---|---|
| 1 | social_video | | HELD-skip unless live | Approve / Request Changes / skip |
| 2 | blog | | **first real** when O1 HELD | Approve / Request Changes |
| 3 | email_segments | | | Approve / Request Changes |
| 4 | changelog | | | Approve / Request Changes |
| 5 | login_animation | | HELD-skip | skip |
| 6 | in_app_popup | | HELD-skip | skip |
| - | cadence binder | | one-release cells | Approve / Request Changes |

## Decision
- [ ] **Approve pack** → status `approved` → package + honesty doc (name HOLDs)
- [ ] **Request Changes**: list **named** slot(s) to regenerate only (no silent rewrite-as-approve)

## Forbidden
- One-click ship / auto-publish
- CRM or ESP sandbox export **before** this approve
- Slack emoji as approve
- Claiming all six review-ready while 1/5/6 are held
- Invent pricing in approved copy
