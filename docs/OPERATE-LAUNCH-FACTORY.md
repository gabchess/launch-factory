---
document_id: LF-OPS-02
title: Build and review a launch package
version: 2.0.0
status: Ready for Owner Review
owner: Gabriel
approver: Gabriel
effective_date: ""
review_date: 2026-12-13
risk_tier: Tier 1 Standard
canonical_source: docs/OPERATE-LAUNCH-FACTORY.md
supersedes: v1 operating guide
audience: Local operators and their human reviewers
---

# Build and review a launch package

## Operational foreground

V2 builds local files. The operator supplies source-backed drafts and footage. A person decides which claims and final assets to approve. The owner must approve this procedure before anyone treats it as company policy.

## Purpose and outcome

Produce six launch assets and a campaign plan that the reviewer can inspect together.

## Trigger

A release owner provides a feature outline, readable transcript, footage, and audience choices.

## Scope and boundaries

Use this procedure for a local build. Publishing, sending, scheduling, and paid provider calls require separate decisions and tools.

## Prerequisites and stop conditions

| Requirement | Ready condition | Evidence | If unavailable |
|---|---|---|---|
| Tools | Python 3.10+, FFmpeg and ffprobe; FFmpeg includes subtitles | Local version/filter checks | Install before build |
| Sources | Readable local files and exact quotes | release.json | Ask the release owner for the missing source |
| Claims decision | Human reviewed the current claims and source revision | claims-lock.json | Stop before drafting |
| Footage | A usable local clip and timed captions, 1–30 seconds | release.json and media file | Resolve the media gap before build |

## Roles and decision rights

The operator or AI host prepares sources and drafts. The human reviewer checks each claim's meaning and records Claims Lock in their own terminal. The operator runs the build. The human reviewer approves the final assets and any publication.

## Systems, inputs, and records

Keep one release folder containing `release.json`, its named source files, footage, and `claims-lock.json`. Sources can contain private product details. The output includes their text for review, so share the package only with authorized reviewers. No remote upload occurs during build.

## Standard path

1. **Prepare the claims.** The operator fills the product, title, version, and claims in `release.json`, using the example's shape. Run `python3 launch_factory.py inspect RELEASE_FOLDER`. Show the claims and quotes to the reviewer.
2. **Record the human decision.** The reviewer checks meaning and runs `python3 launch_factory.py lock-claims RELEASE_FOLDER --reviewer "Your name"`. Only that person types `LOCK CLAIMS`. If a claim is wrong or incomplete, return to step 1.
3. **Draft the assets.** The AI host uses the channel protocols to fill copy blocks, five email segments, timed captions, and campaign rows in `release.json`. Each copy block cites claim IDs. The operator resolves missing evidence instead of inventing it.
4. **Build a new revision.** Run `./run.sh RELEASE_FOLDER --out runs/NEW_REVISION`. A nonzero exit means no completed package. Fix the named error and repeat this step using a new output folder.
5. **Verify and inspect.** Run `python3 launch_factory.py verify runs/NEW_REVISION`. Serve that folder locally and open `index.html`. Read every email and check the campaign sequence. Play the full video with sound; inspect the captions, animation, and popup dismissal. Source checks do not replace a person's review of meaning or quality.
6. **Retain the review.** The reviewer records requested changes or approval with the package manifest hash in their own review system. Any edited asset needs another review. A source change returns to step 1. Publishing stays outside this tool.

## Decision points

Claims Lock permits drafting from that source revision. Finished assets require a separate approval. A successful build makes the package ready for review. Publication requires another decision. The local decision file records an operator's assertion without authenticating their identity.

## Exceptions and escalation

| ID | Trigger | Action and owner | Re-entry |
|---|---|---|---|
| E1 | Missing or changed source | Operator stops and asks the release owner to resolve it before drafting | Step 1 |
| E2 | FFmpeg error or timeout | Operator checks footage and tool output; earlier packages remain intact | Step 4 |
| E3 | Interrupted run | Operator confirms no completed destination exists; discard only a leftover temporary `.launch-*` folder from that run | Step 4 |
| E4 | Unsupported claim or poor output | Reviewer names the claim or asset and requested correction | Step 1 for facts; step 3 for copy/media |
| E5 | Private material cannot be shared | Release owner selects approved source material before building a distributable package | Step 1 |

## Completion and verification

A build is complete when `verify` passes and the output files are inspectable. Human review is complete only when the reviewer records their decision against that version. Resume interrupted work from the last saved source folder and build into a new destination.

## Evidence basis and open items

The implementation and tests define the executable behavior. `docs/V2-AUDIT.md` records the checks. The bundled example rehearses rendering without human approval. The human reviewer decides whether the visuals, audio, writing, and claim meanings are acceptable.

## Governance

Gabriel owns this procedure. Review it at each major release or when inputs, authority, rendering, or delivery change. Report corrections through the repository's issues. Retire this version when a later procedure replaces it.

## References and related artifacts

- [README](../README.md)
- [Input example](../examples/v2-release/release.json)
- [V2 audit](V2-AUDIT.md)
- [Implementation decision](adr/0020-v2-local-package-builder.md)

## Change history

| Version | Date | Change | Authority |
|---|---|---|---|
| 2.0.0 | 2026-09-13 | Replace instruction copying with a local renderer and review procedure | Prepared at Gabriel's request; owner review pending |
