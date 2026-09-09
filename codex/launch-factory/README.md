# launch-factory (Codex skill)

Version **0.2.0**: Launch Factory workflow pack (A3 engine wired Option B).

## Claim ceiling

| Claim | Allowed? |
|---|---|
| Draft launch artifacts from release-folder evidence | Yes, after / toward Claims Lock |
| Invent pricing, features, or limits | **No** |
| Auto-publish or auto-send | **No** |
| All six slots review-ready in v0.2.0 | **No**: 1/5/6 HOLD |
| Structural self_check proves marketing quality | **No**: structure only |
| Reviewer replaced by Writer | **No** |

## self_check

Canonical structural helpers live under product-root **`engine/scripts/`** (`validate_ledger`, `validate_campaign`, `build_package`). They are **STRUCTURAL_INTEGRITY_ONLY**:

- Verify required files / ledger / campaign shape / package mechanics.
- Do not score brand voice.
- Do not authorize publish.
- Fail closed on ledger kill-switch / missing evidence when validators run.

This skill's local `scripts/` folder is README-only. `schemas/` here is a **pointer** to `../../../engine/schemas/`: do not fork. Manual checklist: `docs/VALIDATION-AND-LIMITS.md`.

## Authority

See `knowledge/capability-and-authority.md` and product-root `docs/TRUST-PRIVACY-AND-AUTHORITY.md`.
