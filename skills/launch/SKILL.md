---
name: launch
description: "Run Launch Factory on a release source: turn a release folder, repo path, or URL into claim-traced launch assets (blog, changelog, emails, social, campaign plan, and more), with a human gate on every draft. Use when asked to run Launch Factory, draft launch assets from a release, or turn a feature/repo/release into marketing content."
argument-hint: "[release folder, repo path, or URL -- leave empty to be asked]"
---

# Launch Factory: /launch-factory:launch

This is the portable operator: it works on your own product, from any project
directory, without cloning this repository's full engine. It never publishes,
sends, or schedules. A person approves every asset, or every asset is
mechanically labeled unapproved.

Source input: $ARGUMENTS

## Stage 0: Source

If $ARGUMENTS names a release folder, repo path, or URL, restate it in one
line and move on.

If empty, ask what to point this run at: a local folder, a repo path, or a
URL with the release material (changelog entry, PR, transcript, feature
outline, product page). One plain question is enough; this does not need
AskUserQuestion.

Read the source directly (Read/Glob for local paths, WebFetch for a URL).
Never fetch a URL through backtick command substitution in a shell one-liner
(`$(curl ...)`): a failed fetch returns an empty string silently instead of
an error. Use the WebFetch tool, or a checked `curl` call whose exit code you
inspect.

## Stage 1: Channel selection

Use AskUserQuestion, one question, multi-select, before any drafting. Offer
the routes in `${CLAUDE_PLUGIN_ROOT}/engine/specialists/registry.json`
(`routes` key), grouped by whether they need a render this skill cannot
produce:

**Copy only, drafted directly:**

| Channel | What it produces |
| --- | --- |
| `blog` | A source-linked feature article. |
| `changelog` | A short versioned changelog entry. |
| `email_segments` | Five announcement variants by buyer/customer segment. |
| `linkedin_post` | A grounded LinkedIn post. |
| `written_social` | X and Threads copy. |
| `campaign_plan` | A weekly multi-channel calendar with asset bindings. |

**Need a render no chat agent can produce (script, copy, or concept only):**

| Channel | What it needs beyond this skill |
| --- | --- |
| `social_video` | An actual video edit; this drafts script and shot plan only. |
| `login_animation` | An actual motion render; this drafts the concept only. |
| `in_app_popup` | Real graphic design; this drafts copy and layout intent only. |
| `carousel` | Real slide design; this drafts the page-by-page argument only. |

If the registry file has changed since this table was written, trust the
file. Tell the user plainly, for any second-group channel selected, that the
output is a script or brief, not a finished render.

## Stage 2: Mode

Use AskUserQuestion, exactly one question, before grounding:

> How do you want to run this?
> - **Gated** (recommended): you approve each draft before the run continues.
> - **Autonomous**: the run finishes and presents everything at once, each
>   draft labeled unapproved.

Remember the answer for the whole run. In autonomous mode, do not stop to ask
anything else unless a claim genuinely has no source, or the source
disappears mid-run.

## Stage 3: Ground

Build a claim list before drafting anything. For every factual claim the
output will make: quote the exact source text, and record the file path or
URL and, for a file, an approximate location (heading, line, or paragraph).
A claim with no source is dropped, or kept only as a labeled opinion, never
stated as fact. This mirrors the evidence discipline `engine/scripts/validate_ledger.py`
enforces on the engine's own claim ledger, at chat scale, without needing
that literal file format.

If `voice-bank/` in this project (or the installed plugin) has a populated
corpus, read it and note the product's own writing patterns; drafts should
sound like the product, not like Launch Factory's own docs. No voice-bank
corpus ships with this plugin. If none exists, say so once and draft in a
plain, direct register instead of inventing a voice.

Write the claim list and voice notes to `00-brief.md` in the run folder (see
Stage 6 for where that is).

## Stage 4: Draft, one fresh seat per artifact

One seat never drafts two artifacts. For each selected channel, dispatch a
separate subagent (Agent tool, general-purpose) with a self-contained brief:

- the claim list from Stage 3 (paste it in; the seat does not re-fetch the
  source)
- the channel's rubric, read from that route's `rubric` array in
  `registry.json`
- the voice notes from Stage 3, or the plain-register instruction if none
- the target format and, for slot channels, the slot number

Every claim in every draft must trace to the claim list. A seat that wants a
fact not on the list returns and asks; it does not invent one.

## Stage 5: Gate

- **Gated:** present each draft with AskUserQuestion (approve / request
  changes / drop). A change request goes to a fresh seat with the current
  draft plus the change list, never the full drafting history. Loop until
  approved or dropped.
- **Autonomous:** skip the per-draft gate. Add one line at the top of every
  drafted file: `status: unapproved draft`. This label is mechanical, not a
  judgment call by the model.

Never pass an approval flag or state on a person's behalf. Nothing in this
skill publishes, sends, or schedules; that stays with a human, always.

## Stage 6: Output

Ask once, before drafting, where output should land: default
`./launch-factory-runs/run-NN/` in the current project (check existing
`run-*` folders for the next number). Write one file per selected channel,
plus `00-brief.md` (claim list and voice notes) and `RECAP.md` (Stage 7).

## Stage 7: Close

Tell the user, briefly: what was produced, which channels, the gate state of
each draft (approved / changed / dropped / unapproved), and the single next
action. Write the same as `RECAP.md` in the run folder.

## Prime rules

1. Never publish, send, or schedule. Draft only, always.
2. One fresh seat per artifact. A revision seat gets the draft and the
   change list, never the whole history.
3. Every claim traces to a source file or URL, or is dropped, or is marked
   opinion.
4. Autonomous mode labels every draft `status: unapproved draft`; the label
   is mechanical, not prose.
5. Bring your own voice bank. This plugin ships none and invents no voice
   when one is missing; it says so and drafts plainly instead.
6. AskUserQuestion is the only pause mechanism in this skill. Do not print a
   question and wait; ask through the tool.
7. Never fetch a URL through unchecked shell command substitution.
