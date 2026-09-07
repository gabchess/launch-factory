# Documentation custody

## Customer-facing docs (this release)

Paths listed in `documentation-manifest.json` at product root. Edit only through the maintainer process; do not silently diverge claim ceilings across surfaces.

## Alignment rule

These must stay lockstep on HITL / non-goals:

1. `START-HERE.md` — What Launch Factory is not
2. `codex/launch-factory/SKILL.md` — Trust / Do-not
3. `codex/launch-factory/knowledge/capability-and-authority.md`
4. `docs/TRUST-PRIVACY-AND-AUTHORITY.md`
5. `docs/VALIDATION-AND-LIMITS.md` + `HOST-MATRIX.md`
6. `codex/launch-factory/README.md` — claim ceiling / self_check

## Runtime vs maintainer

- **Ship:** product root, `docs/`, `codex/`, `claude/` (ZIP when present), `engine/` (customer-visible SoT pointer).
- **Never ship as runtime:** `maintainer-source/`.

## Version

Documentation in this tree is for **Launch Factory v0.1.1** (skeleton). Update `CHANGELOG.md` and manifests when docs change claim boundaries.
