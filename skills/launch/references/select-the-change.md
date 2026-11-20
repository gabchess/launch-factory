# Select the change before writing

Use this step to turn supplied product updates into a useful launch decision. It is a single run over the inputs the user supplied, not a repository monitor or a promise to discover every change.

For each change, identify:

- What changed and the source that says so.
- Who can do something differently, and the supported benefit or problem solved.
- Availability: released, beta, planned or unknown. Record eligibility or rollout limits.
- Whether it fits the client's positioning and intended audience.
- Decision: include in this launch, hold for evidence or availability, or skip because there is no supported audience-facing story.

Show a compact decision table when there are several candidates. A dependency bump or internal refactor usually belongs in the skip group unless the sources establish a relevant user benefit. A merged feature behind a flag belongs in hold when its availability is unknown. A released feature with a clear audience and use case is a candidate for the launch. These are judgments from the sources, not automatic rules based on a PR label.

Choose one coherent story. Group several changes only when they serve the same audience and outcome. Do not turn a list of unrelated commits into a generic announcement. A user-specified planned launch can still receive clearly labeled planned drafts; never imply it is available now.

When no change qualifies, say why and what would change the decision. Do not create empty launch files or dress up an internal update to satisfy a six-output count. Ask one useful next question, such as whether the team has a release confirmation or a customer-visible change to use instead.

For a chosen launch, carry a small shared brief into every output: audience, change, supported benefit, status, limits, next action and the source for each. Derive the angle from the company's positioning and use cases. Do not invent a before-state, a customer quote, a result or a CTA destination. Missing information stays a question for the reviewer.
