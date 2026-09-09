# Actor production and human review

Version 0.1.4. This original protocol belongs to the existing video lead. Read it for a film with a fictional or consented actor, from shot planning through final export. The [prompt templates](PROMPTS.md), [job schema](production-job.schema.json) and [offline checker](validate.py) travel with the augment. They do not submit jobs or authenticate decisions.

For an actor story followed by an authored product interaction, select [UGC App Reveal](recipes/ugc-app-reveal/README.md), recipe ID `ugc-app-reveal`. Its five named prompts and machine-readable index travel with this protocol. The existing video lead owns the work; the recipe adds no provider or approval authority. Use current run bindings and the actual human's selected review schedule.

## Keep the accepted story

Load the selected product evidence, voice brief, angle, exact script and sketch. Carry their file versions and SHA-256 values into the job. Preserve the actual human's existing decision for those exact inputs. A separate decision receipt can supersede an old draft label inside a frozen source. Do not rewrite settled dialogue or ask the human to approve unchanged words again.

Every spoken number has an approved plain-language form. Keep units, currency and qualifiers such as “less than” intact. An illustrative listing is not proof of savings, availability or market value. A strict price ceiling excludes a listing equal to that ceiling. The checker verifies selected numeric examples and literal source spans; a person still reviews their meaning and listens to the performance.

Keep the film target, each edit slot, requested source-take length and quoted billing length separate. A 60-second film can begin with a five-second sample. If a verified provider requires a longer take, document the trim and its cost. Keep the approved words and pacing within the accepted edit slot. TaskLink social slot 1 remains at most 30 seconds; a separate film brief does not change that rule.

## Give references named jobs

Each reference has an ID, role, version and hash. Roles are actor identity, voice, setting, wardrobe, pose or product UI. A portrait controls identity; it supplies no product evidence. A provider voice record stores the provider, its returned selection ID when available, settings and any approved reference audio. A descriptive voice direction remains a direction until the output is heard. Voice IDs and identity controls do not transfer across providers by name.

Lock wardrobe, light direction, speaker eyeline, seat and table geography, phone hand, prop placement and camera side. Use opposite-side references for reverse shots so the room stays consistent. Avoid mirroring a finished shot to invent the other angle. Give one speaking role each clip, with one small timed action. Record camera framing, camera movement, action and exact dialogue in separate fields. Request a continuous take when needed and inspect whether the result followed it.

A returned face, voice or room can drift despite the prompt. Keep that uncertainty visible. Use the actual human's existing acceptance of cast and voice direction within the brief. Ask only for a reference choice that is still unresolved. When organic actor audio is explicitly allowed, inspect its voice in the first sample and return that rendition for human review. Reuse accepted reference bindings. New identity or dialogue needs its affected gate resolved; unrelated approved material stays intact.

## Specify the whole film's audio before the sample

Write a plan for **dialogue, ambience, music, SFX and captions**, with each category explicitly on or off and a reason. Include timing intent, source or retrieval route, mixing intent and inspection needs. The first sample may use dry provider dialogue with ambience, music, SFX and captions off. That sample choice does not make the whole film silent or remove its later music plan.

For native actor speech, pass the exact locked line through the supported text or prompt control. Preserve the returned speech-bearing media and any separate audio stems. Check every word, speaker, accent, lip sync and unwanted background sound. Keep accepted provider speech through the edit. Do not silently replace it with TTS or allow an agent to improve the approved script. An approved separate voice file is another supported branch, with its own provider and hash.

When ElevenLabs speech is requested, read [the direct-account adapter](ELEVENLABS-DIRECT.md). Use the owner's approved clone for their own educator/founder persona and catalog voices for fictional UGC. Organic actor speech remains available when explicitly approved for the job. Direct ElevenLabs account access and inference.sh billing are separate routes; preserve settled decisions and apply the human's selected review schedule to each returned rendition.

Authored layers carry readable UI, prices, disclosures, captions and product evidence. Generate a blank device or a view of its back when the actor scene needs a phone. Place the verified screen in HyperFrames or use a verified product capture. Keep the actor's action aligned with the authored insert. Follow the current approved visible-copy requirement across crops. An explicit amendment can remove draft or roadmap overlays while concept status and unexecuted actions remain documented in the production and presentation records. Retain that amendment without rewriting historical decisions.

## Submit one authorized sample

1. Confirm the recipient's own account and the selected host's callable tools. A desktop MCP login is not a worker credential. Record the actual gateway, producer, model and capability receipt; leave runtime job/output IDs null before submission. Never put keys, tokens or account cookies in the packet.
2. Obtain a current quote for the exact source duration, model and quantity one. State currency or provider credits. Unknown cost remains unknown. Credits need an evidenced USD conversion before comparison with USD ceilings. Check both the per-call ceiling and remaining film budget. A plan name or authenticated tool does not establish free generation.
3. Check the packet locally. A consistent packet goes to the operator's authority check. Confirm the actual human authorized this stage and spend, including decisions already in the session. A JSON decision reference cannot supply that authority.
4. Submit **one** sample. Keep the provider's returned job ID. Follow its documented asynchronous status method. Ambiguous submission or timeout requires reconciliation of that same job before any further call. No automatic retry, fallback or batch follows an error or rejection.
5. Materialize the returned bytes in the release workspace and hash them. Save the actual producer, model, source references, job/output IDs, rights status and input lineage. Show the playable clip with its exact version/hash, exact intended speech, findings and next choice. Stop at the human review of this rendition.

By default, after the first accepted sample, request each later authorized shot as its own job and show every new result for human review. Acceptance of a sample alone supplies no continuous-pass authorization. Reuse the prior reviewed clip reference when proposing a correction. Change only the rejected variable when practical, and identify dependent audio, captions, crops or UI that need a new render. Reuse settled gates for unchanged inputs.

