# AGENTS.md

Launch Factory turns a briefing and a few links into six launch drafts in one chat. It ships as a Claude Code and Cowork plugin and as a standalone skill.

It never publishes, posts, sends, merges or spends. It holds no keys, and it runs nothing when installed.

Layout:

- `.claude-plugin/plugin.json`: the plugin manifest.
- `skills/launch/`: the 0.3.0 plugin copy. `SKILL.md` holds the steps Claude follows, `outputs/` holds one contract per draft, `references/` holds setup help and the content policy, `templates/` holds the two HTML pages.
- `scripts/build_skill.py`: builds the standalone skill into `dist/` (`python scripts/build_skill.py`). It is not part of the plugin.

Try the plugin from a clone with `claude --plugin-dir .`, then type `/launch-factory:launch`.

The source of truth for the skill's steps, contracts and templates is [`skills/marketing/launch-factory/`](https://github.com/gabchess/skills/tree/main/skills/marketing/launch-factory) in gabchess/skills, a private repo with invite-only access. Make every change there. For a plugin release, copy its `SKILL.md` to `skills/launch/SKILL.md`, its `references/` contracts to `skills/launch/outputs/`, and its `assets/` pages to `skills/launch/templates/`, then run one test briefing.

One rule: change one output contract at a time, and run one test briefing after each change.
