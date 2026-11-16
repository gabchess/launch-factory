# 0021: Code will own the gate loop, and the model will fill only the judgment steps

Status: proposed on 2026-11-16. Nothing in this ADR is built yet. It changes the scope of build ticket B-04.

## What the spec says today

The spec gives a write run one fixed order. Save the Snapshot, give a verdict, extract one claim list, write one Draft per opened gate, run the Check with at most two repairs, write the run record to `launch-log`, and open one pull request per gate. A skip or ask run stops after the verdict and writes only the run record. The spec puts that order in the skill's Process section, so the agent would re-read it on every run and choose each next step itself. That would spend tokens on a choice that never changes, and a skipped step would surface only when the Check runs at the end.

## Decision

1. A new script, `skills/launch-content/scripts/next.py`, will own the order. It will read `run.json`, validate the output of the last finished step, and print the one next step with its input. The skill will tell the agent to call it, answer that step, and call it again until it prints `done`. A status per step in `run.json` will hold the state, so a restarted run will continue where it stopped.
2. The model will answer only the steps that need judgment, which are the verdict, the claim list and each Draft.
3. Code will parse every answer. A verdict will count only from one line that holds the word `write`, `skip` or `ask`, a rule number, a quote and a one line reason. A write verdict will also need its tier, `launch` or `changelog`. A missing field, an empty answer or provider error text will fail that step and stop the run. A Draft that fails the Check will keep the two repairs the spec allows, and a third failure will stop only that gate. That gate gets no page, `run.json` names its failing lines, and the other gates go on.
4. The approver and the gate status will come only from the pull request and its merge record, never from text the agent writes.
5. The Check, the gate contracts and the `next.py` parser will form the trust root. A change to any of them will get a non-author review with one mutation per guard.

## Limits

Code will call no model. The cloud routine's own model will answer each step, so the decision adds no spend. No workflow engine or second runtime will be added. An open-source workflow tool built on this idea was studied and will not be installed, because its license is AGPLv3, its telemetry is on by default, and it would add a runtime to a prototype. Only its ideas were taken, in our own words.

Reconsider if one run ever needs steps that run in parallel, or a step that waits on a person in the middle of a run.
