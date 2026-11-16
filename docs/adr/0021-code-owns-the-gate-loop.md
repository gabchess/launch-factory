# 0021: Code owns the gate loop, and the model fills only the judgment steps

Status: proposed on 2026-11-16. It changes the scope of build ticket B-04. Nothing in this ADR is built yet.

A write run always takes the same path. It saves the Snapshot, gives a verdict, extracts one claim list, writes one Draft per opened gate, runs the Check with at most two repairs, writes the run record to `launch-log` and opens one pull request per gate. A skip or ask run stops after the verdict and writes only the run record. When that order lives in a skill, the agent re-reads the skill on every run and decides each next step itself. That costs tokens on a choice that never changes, and a skipped step is found only by the Check at the end, if at all.

A new command, `launch_factory.py next <run folder>`, will own the order. It will read `run.json`, validate the output of the last finished step, and print the one next step with its input. The skill will tell the agent to call it, answer that step, and call it again until it prints `done`. A status per step in `run.json` will be the state, so a restarted run continues where it stopped.

The model will answer only the steps that need judgment, which are the verdict, the claim list and each Draft. Code will parse every answer. A verdict will count only from one line that holds the word `write`, `skip` or `ask`, a rule number, a quote and a one line reason, and a write verdict also needs its tier, `launch` or `changelog`. A missing field, an empty answer or provider error text will fail that step and stop the run. A Draft that fails the Check keeps the two repairs the spec allows, and a third failure stops the run.

The approver and the gate status will come only from the pull request and its merge record, never from text the agent writes. The Check, the gate contracts and the `next` parser decide what is true, so a change to any of them gets a non-author review with one mutation per guard.

Code will call no model. The cloud routine's own model answers each step, so this adds no spend. No workflow engine or second runtime is added. An open-source workflow tool built on this same idea was studied and not installed, because its license is AGPLv3, its telemetry is on by default and it would add a runtime to a prototype. Only the ideas were taken, in our own words, and the private project notes hold the source ledger.

Reconsider when one run needs steps that run in parallel or wait on a person mid-run. In the spec, a gate pull request waits on its owner outside the run.
