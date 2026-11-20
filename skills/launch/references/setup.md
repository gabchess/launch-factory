# Setup and team context

Launch Factory works from a pasted briefing with no connector. Links are optional: use the connected service that can read each supplied link, or ask for the text or an attachment. Do not enumerate unrelated missing tools or ask for credentials. A connector being listed is not proof that it can access a particular source.

## Reuse the client's context

Read context the user supplied or identified for this client. In a local project, the usual locations are `.launch-factory/preferences.md` and `.claude/product-marketing-context.md`. If both exist, use the product context for positioning and the preferences for writing constraints; explicit current instructions win over older preferences. Surface conflicting facts.

On Claude chat, accept an attached file or pasted equivalent. In Cowork, use the permitted working folder or attachments. If a path is inaccessible, say so; do not claim to have read it. Do not require people to recreate context their team agent already has. Never save client material inside the installed skill folder or carry it between clients.

Useful context fields:

- Product, intended audience, problem solved and positioning.
- Approved terms and product spellings; phrases or claims to avoid.
- One or two approved writing samples and what to preserve about their voice.
- Availability, eligibility, limitations and approved launch facts.
- Preferred channels, CTA and CMS format constraints, if already known.

Apply these within each output's contract. If a preferred channel or format falls outside a contract, flag the mismatch; do not silently rewrite the contract or promise channel readiness. For example, the supplied blog contract is a short launch post, not a long tutorial.

With no context, continue from the briefing with neutral writing. Ask only for missing details that would change the work, at the end of the run. A missing metric stays unknown; a writing example never proves a product fact.

## Optional preferences file

Save `.launch-factory/preferences.md` in a local project, attach an equivalent file in Claude chat, or paste its contents. Offer this template when useful:

```markdown
# Client context
Product and audience:
Positioning and problem solved:
Voice and spelling:
Approved writing examples:
Terms and claims to avoid:
Preferred channels and next action:
Known availability and limits:
```

Empty fields mean unknown. Do not invent facts to populate them. Keep setup files intact so the skill can be reused or removed cleanly.

## Reading links

A code-host connector can read supplied PRs; an issue tracker can read issues; a team-chat connector can read a supplied thread; a page-fetch tool can read public pages. Use only sources supplied or specifically identified for this run. Do not start a background watcher or search across unrelated repositories, workspaces or clients.

If a required private source cannot be read, offer a pasted excerpt or attachment. Users who prefer a connector can add it through Claude's Connectors settings or Claude Code's MCP settings. Follow current official help rather than guessing menu labels. Launch Factory does not install or authorize a connector.

## Host installation

- **Claude Code:** extract `launch-factory-skill.zip` and copy its entire `launch-factory` folder to `~/.claude/skills/` for personal use, or `.claude/skills/` in a project. If building from the repository, copy `dist/launch-factory/`, not the repository folder: the installed folder must contain `SKILL.md` directly. Start a new session and use `/launch-factory`. Preserve an existing folder before replacing it. Copying only `SKILL.md` loses required templates and references.
- **Claude chat and Cowork:** enable file creation/code execution where available. Under **Customize > Skills > + > Create skill > Upload a skill**, upload the standalone ZIP and enable it. Start a fresh chat or Cowork task and explicitly ask to use Launch Factory. Without the slash command, the skill asks one yes before drafting. Menus and organization policies may differ; see official help below.
- A local Claude Code installation alone does not install the skill for Cowork. Each teammate needs access to the account-enabled skill or their own copy; team sharing depends on the organization's settings.
- Use either the skill or the same-named plugin in a given account/session to avoid ambiguous discovery. The plugin uses `/launch-factory:launch`; the standalone skill uses `/launch-factory` in Claude Code. Natural-language selection is the portable starting route for chat and Cowork.

Official references, checked 2026-11-20:

- [Claude Code skills](https://code.claude.com/docs/en/skills)
- [Use skills in Claude](https://support.claude.com/en/articles/12512180-use-skills-in-claude)
- [Create custom skills](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills)

## Files and privacy

The six output types produce seven files: four Markdown drafts, a launch-map HTML file, and an explainer HTML file with its Markdown script. HTML files use bundled templates and make no network requests. The explainer has captions and playback controls, but no rendered video or audio.

Claude Code and Cowork can save files in an allowed working folder. Claude chat can offer downloadable files when file creation is available; otherwise show the supported drafts and explain the limitation. Never claim a file exists on the user's computer merely because it exists in a chat's file environment.

The briefing is processed by the Claude session and any connected tools used to read supplied sources. This is not an offline or local-only privacy guarantee. Launch Factory adds no credentials, telemetry, background jobs or publishing integration.
