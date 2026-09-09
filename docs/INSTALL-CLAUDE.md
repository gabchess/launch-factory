# Use Launch Factory in Claude Code

Open the full repository as a Claude Code project. `.claude/skills/launch-factory/SKILL.md`
is the canonical operator; `.claude/agents/*.md` supplies the named specialist roles. The
shared `engine/specialists/` contracts and reference banks stay in the repository.
Project wrappers are generated from one registry; don't install a single wrapper
somewhere else on its own.

Start a fresh session in the project and ask Launch Factory to look at a source folder or
a supplied packet. It confirms the chosen skill path, the product, the human reviewer,
and the source gate. If native delegation isn't available, the operator reads the
selected skill and reference bank and does that role's work inline, and says so.

The project role fields follow [Claude Code's subagent documentation](https://code.claude.com/docs/en/sub-agents).
The checks in this repository confirm file consistency and offline routing only.
Destination-host discovery, actual delegation, tool access, and first output each need
their own evidence on your host. Check your installed host's help before you run any
host-management command.

`claude/launch-factory-v0.2.0.zip` is a legacy skill-only archive. It predates the
specialist layer and doesn't include the engine or the native project roles. Use the full
repository project door described above instead.

If you have an older global or project skill with the same name, decide which source path
you want before you proceed. Don't overwrite your own skills or credentials. To roll
back, keep a separate checkout of the earlier version, and back up local changes before
you remove this layer's generated project files.

Configure and verify provider access with your own account on this host. Nothing in this
pack auto-publishes, auto-sends, or auto-retries a paid call. The human reviewer's actual
decisions stay separate from a model's recommendation and from the legacy structural
record.

See [INSTALL-CODEX.md](INSTALL-CODEX.md), [the offline specialist fixture](../engine/specialists/README.md),
and [ADR 0017](adr/0017-specialist-routing-and-current-scope.md) for current scope.
