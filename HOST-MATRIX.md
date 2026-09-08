# Host evidence

The full repository now includes the specialist layer described in [ADR 0017](docs/adr/0017-specialist-routing-and-current-scope.md). The retained Claude v0.2.0 ZIP is a legacy skill-only archive and does not contain this layer.

| Evidence | Codex project | Claude Code project |
| --- | --- | --- |
| Operator skill | `.agents/skills/launch-factory/` | `.claude/skills/launch-factory/` |
| Specialist skills | `.agents/skills/lf-*/` | `.claude/skills/lf-*/` |
| Native roles | `.codex/agents/lf_*.toml` | `.claude/agents/lf-*.md` |
| Shared protocol and banks | `engine/specialists/` | Same canonical files |
| Entry-point consistency | Offline generated-file check | Offline generated-file check |
| Packet routing and review binding | Offline Python fixture tests | Same helper; no host claim |
| Project skill discovery | Observed: Codex CLI 0.153.3 app-server `skills/list` with `forceReload`, 14 enabled repo skills including `lf-short-motion-finishing`, zero missing names or target errors | Not executed for this layer |
| Native role invocation | Not executed for this layer | Not executed for this layer |
| Provider access and real first output | Not verified by these files | Not verified by these files |
| Human authentication/event ledger | Not implemented by this layer | Not implemented by this layer |
| Media quality and human acceptance | Require actual artifact inspection and decision | Same requirement |
| Publish/send/schedule externally | Not included | Not included |

The operator can perform a specialist protocol inline after reading its selected skill and bank. It must identify that fallback. Schema/hash checks do not measure copy quality. The legacy validators and fixtures retain their structural limits; a boolean flag or matching event envelope does not authenticate a human.

The fresh 14-skill discovery probe ran after the finishing update on 8 September 2026. The earlier 13-skill receipt remains historical evidence. It made no model turn or provider call and changed no host configuration. Destination hosts still require their own discovery check.

The actor-production contract added in layer 0.3.0 extends the existing video lead and keeps the same 14 skill names. The observed discovery receipt above predates this contract update; its code and prompts have only offline validation here. No native invocation, provider job, n8n adapter or actor-quality result is claimed by this update.
