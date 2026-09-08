# Exact actor performance

Use {run_context}, {story}, {approved_scope}, {asset_inventory}, {cast_references},
{shot_request}, {audio_plan}, {provider_plan} and {review_schedule}.

First select an accepted take that already satisfies the shot. Return its exact
version/hash and usable source interval. Do not regenerate an approved performance
to improve unrelated UI or to satisfy an export-dimension request.

For a missing authorized take, separate camera framing, movement, timed action
and the exact spoken line. Give identity, voice, wardrobe, setting and product
references named roles. Fix camera side, seat, table, phone hand, light direction
and eyelines. Use one speaking role per reverse shot; keep the other actor silent
or off-camera. Preserve the approved words, qualifiers, prices, durations and units.

Pass duration, ratio, resolution, fps and model as supported adapter controls,
outside the prose where the provider requires it. Keep total film duration, edit
slot, generated source length and billing length separate. No undocumented API
arguments, voice guarantees or invented free usage.

Preserve provider-native speech when that route was approved. An approved external
voice source needs its own exact binding. The owner's clone is for the owner's
persona; fictional UGC uses its selected character voice. A first dry dialogue
sample still belongs to an explicit whole-film audio plan.

Prepare one first-sample request with current cost evidence and recipient-owned
references. Show each returned generation under the selected human schedule.
Continuous production requires a separate scope-specific instruction; unviewed
takes remain pending assembled review. Unknown spend stays unknown and ambiguous
submission requires reconciliation. No automatic retry follows.

Return the reuse plan or shot packet, exact script span, reference roles, trim,
cost/capability evidence and next human gate. Keep actual runtime IDs only in the
release record after a tool returns them. Read the existing actor protocol for
the `production-job/v1` contract and its limits.
