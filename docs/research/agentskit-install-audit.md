# AgentsKit install audit

Checked on 2026-09-08 against the entitled private repository at `getagentskit/kit`, commit `991fa9cd57e686069aba2580d00ae1904c1ebcb5`. This is an original audit summary. Purchased source and raw private repository responses are excluded from Launch Factory.

The existing AgentsKit CLI was version `1.0.0`. All 768 files selected by its package manifest matched that commit. The source contained 103 skills. No global upgrade or overwrite was needed.

A read-only Codex 0.153.3 discovery call found the relevant installed skills enabled. `content-creator`, `content-research-writer`, `email-sequence`, `popup-cro` and `executing-marketing-campaigns` matched the kit copies. The first and last also had all their referenced files. Local `copywriting` and `copy-editing` house variants were preserved.

The observed host had copies in both `.agents/skills` and `.codex/skills`. The operator used explicit skill paths to avoid ambiguous names. Discovery establishes availability; separate artifact evidence must record any actual skill invocation or helper execution.

The [official quickstart at the inspected commit](https://github.com/getagentskit/kit/blob/991fa9cd57e686069aba2580d00ae1904c1ebcb5/docs/quickstart.md) installs `.claude/` components. Its [CLI source](https://github.com/getagentskit/kit/blob/991fa9cd57e686069aba2580d00ae1904c1ebcb5/src/cli.js) has no Codex target. Codex can load the imported `SKILL.md` files; this audit did not install native AgentsKit agents or convert its `/blog-post` command. The public site advertised more skills than the accessible source, so the audit uses the verified source count.

AgentsKit is optional for this handoff. Launch Factory's own [channel prompts](../../engine/specialists/channel-production/README.md), source contracts and [preparation code](../../automation/n8n/channel-production/README.md) are original repository material. Recipients who choose AgentsKit use their own entitled account and local skill install. No kit command, catalog prose, paid template or credential was copied into these reusable prompts.

For this batch, the user's instruction to draft all four channels before consolidated review governed the generic skill interview steps. Source facts and the observed channel samples governed the writing. Generic examples inside a skill supplied no evidence for product claims, pricing or results.
