# AGENTS.md

Launch Factory turns a briefing and a few links into six launch drafts in one chat. It ships two ways from one source folder: a Claude Code and Cowork plugin, and a standalone skill.

It never publishes, posts, sends, merges or spends. It holds no keys, and it runs nothing when installed.

Layout:

- `.claude-plugin/plugin.json`: the plugin manifest.
- `skills/launch/`: the only source. `SKILL.md` holds the steps Claude follows, `outputs/` holds one contract per draft, `references/` holds setup help and the content policy, `templates/` holds the two HTML pages.
- `scripts/build_skill.py`: builds the standalone skill into `dist/` (`python scripts/build_skill.py`). It is not part of the plugin.

Try the plugin from a clone with `claude --plugin-dir .`, then type `/launch-factory:launch`.

The source of truth for the skill's steps, contracts and templates is [`skills/marketing/launch-factory/`](https://github.com/gabchess/skills/tree/main/skills/marketing/launch-factory) in gabchess/skills (added in gabchess/skills#37). Make every change there. `skills/launch/` here is the 0.3.0 plugin copy: change it only to rebuild it from that folder for a plugin release.

One rule: change one output contract at a time, and run one test briefing after each change.