## Explicitly authorized continuous production

After the exact story and role samples are accepted, the human may authorize a continuous production pass for a named film scope with one assembled review gate. Record that instruction against the story version, approved references and permitted spend. This later instruction changes the review schedule for that scope; the per-generation gate remains the default for other work.

Run the authorized shots as sequential provider jobs, check returned media and assemble the cut without repeated chat confirmations for those internal steps. Track each job and its actual call count. Keep unviewed takes marked generated or checked and pending human acceptance. Present the assembled cut with its findings for the human's decision. One orchestration pass may contain several provider inferences; it supplies no evidence of a one-prompt, whole-film provider capability.

Keep per-call quotes, the film budget, retry limits and uncertain-submission reconciliation in force. A scope change or unresolved execution block still requires attention. The pass grants no automatic paid retries, provider fallback or expansion beyond the authorized story.

This exception is an operator instruction. The current `production-job/v1` schema and checker still model review after each generation and do not encode continuous-pass authority. Retain the separate human instruction with the run record. Never manufacture accepted review events for unviewed takes to make a packet pass; a future adapter must represent this review schedule explicitly before automating it.

## Edit, inspect and export

For a template-led app revision, read [the source-reuse and app-scene notes](PROVIDER-NOTES.md#reuse-the-actual-template-source) and use [the revision prompt](PROMPTS.md#revise-an-authored-app-scene). They cover actual source attribution, native UI versus source enhancement, verified listing photos and one final event map for speech, UI and sound. Preserve the selected review schedule and existing runtime contract.

Assemble accepted clips with the authored UI, or include checked takes pending assembled review under the explicit continuous-pass instruction. The selected final editor owns the film timeline and mix; HyperFrames supplies editable product UI and graphic inserts. Keep one authoritative caption source derived from the locked transcript and actual audio. Render captions once in the selected final editor instead of flattening duplicate captions into each input. Preserve actual provider lineage through every renderer and editor. A ChatCut-origin clip remains a ChatCut-origin clip after HyperFrames or FFmpeg processing. Store the new edit as another asset with its input IDs and its own hash. Use the [short motion finishing protocol](../finishing/SKILL.md) for exact cue sheets, two to four useful motion rules, measured mix levels and typed speech Caption JSON.

Caption JSON uses actual speech timings after the audio exists. Transcription is a draft to inspect; silent kinetic headlines use authored animation timing. The `approved_audio` branch requires a separate exact speech input binding, included in the reference decision and returned lineage. Native dialogue uses the returned actor audio. Duck music under the actual speech-bearing track, which may be the actor video rather than a separate narration file. Listen to the whole film for intelligibility, room tone, edits, clipping and the closing hold. Preserve separate dialogue, ambience, music and SFX tracks when available; record when only an embedded mix was returned.

Decode the final export fully and inspect exact frames and speech timestamps. Bind every reported check to the reviewed bytes. A disputed visual defect requires a fresh decoded frame from the named artifact/hash before it blocks the film. Show the final media for the actual human's decision and retain the approved export with a byte/hash comparison. Keep its editable source, reference records, audio cues, captions, manifest and decision receipt together. A new export encoding has its own hash; do not transfer checks or approval from a different encoding.

## Packet and future n8n handoff

Run with Python plus the repository's existing `jsonschema` dependency:

```bash
python3 engine/specialists/video-production/validate.py JOB.json --workspace RELEASE_WORKSPACE
```

The distributed [example](example.json) is a held fictional preparation record. Copy the `example-workspace/` files into a recipient-owned release workspace to inspect it. It has no live account IDs or human approvals. The local skill mirrors this bundle next to `short-motion-finishing/`; use that bundle's `validate.py` from its installed location.

A standalone film enters this existing video-lead protocol with `production-job/v1`. The campaign's `specialist-request/v1` social-video route retains TaskLink's 30-second rubric. Do not assign a longer standalone film to that slot or silently weaken its rubric. This branch adds a prompt/job protocol, without a new agent or campaign route.

`prepared`, `submitted`, `returned` and `failed` are reported job observations. The checker verifies file bindings, literal script spans, timing, references, cost consistency and returned-media lineage. Its projection always grants **zero** execution or approval authority. An output or matching/replayed review record stays at human review. Supplied receipts are evidence records whose authenticity, freshness, rights and quality remain outside the checker.

The story subject includes the product, file bindings, structured film brief and price constraints. The reference subject includes named references and continuity, including any supplied speech audio. Map an existing decision to this precise scope using its receipt; the mapping does not require the human to repeat a settled decision. A changed format, duration, disclosure, qualifier or reference produces a scope hold. A revision may cite a bound request for changes plus explicit feedback; it does not require falsely accepting the rejected clip. Returned lineage must include the exact script and selected identity, voice, setting and supplied speech-audio files.

For the next shot or revision, carry the previous projection's entire `rendition_binding` into `previous_rendition.subject` and preserve the original review event unchanged. Its digest is the same `subjects.rendition` used at review. Do not rewrite a decision to a media-only digest. The checker compares that binding and grants no authority to the next job.

A later app/n8n adapter must authenticate the actual reviewer, verify the latest decision for this subject, deduplicate the job key and callbacks, and commit the receipt plus state update and next outbox message in one transaction. Reconcile uncertain provider submission before retrying. Keep one authoritative approval store. These requirements are a handoff contract; this package adds no app, queue, callback server or trusted event ledger.

Before handoff, the recipient checks installation, host discovery, explicit skill invocation, own-account tool access, one real output and human acceptance separately. The disposable presenter UI and the author's private vault are not runtime dependencies. Provider-specific facts belong in [adapter notes](PROVIDER-NOTES.md), dated and subject to current verification.
