# Scripts

**STRUCTURAL_INTEGRITY_ONLY**

Scripts that land here may:

- check required paths and manifest shape;
- validate JSON Schema structure when engine schemas exist;
- run deterministic package integrity tests.

Scripts must **not**:

- publish or send;
- call HubSpot / CMS / social APIs to mutate production;
- invent claims;
- bypass Reviewer Claims Lock or pack approve.

A1 ships this README only, no executable helpers yet.
