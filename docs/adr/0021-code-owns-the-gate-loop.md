# 0021: Code owns the gate loop, and the model fills only the judgment steps

Status: proposed on 2026-11-16. It changes the scope of build ticket B-04.

Every run takes the same path: save the Snapshot, give a verdict, extract one claim list, write one Draft per opened gate, run the Check, and open one pull request per gate. When that order lives in a skill, the agent re-reads the skill on every run and decides each next step itself. That costs tokens on a choice that never changes, and a skipped step is found only by the Check at the end, if at all.

`launch_factory.py next <run folder>` will own the order. It reads `run.json`, validates the output of the last finished step, and prints the one next step with its input. The skill tells the agent to call it, answer that step, and call it again until it prints `done`. The status per step that the run record already holds is the state, so a restarted run continues where it stopped.

The model answers only the steps that need judgment: the verdict, the claim list and each Draft. Code parses every answer. A verdict counts only from one line of the form `Verdict: write|skip|ask` with a rule number. A missing line, an empty answer or provider error text fails that step and stops the run.

The approver and the gate status come only from the pull request and its merge record, never from text the agent writes. The Check, the gate contracts and the `next` parser decide what is true, so a change to any of them gets a non-author review with one mutation per guard.

Code calls no model. The cloud routine's own model answers each step, so this adds no spend. No workflow engine or second runtime is added. An open-source workflow tool built on this same idea was studied and not installed, because its license is AGPLv3, its telemetry is on by default and it would add a runtime to a prototype. Only the ideas were taken, in our own words, and the private project notes hold the source ledger.

Reconsider when one run needs steps that run in parallel or wait on a person mid-run. A gate pull request already waits on its owner outside the run.
