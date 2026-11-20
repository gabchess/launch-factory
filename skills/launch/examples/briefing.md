# Fictional launch briefing

Everything in this example is fictional. It demonstrates a workflow, not a real customer result. Paste it into a new session after enabling Launch Factory. No browsing or connector is needed.

Use Launch Factory to select a useful launch story and prepare the six draft types below for human review. Do not publish anything.

## Product and audience

Fieldnote helps small service teams organize client intake. This launch is for operations managers using existing Team-plan workspaces. The goal is to help them use CSV export for their weekly spreadsheet handoff. Voice: a practical peer; clear, modest and specific. Avoid "game-changing", urgency tactics and unmeasured claims about time saved.

## Source 1: approved release note

CSV export is available now for all Team-plan workspaces. Workspace admins can export selected form responses using the active date-range filter. Exports retain custom field headers. Members cannot export. Attachments are not included.

## Source 2: merged PR summary

PR 412 implements CSV export, date filtering and admin-only access. It is included in the release confirmed in Source 1. Tests cover empty results and Unicode headers. A test passing is not a customer outcome measurement.

## Source 3: product guide

An admin opens Responses, chooses a date range, selects Export CSV and confirms. An empty result produces a header-only file. The next action in the draft should be to open Responses and try an export. Do not invent a guide URL.

## Source 4: approved positioning and voice example

Positioning: "Keep client intake organized so the next person can act on it."

Voice example: "Small change this week: filter responses by date before reviewing them with your team. Clearer handoffs start with the right information."

Use the example for style. It is not proof that this launch improved any measured outcome.

## Other changes

- PR 413 removed unused internal logging configuration. No user-visible behavior changed.
- PR 414 implements a new dashboard behind a disabled feature flag. No release date or customer availability is approved.
- An informal comment guesses "42% less admin work". There is no measurement supporting it.

Select what belongs in this launch, hold or skip the rest with reasons, and keep unsupported claims out of the draft copy.
