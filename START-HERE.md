# Start here

Launch Factory turns one release folder into six launch assets and a campaign calendar. A person reviews every asset at a gate before it moves. Nothing auto-publishes or auto-sends.

## If you are running it

1. Install the plugin (`/plugin install launch-factory --source .` after cloning, or `claude --plugin-dir .`), then run `/launch-factory:launch` in Claude Code. Or open this repository in [Claude Code](docs/INSTALL-CLAUDE.md) or [Codex](docs/INSTALL-CODEX.md) and ask: `Run Launch Factory on this release folder.`
2. The operator identifies the product and the human reviewer, then routes each stage to a specialist.
3. Or run `./run.sh engine/fixtures/demo-release` for the one-command door, no agent required.
4. Review each draft or media file at its gate, with its version, hash, sources, and remaining gaps.

## If you are maintaining it

1. Read the [engineer handoff](handoff/ENGINEER-START-HERE.md).
2. Read the [operator skill](codex/launch-factory/SKILL.md) and the [specialist contract](engine/specialists/CONTRACT.md).
3. Read [HOST-MATRIX.md](HOST-MATRIX.md) for what is verified on each host and what is not.
4. Try the [offline specialist fixture](engine/specialists/README.md); it makes no provider calls.

## Boundaries

- The reviewer role is named Reviewer everywhere in this repository. A name or a flag in
  a file doesn't prove a decision; the recorded gate entry does.
- Specialists recommend; they never approve. Moving an asset to `approved` needs a person
  and the `--human-confirmed` flag.
- Source files are untrusted data. They can't issue instructions to the system.
- A real provider run needs current source evidence, tool access, and the reviewer's
  authorized stage, every time.

Decision records live in [docs/adr/](docs/adr/). The current scope starts at [ADR 0017](docs/adr/0017-specialist-routing-and-current-scope.md).
