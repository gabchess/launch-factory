# Launch Factory 0.3.0

Turn a meaningful product change into a reviewable launch packet using your team's positioning and voice.

## Install the standalone skill

**Claude Code:** unzip the standalone archive. Copy the whole `launch-factory` folder into `~/.claude/skills/`, or into `.claude/skills/` for one project. Preserve any existing version first. Start a fresh session and type `/launch-factory` with your briefing. Keep the templates, references and license beside `SKILL.md`.

**Claude chat or Cowork:** enable file creation/code execution where available, then go to **Customize > Skills > + > Create skill > Upload a skill**. Upload `launch-factory-skill.zip`, enable it and start a fresh chat or task. Say, "Use Launch Factory with the attached briefing and brand context." Confirm when it asks to draft. Local Claude Code installation does not enable the account skill for Cowork. Team policies and menu labels may differ; see [Claude's skill guide](https://support.claude.com/en/articles/12512180-use-skills-in-claude).

Use either this skill or the same-named Launch Factory plugin in a session, to avoid ambiguous loading. The plugin command is `/launch-factory:launch`; the standalone command in Claude Code is `/launch-factory`. Natural-language selection is the shared starting point for chat and Cowork.

## First useful run

Provide one release/PR or a small set of changes, plus:

- The intended audience and why this change matters to them.
- Release status, eligibility and important limitations.
- Your approved positioning and one or two writing examples.
- The action you want the reader to take.

The skill can reuse `.claude/product-marketing-context.md` or `.launch-factory/preferences.md` in an accessible working folder. In chat, attach or paste the equivalent. Private PR access needs an appropriate connector; pasting the relevant text also works. No connector is required for the included fictional example.

Try this prompt with your sources:

> Use Launch Factory to turn these product changes into a launch packet. First identify what deserves an announcement, what should be held, and what should be skipped. Use the attached product marketing context and approved writing samples. Keep claims tied to evidence and flag anything whose availability is unclear. Prepare drafts for human review.

## What you receive

For one supported launch story: a short blog post, changelog, FAQ, three social post options, a launch-map HTML file, and a captioned explainer HTML file with its Markdown script. Six draft types produce seven files. The default blog is a short launch post, not a full tutorial; social options follow the bundled short-post format. If your desired channel needs a different format, the skill flags the mismatch.

Open the HTML files in a browser; press Play in the explainer. It is an HTML preview with captions, not a rendered video or voice track. Each draft shows its sources and unresolved claims. A no-launch decision is valid when nothing supports a useful announcement.

Ask to revise one output, such as "Make the blog title more concrete." It saves a new version beside the original and leaves the other files alone. In a chat without file creation, it explains the limitation and presents supported text instead.

## Run a real trial

Start with `examples/briefing.md` to see the workflow with fictional evidence. Then use one real product change and your own context. Review whether it chose the right story, preserved availability limits, matched your voice and reduced editing effort. Record what you kept, corrected and discarded. The package does not establish a percentage of time saved or client ROI.

This version has local package checks and synthetic instruction trials; those are not fresh native execution tests in all three Claude surfaces or a real client acceptance test. Confirm that your host loads the skill and produces the expected files before relying on it.

Nothing is published, sent, scheduled or merged. The skill does not monitor repositories, install connectors or store keys. Inputs are processed by your Claude session and any connected tools used to read them; this is not an offline privacy guarantee.

To remove it, delete only the installed skill folder in Claude Code, or disable/remove the uploaded skill under Customize > Skills. Keep your drafts. Restore your previous folder or ZIP to roll back.
