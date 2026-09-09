# Reviewer: Pack approve (copy + creative)

**Campaign:** {{campaign_id}}
**Prerequisite:** Claims Lock approved; spot-check the **first real (non-HELD) slot** (for this campaign: O2 blog), not O1 when O1 is HELD; validate ≤2 done
**WIP:** 1 in awaiting_reviewer

## Artifacts
| Slot | Type | Link | Spot-check | Decision |
|---|---|---|---|---|
| 1 | social_video | | skip if HELD (first required = first non-HELD real slot) | Approve / Request Changes |
| 2 | blog | | required first when O1 HELD | Approve / Request Changes |
| 3 | email_segments | | | |
| 4 | changelog | | | |
| 5 | login_animation | | skip if HELD | |
| 6 | in_app_popup | | skip if HELD | |
| - | cadence binder | | | |

## Spot-check rule
- If O1 is HELD, skip O1 spot-check; first required spot-check = first non-HELD real slot (blog / slot 2 for non-video packs).
- Do not treat a HELD slot as the pack-approve gate.

## Decision
- [ ] **Approve pack** → status `approved` → package + honesty doc
- [ ] **Request Changes**: list artifact slot(s) to regenerate (named only; no silent rewrite-as-approve)

## Forbidden
- One click to ship / auto-publish
- HubSpot sandbox export before this approve
- Treating Slack emoji as approve
