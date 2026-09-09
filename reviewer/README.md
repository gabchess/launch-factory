# Reviewer HITL (A5)

Three gates inside the workflow pack, in order:

1. **Claims Lock** (`claims-lock.md`): Reviewer once before adapters fan-out  
2. **Spot-check** (`spot-check.md`): first **real** (non-HELD) slot; with 1/5/6 HOLD → **blog (slot 2)**  
3. **Pack approve** (`pack-approve.md`): copy + creative; WIP=1 in `awaiting_reviewer`

**Spot-check timing:** Draft the first real slot (blog when O1 HELD) → Reviewer spot-checks **that** artifact → then remaining non-HELD adapters. Never spot-check before a draft exists.

**Which reviewer folder?** Humans fill/use these product-root cards (`reviewer/*.md`). `engine/reviewer-templates/*-template.md` are pack-builder generator templates. Don’t open both in a demo.

## Hard rules
- Writer ≠ Reviewer  
- Slack thumbs / emoji ≠ approve  
- No auto-publish / no CRM or ESP export before pack approve  
- No invent pricing  
- HOLD slots 1/5/6: HELD-skip, not the spot-check gate  
- Request Changes regenerates **named** artifact(s) only, never silent rewrite-as-approve  

Aligned also in: `START-HERE.md`, `codex/launch-factory/SKILL.md`, `knowledge/capability-and-authority.md`, `docs/TRUST-PRIVACY-AND-AUTHORITY.md`, `docs/VALIDATION-AND-LIMITS.md`, `docs/OPERATE-LAUNCH-FACTORY.md`.
