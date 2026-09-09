# Troubleshooting

## Skill or workflow pack not active

**Symptom:** the files are on disk, but the host doesn't behave like Launch Factory.

**Fix:** having the folder present doesn't mean the workflow pack is active. Re-run
install ([INSTALL-CODEX.md](INSTALL-CODEX.md) or [INSTALL-CLAUDE.md](INSTALL-CLAUDE.md)),
reload the host, and confirm the skill name.

## Claude ZIP missing

**Symptom:** no `claude/launch-factory-v0.2.0.zip`.

**Fix:** the ZIP ships in `claude/` in v0.2.0. If it's missing, use the Codex door
instead. See `claude/README.md`.

## The pack tries to publish or send

**Symptom:** a user or the model proposes "just publish" or "send the email."

**Fix:** refuse. That needs Reviewer's human review and authorized tooling. Re-read
[TRUST-PRIVACY-AND-AUTHORITY.md](TRUST-PRIVACY-AND-AUTHORITY.md) and the skill's
"Trust / Do-not" section.

## Invented claims or pricing

**Symptom:** the output includes features or prices not in the release folder.

**Fix:** strip the claim back to what Claims Lock allows, and escalate. Don't ship it. If
validation still fails after one fix-and-retry, hand the reviewer a clear gap list
instead of looping.

## Expecting all outputs to be ready

**Symptom:** a reviewer expects video, login animation, or the popup as finished, final
assets.

**Fix:** these need real footage and creative judgment. Some may be held with a reason;
see [HUMAN-GAPS.md](HUMAN-GAPS.md). Every package must name what's held.

## Engine schemas missing or forked

**Symptom:** `engine/schemas/` is missing, or a second schema set has appeared under
`codex/launch-factory/schemas/` or in the Claude ZIP.

**Fix:** the canonical schema set lives under repo-root `engine/`
(`engine/schemas/` plus the validators in `engine/scripts/`). `codex/launch-factory/schemas/`
is a pointer only; don't invent a parallel tree. If `engine/` looks empty, you're on an
old checkout; pull the latest `main`.
