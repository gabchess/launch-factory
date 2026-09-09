# Launch Factory: glossary

Domain language for turning one feature-release folder into review-ready launch
artifacts plus a one-release campaign plan, with Reviewer as the only copy-and-creative ship
gate.

## Language

**Launch Factory**:
The system that turns one release folder into review-ready launch artifacts. Not a prompt. Not auto-publish.
_Avoid_: pipeline, motion, machine, orchestrator (except as informal talk)

**Release Campaign**:
One campaign object for one feature ship. Holds status, sources, six artifact slots, cadence, Reviewer queue, CRM/ESP sandbox state.
_Avoid_: project, job, workflow run

**Claim Ledger**:
The allowed / forbidden / needs-disclaimer list plus evidence spans for one campaign.
_Avoid_: facts list, brand rules, compliance pack

**Claims Lock**:
Reviewer's once-per-campaign yes on the Claim Ledger. Adapters stay cold until this passes.
_Avoid_: brand check, first review, copy review

**Adapter**:
The cell that drafts one output slot (social video, blog, email, changelog, login animation, in-app popup) from locked claims only.
_Avoid_: generator, writer, skill

**Cadence Binder**:
The one-release schedule that sequences the six outputs across channels (changelog → interrupt email → story video → written social + IG/TikTok).
_Avoid_: campaign calendar, content plan, blast list

**Reviewer**:
The VP Marketing seat. Only human who Approves copy and creative. Writer is never this seat.
_Avoid_: approver, HITL, marketing lead (when you mean this gate)

**Fixture**:
A labelled fake release used for rehearsal. Placeholders only (`FEATURE_NAME`). Not real product facts.
_Avoid_: mock, sample, demo data (when you mean this labelled pack)

**Held**:
An artifact slot kept empty on purpose, with a reason, instead of inventing a claim or asset.
_Avoid_: skipped, missing, N/A (when a slot is intentionally stopped)

**Kill-switch**:
Armed when an allowed claim has no evidence or forbidden text appears. Factory stops drafting.
_Avoid_: error, fail, block

**Honesty Doc**:
The list of steps that still need a human, shipped with the package.
_Avoid_: limitations, known issues, TODO

**Demo Asset**:
A generated mockup/video/example made for a recorded demo run so the system looks cool. Not evidence for Claims Lock. Not sourced from a real client's internal docs or access.
_Avoid_: fixture (fixture = labelled fake claims pack), real output, production creative

**Tech Demo**:
A mocked/simulated interactive run of the Launch Factory with made-up data for a non-technical audience. Clips can feed a recorded walkthrough. Not Claims Lock evidence.
_Avoid_: production app, live CRM/ESP, fixture (claims pack)

**Orchestrator**:
The front-door seat that routes any arrival (topic, file dump, release folder) into the
right spine and owns sequencing decisions. Never drafts copy itself; never approves.
_Avoid_: router, conductor, main agent (when you mean this seat)

**Campaign Plan**:
The seventh output: one-release, day-by-day, multi-channel sequence drawn from the same
locked claims. Reviewer approves it inside the pack. Replaces "Cadence Binder" as the
customer-facing name; cadence_binder.json remains its data shape.
_Avoid_: content calendar, blast plan

**Voice Bank**:
The interim corpus of the product's own authored public material (site copy, social,
LinkedIn, and any internal writing sample explicitly provided for this purpose) plus
the tone-and-style brief derived from it. Every voice judgment cites a bank item.
Interim until a real brand guide lands. See `voice-bank/README.md`.
_Avoid_: brand guide, style corpus

**Run Log**:
The per-run record: inputs and hashes, claims state, adapter outputs, validation
results, retries, gate decisions, final package path. Written by both doors.
_Avoid_: audit trail, history (when you mean this artifact)
