# ADR 0016: campaign planning alongside the assets

Date: 2026-09-07. Status: implemented through host-agent drafting and the v2 package builder.

## Decision

The operator prepares a campaign plan from the release sources alongside the channel assets. It proposes dates and audiences so the reviewer can assess the sequence as a whole.

## Consequences

The plan cannot introduce unsupported product claims. Human review covers both the assets and their proposed use. The v2 builder checks the supplied plan and assembles it with the outputs; it does not invent a strategy or publish a schedule.
