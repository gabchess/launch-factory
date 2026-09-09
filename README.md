# Launch Factory

One feature-release folder in. A review-ready launch package out. A person approves every word before anything leaves.

Hand your AI agent this repository and one release folder: a transcript, a feature outline, raw screen or product footage, a link, a repo, whatever you have. It returns six launch assets and a campaign plan. Every product claim traces to a quoted source. Every asset waits for a human decision. Nothing publishes, sends, or schedules.

It runs two ways:

- **From an agent.** Open this repository in Claude Code or Codex, then ask, in plain language: `Run Launch Factory on this release folder.` The operator reads the release folder, drafts each asset, and stops at every gate below for a human decision.
- **From the command line.** Run `./run.sh RELEASE_FOLDER` for the same ingest, validate, and package steps, no agent required.

## Install

As a Claude Code plugin, from a clone of this repository:

```bash
git clone https://github.com/gabchess/launch-factory.git
cd launch-factory
claude
```

Then, inside Claude Code:

```
/plugin install launch-factory --source .
```

Or point Claude Code at the checkout directly, without installing: `claude --plugin-dir .`. Either way, the plugin adds one skill, `/launch-factory:launch`, that runs the operator flow described below inside a chat session.

The command-line door needs no agent and no install: `./run.sh RELEASE_FOLDER` (see Run it, below).

## What comes out

| # | Output | What you get |
| --- | --- | --- |
| 1 | Social video | A short cut with burned-in captions, plus the IG/TikTok script and shot plan. |
| 2 | Blog post | Markdown and HTML, ready for your own blog, with images. |
| 3 | Email announcement | Five variants, segmented by audience: you define the segments, the run fills them. |
| 4 | Changelog post | A short versioned entry for your own changelog. |
| 5 | Login animation | A short looping motion piece for your own login or site. |
| 6 | In-app popup | Graphic, copy, and a working dialog preview. |
| 7 | Campaign plan | A two-week calendar across email, popup, blog, LinkedIn, X, Threads, and IG/TikTok, with a human gate on every row. |

## Try it

No example run ships in this repository. Try it on the bundled fixture first:

```bash
./run.sh engine/fixtures/demo-release
```

Or, from Claude Code with the plugin installed, run `/launch-factory:launch engine/fixtures/demo-release` and pick a channel or two when it asks.

## How a run works

| Stage | What happens | Who decides |
| --- | --- | --- |
| Ingest | Every source file is hashed into one release record. | System |
| Ground | Claims are extracted with a file, offset, and quote each, and an optional voice bank checks drafts against the product's own writing. | System |
| Claims Lock | Allowed, forbidden, and held claims are confirmed once. | Reviewer |
| Create | Twelve specialist roles draft each asset from locked claims only. | System |
| Review | Scripts check evidence, slot completeness, and approval authority; a specialist checks voice and Reviewer makes the final call. | System, then Reviewer spot-check |
| Package | A review page, honesty note, and campaign plan are assembled. | Reviewer approves |
| Stop | Publishing, sending, and scheduling stay with a person. | Human |

## Where the checks live

- A claim without an evidence span arms the kill-switch before any drafting starts.
- Reviewer locks claims before fan-out, the cheapest point to stop a wrong promise.
- The first blog draft gets a spot-check before the other assets are written.
- The writer role can never approve. Moving a slot to `approved` or `packaged` needs a `--human-confirmed` flag from a person, and `validate_record.py` refuses to accept either state unless a matching Reviewer decision is recorded.
- Each validator runs once. On failure, `run.sh` prints the failed check and the safest re-entry point, then stops. Nothing retries automatically.

## Run it

```bash
git clone https://github.com/gabchess/launch-factory.git
cd launch-factory
./run.sh engine/fixtures/demo-release
```

`run.sh` creates a virtual environment on first use, then runs ingest, validation, and packaging with stage banners. `engine/fixtures/` also has `mock-gtm-ship` (a fuller sample release) and `specialist-demo` (routing only, no packaging). The same spine runs from a chat prompt in Claude Code or Codex.

## Verify

```bash
.venv/bin/pytest -q
```

Expected: every test passes.

## What still needs a human

| Job | Why |
| --- | --- |
| Claims Lock | Only Reviewer knows what the product may promise. |
| Final voice call | A voice bank flags drift; taste decides. |
| Video, animation, and popup art | Real footage and creative judgment are required. |
| Publish, send, schedule | Never automated in v1, by design. |
| Which feature, which week | The factory runs launches; it does not choose them. |

## Status and limits

- Reviewer has not approved any output; every asset is a review-ready draft.
- Today an engineer runs the media lane from Claude Code or Codex. A hosted app where a non-engineer clicks a button and gets a package back is the next phase (Phase B), not built yet.
- No pre-built example package ships in this repository. `packages/` fills in with `build_package.py` output once you run the pipeline against your own release folder. The single command that ingests a folder and packages six outputs end to end, unattended, is still being closed.
- Two n8n workflows prepare work packets; they do not yet dispatch a provider worker.
- No voice-bank corpus ships with this repository. Bring your own if you want the voice check; the pipeline runs without one.

Full detail on what still needs a human and why: [docs/HUMAN-GAPS.md](docs/HUMAN-GAPS.md).

## License

MIT. See [LICENSE](LICENSE). Fork it, change it, ship it commercially; keep the copyright notice, and expect no warranty. What the grant does not cover (runtimes, provider accounts, your own inputs and outputs) is set out in [LICENSE-STATUS.md](LICENSE-STATUS.md).

## Layout

| Path | Role |
| --- | --- |
| `engine/` | Schemas, validators, specialist protocols, fixtures, and the package builder. |
| `codex/launch-factory/` | The operator skill an agent reads first. |
| `.claude/`, `.agents/`, `.codex/` | Native entry points for Claude Code and Codex. |
| `.claude-plugin/`, `skills/launch/` | The installable Claude Code plugin manifest and its `/launch-factory:launch` skill. |
| `packages/` | Where `build_package.py` writes your finished package. |
| `voice-bank/` | Where a voice-bank corpus and its derived tone brief go, if you provide one. |
| `reviewer/` | The three human review cards: claims lock, spot-check, pack approve. |
| `automation/n8n/` | Two importable preparation workflows. |
| `handoff/` | The engineer handoff; start at `handoff/ENGINEER-START-HERE.md`. |
| `docs/` | Operating guide, first run, troubleshooting, decision records, and the [engine reference](docs/REFERENCE.md). |

Read [START-HERE.md](START-HERE.md) next, then the [engineer handoff](handoff/ENGINEER-START-HERE.md).
