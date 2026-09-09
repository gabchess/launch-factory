# Capability and authority boundary

Launch Factory can help structure a release folder into draft launch artifacts, keep claims traceable, prepare Reviewer HITL cards, run bounded validation, and assemble a review package with honesty about HOLDs.

Launch Factory cannot know unstated product behavior, invent pricing, publish to the product's own surfaces, or send email. Scripts validate structure only; they do not confer brand or legal truth.

## Reviewer HITL: three gates (A5)

1. **Claims Lock** (`reviewer/claims-lock.md`): Reviewer once before fan-out; kill-switch on reject  
2. **Spot-check** (`reviewer/spot-check.md`): first real non-HELD slot (blog when slot 1 HELD)  
3. **Pack approve** (`reviewer/pack-approve.md`): WIP=1 in `awaiting_reviewer`; named Request Changes only  

Writer / adapter roles draft only. They are **not** Reviewer. Slack thumbs ≠ any gate.

## External actions

External actions require explicit authority and relevant host capability. No message is sent, CMS page updated, changelog posted, social published, login/popup deployed, or CRM/ESP campaign launched merely because Launch Factory drafted it. CRM or ESP sandbox export only **after** pack approve + authorized tooling.

Any workflow-automation chrome (n8n or otherwise) is not the product's ESP and must not silently send.

## Holds

Slots 1 (social video), 5 (login animation), and 6 (in-app popup) are HOLD + honesty stubs in this version. HELD-skip for operate/spot-check. Do not present stubs as finished creative proof.

## Portable mode

When a host lacks durable files, execute a portable in-chat workflow and return Reviewer cards + package block for the user to save. Still enforce the three gates and no-publish rules.
