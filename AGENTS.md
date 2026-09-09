# Launch Factory

Root stays thin. Pull deeper files when the stage needs them.

1. Entry: read [codex/launch-factory/SKILL.md](codex/launch-factory/SKILL.md); it routes each stage through `engine/specialists/`.
2. Claims Lock comes before any drafting. Reviewer reviews all copy and creative. No invented features, limits, or pricing.
3. Nothing auto-publishes, auto-sends, or auto-schedules.
4. Specialists recommend; a person decides. Never pass `--human-confirmed` on a model's behalf.
5. Domain language: [docs/CONTEXT.md](docs/CONTEXT.md). Current scope: [ADR 0017](docs/adr/0017-specialist-routing-and-current-scope.md).
6. Tests: `.venv/bin/pytest -q`. Entry-point drift: `scripts/sync_specialists.py --check`.
