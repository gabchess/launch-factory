# Portable production prompts

These are original templates. Fill slots from the current release workspace and approved records. Read the production protocol first. The specialist drafts; the operator performs separately authorized tools. Never paste private credentials or licensed prompt-library prose into these templates.

For a repeatable actor-to-app film, use the named [UGC App Reveal prompt index](recipes/ugc-app-reveal/README.md#prompt-index) and [recipe metadata](recipes/ugc-app-reveal/recipe.json). It supplies discovery, exact performance, authored UI, assembly/audio/captions and QA/revision prompts. Pass raw markdown and run bindings separately to a preparation workflow; matching bindings do not authorize execution.

## From the accepted angle to a shot request

```text
Use product {product_id} and only the selected source/voice references.
The accepted angle, script and sketch are {story_bindings}. Their existing human
decision is {decision_reference}. Preserve that decision for those exact inputs.

Prepare shot {shot_id} for film target {film_duration_ms}, aspect {aspect_ratio}.
Its edit slot is {edit_duration_ms}. Requested source length is
{generation_duration_ms}; keep {trim_start_ms} through
{trim_start_ms + edit_duration_ms}. Do not rewrite speech to fit a provider limit.

Separate framing, camera movement, timed action and exact approved speech.
Use these named references: {reference_ids_roles_versions_hashes}.
Preserve {wardrobe}, {light_direction}, {eyeline} and {geography}.
Only {speaker_id} speaks. The other person is off-camera or silent as specified.
Keep product pixels in the authored UI insert {ui_reference}.

Return one production-job/v1 packet, unresolved IDs as null, all five whole-film
audio categories explicit, and any missing capability/quote/reference gate.
The next action is operator review of one sample. Do not submit or approve it.
```

## One actor take

Keep duration, aspect ratio, resolution, fps and model as adapter control data. Where the selected provider requires them as tool parameters, remove those fields from the prose prompt. The template below separates the two surfaces; it is not a ready-to-send universal API payload.

```text
ADAPTER CONTROL DATA: source_duration_ms={generation_duration_ms},
aspect_ratio={aspect_ratio}, model={verified_model}, resolution={verified_resolution},
fps={verified_fps}. Use supported tool parameters; do not guess missing controls.

PROVIDER PROMPT:
Produce one continuous take using {identity_reference} as identity,
{setting_reference} as room/lighting and {voice_reference} as voice direction
or provider-specific selection. Keep {wardrobe}, {eyeline} and {geography}.
Frame: {framing}. Camera: {camera_movement}.
At {action_start_ms}, {action}; finish by {action_end_ms}.
One speaker: {speaker_id}. Say these exact words, with no additions:
{exact_script_span}

Audio branch: {provider_native | approved_audio | silent}.
Sample audio plan: {dialogue_ambience_music_sfx_captions}.
Preserve natural pauses and the complete spoken numbers and units.
No improvised claims, readable generated interface or invented price labels.
Required visible disclosures are authored during editing: {disclosures}.
Return the source take and any supported separate speech audio; do not add
unsupported control fields.
```

## Inspect the returned rendition

```text
Inspect {asset_path}, version {version}, SHA-256 {sha256}, from actual producer
{producer}, gateway {gateway}, model {model}, job {job_id}, output {output_id}.
Compare against locked speech {script_span_and_hash} and named references.
Check identity, voice, words, mouth timing, wardrobe, eyeline, room, hands,
unwanted cuts/audio and the usable trim. Cite observed timestamps or frames.
Verify disputed frame defects by fresh decoding from these exact bytes.
Mark missing listening/playback checks not_tested. Preserve price qualifiers
and disclosures. Return recommend_review, revise or blocked with the cause.
Show the playable rendition to {actual_reviewer}; specialists cannot approve.
Do not submit another generation or switch providers automatically.
```

## Assemble the film with its audio plan

```text
Use the exact clip versions listed in {input_manifest} within {review_schedule}.
Accepted parts keep their decisions; unviewed takes remain pending assembled
review only when that continuous pass was explicitly authorized.
Build readable UI and approved visible copy from {authored_sources} and
{approved_copy_amendment}. Keep concept status and unexecuted actions in the
production notes without restoring overlays the human explicitly removed.
Preserve accepted provider dialogue. Audio plan for the WHOLE film:
dialogue {dialogue_plan}; ambience {ambience_plan}; music {music_plan};
SFX {sfx_plan}; captions {captions_plan}. Off categories include their reason.
The first dry sample does not replace this whole-film plan.

Derive exact cues from {final_event_map}; replace obsolete cues after edits.
Keep music beneath the actual speech-bearing track and inspect each audio seam.
Use real speech timings from {dialogue_source_bindings} for Caption JSON.
Exclude music, SFX and ambience from caption input and inspect the final words.
Store this edit as a new asset with source/provider lineage and its own hash.
Return editable sources, the playable export, exact-byte check receipts and
remaining human review. Do not call a render success a watch or an approval.
```

## Revise an authored app scene

Use after reading the corresponding provider notes. These slots describe an
editing instruction; they add no fields or authority to `production-job/v1`.

```text
Preserve {accepted_story_and_speech_bindings} under {approved_revision_scope}.
Inspect {template_source_url_revision_entry_license} and reuse
{retained_source_components}. Record {authorized_layout_changes} and any missing
template files. Attribute fetched workflows, reused code, executing tools,
actual media producers and the final editor separately from their receipts.

Render editable UI at {native_canvas_dimensions_fps}. Use
{transparent_avatar_binding} in the single active {approved_app_layout}.
Remove obsolete screen layers and inspect alpha edges throughout motion.
For actor picture, use {accepted_or_enhanced_picture_bindings_offset_map};
preserve {original_dialogue_bindings}. An upscale needs its actual provider
result, before/after detail and continuity checks, plus unchanged-audio evidence.

Populate cards only from {verified_listing_manifest_and_photo_hashes}.
Preserve seller-posted model, asking price and location; do not invent bargain
or market-value proof. Follow {approved_visible_copy_and_CTA} exactly.
Record {product_vision_and_unexecuted_actions} in production/presentation notes.
Do not restore removed draft overlays or imply that authored actions ran.

Derive meaning-bearing reveals from {measured_speech_windows_and_offsets}.
Inspect phrase onset, settled UI and reading holds on the rendered frames.
Use {final_event_map} for taps and other SFX; retire old cues after timing changes.
Generate captions from {audible_dialogue_source_ids} and the locked transcript;
exclude music, effects and ambience. Preserve source hashes and trim offsets.

Return the complete revision with editable sources, evidence and the remaining
human gate from {review_schedule}. Reuse settled approvals within their scope.
```
