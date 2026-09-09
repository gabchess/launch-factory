# Channel production prompts

Use this original prompt set to prepare complete blog, email, changelog and popup drafts from the same factual release. It extends the existing specialist roles. It contains no purchased kit text and introduces no agent role.

| Deliverable | Existing role | Prompt |
| --- | --- | --- |
| Blog | `blog_editor` | [Blog](prompts/blog.md) |
| Five email segments | `email_editor` | [Email](prompts/email.md) |
| Changelog | `changelog_editor` | [Changelog](prompts/changelog.md) |
| In-app popup | `popup_designer` | [Popup](prompts/popup.md) |

The operator supplies one `specialist-request/v1` packet and its existing route projection for each lane. Read the [shared protocol](../CONTRACT.md), selected role skill and reference bank, then the matching prompt. Source facts and exact claim spans travel separately from voice samples. A channel can use one voice-bank source's observed expression while the factual subject remains another explicitly named product.

The [n8n preparation subworkflow](../../../automation/n8n/channel-production/README.md) can check a four-request batch and return these assignments with inline evidence. Its output is planning context for the operator. Run the existing workspace validator and invoke the selected role, or state that its protocol ran inline. Preparation itself creates no content and authenticates no decision.

Follow the actual user's authorized drafting schedule. For the current draft-all request, complete all four outputs before showing a consolidated review. Retain settled gates; do not infer acceptance of unseen drafts. The view must contain the full article, each of the five emails, changelog text, and the popup graphic with its copy and dismissal behavior.

Save each artifact with its version, SHA-256 and dependencies before requesting a decision. The assigned human must review those exact bytes. A specialist only recommends review or changes. Limit revisions to two attempts per affected asset and carry the feedback subject forward; the later runtime must enforce its durable count. No automatic paid retry, sending or publishing follows from these prompts.
