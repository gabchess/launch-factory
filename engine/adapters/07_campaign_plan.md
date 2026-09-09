# Campaign Plan adapter (slot 7)

Drafts the **Campaign Plan**, the day-by-day, multi-channel sequence for one
release, from locked claims only (ADR 0016). Formerly the customer-facing
"cadence binder"; `cadence_binder.json` remains the data shape.

**Campaign:** one campaign id, one release. Never a standing calendar.
**Input:** the Claims Lock (allowed/forbidden/held) + the six slot states.
**Output:** a `cadence_binder.json`-shaped plan: ordered cells, one per
channel, each pointing at an artifact slot that exists-or-is-held.

## Channels (fixed sequence floor)

1. `changelog`: the floor; shipped first, bullets only.
2. `email_interrupt`: segmented announcement (leads / customers).
3. `story_video`: IG/TikTok vertical video (slot 1).
4. `linkedin_written` / `x_written` / `threads_written`: written social cells.
5. `instagram_video` / `tiktok_video`: video cells (drop one under clock if
   the other exists; TikTok drops when IG ships).
6. `blog` and `in_app_popup` ride their slot drafts (2, 6).

## Drafting rules

- **One-release cells only.** Every cell references this release's slots. No
  invented future features, no placeholder "next month" rows, no roadmap teasers.
- **Locked claims only.** Cell copy notes trace to allowed claim ids. Forbidden
  claims (pricing, seat counts, $ savings) never appear in any cell.
- **Held slots stay held in the plan.** A cell pointing at a HELD slot carries
  the hold reason in `notes` and is marked HELD. The plan never fakes coverage
  for a slot that does not exist.
- **UTM per cell** (`utm_source`, `utm_medium`, `utm_campaign` = campaign id).
- **No publish.** The plan is a review artifact inside the Reviewer pack. Sending,
  scheduling, or posting is human, out of band, after pack approve.

## Validation

`engine/scripts/validate_campaign.py` runs `validate_cadence_binder` against
`engine/schemas/cadence_binder.schema.json` and requires all eight channel
cells present (HELD cells still appear, with hold notes). The release campaign
must also carry a slot-7 `campaign_plan` artifact entry (exists-or-held, same
rule as slots 1 to 6).

## Reviewer gate

The Campaign Plan is approved inside the same pack-approve gate as the six
slots: one card, one WIP=1 queue. Writer drafts it; Reviewer approves it; no
one self-approves.
