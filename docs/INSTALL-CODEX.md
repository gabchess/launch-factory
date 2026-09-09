# Use Launch Factory in Codex

Open the full repository as the Codex project. Keep `engine/`, `.agents/skills/`,
`.codex/agents/`, `codex/`, `docs/`, and your release workspace reachable. The generated
project skill at `.agents/skills/launch-factory/SKILL.md` reads the canonical operator,
which routes to the right specialist skill and reference bank.

Start a fresh task in this project and ask Launch Factory to work on a source folder or a
supplied packet. Confirm that the operator identifies the product, the human reviewer,
and the source stage, and that it reports the specialist it selected and the work it
actually did. Native project roles are declared in `.codex/agents/*.toml`. A host that
can't delegate must read the same selected skill and bank and work inline, and say so.

These paths follow the current [Codex custom subagent contract](https://developers.openai.com/codex/multi-agent).
Don't infer that a skill is discoverable just because the files are present. Check
installation, discovery, invocation, tool access, and first useful output separately on
your destination host. The offline checks described in
[the specialist README](../engine/specialists/README.md) prove routing and file
integrity only.

If an older global `launch-factory` skill exists, check which source path your host is
using before you invoke it. Keep the project version selected; don't overwrite or delete
another installation without an explicit migration. To roll back this project layer,
restore the prior tracked revision in a separate checkout, or remove only this layer's
generated project files after backing up local changes. Don't remove your own skills or
provider credentials.

The older, copy-the-folder `codex/launch-factory` install door is a legacy skill-only
route. Copying that folder alone won't give you the current specialist protocols; use the
full repository project instead. Host commands differ by version, so check your local
help rather than assume a particular validate or install command exists.

Provider accounts and n8n configuration belong to you, the operator. No credentials ship
in this pack. A successful MCP connection in another chat doesn't prove this host can use
it. The human reviewer's actual decisions stay human; the legacy `--human-confirmed` flag
supplies no authenticated authority.

See [INSTALL-CLAUDE.md](INSTALL-CLAUDE.md), [HOST-MATRIX.md](../HOST-MATRIX.md), and
[ADR 0017](adr/0017-specialist-routing-and-current-scope.md) for current scope.
