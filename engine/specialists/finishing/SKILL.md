---
name: lf-short-motion-finishing
description: "Finish an approved short motion edit with restrained kinetic type, a timed music/SFX cue sheet, speech Caption JSON when applicable, and truthful media provenance. Shared by Launch Factory's existing video lead and motion designer."
metadata:
  version: "0.1.0"
---

# Short motion finishing

Use this protocol after the story or sketch is approved, when the user requests timing, type, sound or export polish. The video lead or motion designer keeps ownership. Carry the existing story approval forward for unchanged material. A new spoken script, actor or unapproved paid rendition needs its own actual human gate.

## Lock the edit contract

Record the target duration, dimensions, frame rate, audio branch, exact words and the current human request. Follow the approved brief for the rendition. The v2 social-video builder supports 1–30 seconds; a separate production recipe can use a different duration within its own limits. A timeline length or CLI flag does not prove human authorization.

For HyperFrames, choose duration, size and frame rate on the root composition. Declare typed brand/content variables before composing. Use a separate root when those compile-time settings differ. Keep color, type roles, spacing, motion and audio rules together. Strict variable validation checks names and types; inspect a rendered variation before claiming a successful re-skin.

## Choose two to four motion rules

Select the rules that serve this edit, then apply them consistently. Useful original rules are anticipation before an important action, arc travel that follows the object, a short settle after contact, a shared element across a scene change, masked word reveals, or a timed emphasis on one meaningful word. Avoid simultaneous effects that compete for the same reading moment.

Kinetic headlines are authored composition text. Keep word/character spans editable, measure their final layout before animating, and reveal them with simple masks or transforms on a seek-safe timeline. Give the complete sentence a readable hold. A silent edit does not need a transcript, TTS or Caption JSON. Do not turn headline keyframes into guessed speech timings.

## Write an exact cue sheet

Use `cue-sheet-10s.example.json` as an illustrative timing plan, with unresolved asset IDs until actual media is selected. The schema records each cue's asset ID, source in-point, start/end time, gain and fades. Music occupies its own track; sound effects mark visible actions. A 10-second edit can use a quiet bed, a paper movement, a small contact click and one resolved chime. Silence during a hold is also a deliberate choice.

Retrieve from the chosen catalog or reuse licensed local files first when that is the authorized branch. For a tool exposing `bgm.mode`, choose `retrieve` explicitly; a failed search must not fall back to `generate`. New paid generation requires the exact authorized stage and cost ceiling. Freeze selected source files and verify their real codec and length. No new provider is needed merely to finish an existing local cut.

Treat example gains as starting values, not measured loudness. Keep the bed quiet; when speech exists, make every word clear and duck the bed around it. Use short fades, leave peak headroom, and inspect the actual final mix for clicks, clipped peaks, unexpected silence, truncated tails and channel imbalance. Measure the export and listen at normal phone/headphone levels when that capability is available. A successful decode or an audio stream's presence does not establish audibility or mix quality. Record a listening check that did not run as `not_tested`.

## Use Caption JSON only for speech

After the exact script is approved and actual speech audio exists, obtain real word timings and save typed JSON. The Caption shape is `text`, `startMs`, `endMs`, `timestampMs`, `confidence`, with optional `pageBreakAfter`; timestamps are milliseconds. `timestampMs` and `confidence` can be null. Preserve meaningful spaces in `text` when the caption renderer expects them. Correct the transcript against the final audio, then recompute timing after any speech edit.

The `speech-captions/v1` envelope in `schemas/captions.schema.json` adds the audio path/hash and clearly marks purpose `speech`. It is a local handoff wrapper; its `captions` array contains the Remotion-compatible Caption values. Do not pass the wrapper to an API expecting only Caption[]. Headline animation stays in the composition/cue sheet. Inspect readable grouping, contrast and crop safety on the rendered captions, including disclosures.

## Record the actual provider and lineage

Use `schemas/generation-manifest.schema.json` for selected source assets and each produced rendition. Record source reference, provider, job ID when returned, license status/reference, media path/hash and input-asset IDs. Keep an observed provider receipt attached to the same record. Missing job, rights or provider details stay null or unknown. A returned job ID does not establish a completed media file.

Label a ChatCut result as ChatCut. A skill name or composition file does not establish which provider generated an actor or source clip. Record a HyperFrames or FFmpeg render as a distinct output with its own hash and input lineage. Verify rights for catalog/media reuse; do not treat a subscription or retrieval success as blanket publication clearance.

Track prepared, materialized, decoded, listened, visually inspected and human-reviewed evidence separately. Each performed check names its materialized asset, exact hash and receipt/reference. Changed media needs new check evidence; a pass on an earlier rendition does not transfer. JSON validation proves structure. A matching file hash proves the referenced bytes. Neither proves product claims, licensing, provider entitlement or a human decision.

The optional `validate.py` helper requires Python and `jsonschema`, supplied by the Launch Factory environment. Run it as `python validate.py cues FILE.json --workspace PROJECT`, or choose `captions` / `manifest`. Resolved cue sheets also require `--manifest MANIFEST.json`. A missing dependency means the check did not run; do not claim validation from reading the JSON.

## Inspect and return

Check the encoded duration against the approved brief and any channel cap. Inspect motion seams, headline holds and audio tails. For a disputed visual finding, identify the artifact hash and frame/time, then inspect a fresh decoded frame before making it blocking. Preserve editable composition, original media, cue sheet, captions when applicable and the generation manifest beside the output.

Return the actual playable file and unresolved checks for the human's rendition review. Preserve the approved story, and keep the new rendition's acceptance separate. This protocol does not publish, send or generate paid script/actor work by itself.

## Source and tested status

This is original guidance. It follows the official [HyperFrames variable contract](https://hyperframes.heygen.com/prompting/variables-and-templating), [design-system guidance](https://hyperframes.heygen.com/prompting/design-systems) and [Remotion Caption type](https://www.remotion.dev/docs/captions/caption). External motion catalogs and community media are not bundled.

The schemas and fixture checks are local engineering evidence. Real rendering, caption alignment, listening and human acceptance must be recorded for the exact production artifact. A prior successful video does not certify a new edit or provider.
