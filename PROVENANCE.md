# Provenance

## Canonical sources

This workflow pack is built from:

1. **A client trial brief:** feature-release folder to launch outputs + Campaign Plan; the client's own marketing lead as HITL gate. The client engagement that funded this build is not named in the public repository; its demo package and fixture are removed (see below).
2. **Factory engine (the engine spine):** schemas, validators, adapters, fixtures, reviewer templates, and honesty notes, consolidated under repo-root `engine/` (Option B single SoT; ADR 0012 moved the pack envelope to the repo root in v0.2.0, and the former repo-root developer spine was deduplicated into `engine/`, hashes compared, one copy kept).
3. **This pack:** customer envelope, skill door, docs, manifests, and honesty surfaces authored for Launch Factory v0.2.0, with the later specialist and recipe additions below.
4. **ADR 0012 to 0016** (`docs/adr/`): recorded-run hero + repo-link door, HOLD discipline, one-command door, interim Voice Bank, Campaign Plan as seventh output.
5. **[ADR 0017](docs/adr/0017-specialist-routing-and-current-scope.md):** specialist routing, selective evidence and voice references, project host entry points, and offline consistency checks. These checks grant no human approval or provider authority.
6. **[UGC App Reveal](engine/specialists/video-production/recipes/ugc-app-reveal/README.md):** original reusable prompts drawn from one approved production run. The recipe records the actual provider roles and source-adaptation method; private media, credentials, job IDs and review conversation remain outside the portable pack. Third-party source packs informed patterns only; their prose and assets were not copied into these prompts.
7. **[ADR 0018](docs/adr/0018-ugc-app-reveal-preparation.md):** the n8n preparation subworkflow packages the recipe and source bindings for an operator. **[ADR 0019](docs/adr/0019-testable-app-and-next-milestone.md)** records the next app milestone. This package does not implement an authenticated approval store or unattended media dispatch.

## What this is not derived from

Domain content, personas, knowledge bases, and deal-strategist materials from third-party
finished packs are not sources for Launch Factory. Only the package-layout and
claim-discipline pattern (install door, dual-host support, custody manifests, aligned
human-review surfaces) informed the skeleton. The demo packages under repo-root
`packages/camp_*` are run outputs, not the engine's source of truth.

## Synthetic and placeholder material

The engine fixtures (`engine/fixtures/demo-release`, `engine/fixtures/mock-gtm-ship`,
`engine/fixtures/specialist-demo`) are labelled fixtures: mock release folders. They don't
establish real product pricing or claims. The retained v0.2.0 fixtures keep their
historical slot 1/5/6 hold records from
[ADR 0013](docs/adr/0013-hold-156-until-spine.md). Later, authorized work follows
[ADR 0017](docs/adr/0017-specialist-routing-and-current-scope.md) without rewriting those
historical records; demo assets stay separate from the Claim Ledger. The original
client-named release fixture this pattern was built against is deleted from the public
repository.

`voice-bank/` is where a voice-bank corpus and its derived tone brief go, under ADR 0015.
No corpus ships with this repository; running the voice check on your own product means
supplying your own corpus. Source facts and product claims require their own evidence
regardless of voice.

## Custody note

`maintainer-source/` is for maintainers only and must never ship as customer runtime.
