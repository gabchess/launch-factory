# First run

## Read this first

Launch Factory v0.2.0 is a bounded workflow pack. Claims Lock and the Reviewer human review
gates are real. The engine lives under `engine/`: schemas, structural validators, and
adapters. When Python is available, the scripts under `engine/scripts/` validate and
package a run, but they never publish anything. Don't claim a fully automated, six-output
ship from this version; see [docs/HUMAN-GAPS.md](HUMAN-GAPS.md) for what is and is not
built.

## Goal

Complete one gated run that ends in a Claims Lock draft for Reviewer, not a published
launch.

## Before you start

- Install the skill: [INSTALL-CODEX.md](INSTALL-CODEX.md) or [INSTALL-CLAUDE.md](INSTALL-CLAUDE.md).
- Have one release folder ready, with a Loom recording, an outline, and footage (or use a
  labelled fixture).

## First ask

> Use Launch Factory. Run on this release folder.

Or run the one-command door: `./run.sh <release-folder>` (see [ADR 0014](adr/0014-one-command-one-prompt.md)).

## What happens

1. The operator ingests the release folder.
2. It drafts the Claims Lock: only claims that trace to a source, never invented pricing
   or features.
3. It stops for Reviewer on the Claims Lock (`reviewer/claims-lock.md`) before drafting
   anything else.
4. It drafts the first real output, the blog post, using the adapters under
   `engine/adapters/`.
5. Reviewer spot-checks that first draft (`reviewer/spot-check.md`). The order is always: draft
   the first real output, then spot-check it, then draft the rest. Never spot-check
   before a draft exists.
6. It drafts the remaining outputs: email (3), changelog (4), and the Campaign Plan (7).
   Optionally, run `engine/scripts/validate_*.py` when Python and `jsonschema` are
   available; having the `engine/` folder alone is not enough.
7. It validates. If a check fails, fix the input and re-run; there's no automatic retry.
8. Reviewer approves the pack (`reviewer/pack-approve.md`), and the operator builds the package
   plus an honesty note naming anything still on hold.

## Don't

- Ask the pack to publish, send, or push to a CMS or ESP.
- Treat a drafted output as Reviewer's approval.
- Claim all outputs are review-ready while any are on hold.
- Invent filler for a held slot to make the package look complete.

See [OPERATE-LAUNCH-FACTORY.md](OPERATE-LAUNCH-FACTORY.md) and
[HUMAN-GAPS.md](HUMAN-GAPS.md).
