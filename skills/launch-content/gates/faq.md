# FAQ update

The reader is a customer or a support agent. The owner is the support lead.

The update holds 2 to 4 question and answer pairs, so 4 to 8 lines and 16 to 160 words. Each answer stays under 40 words. The line minimum is one line per required part, and the word minimum is a prototype choice to be checked in the rehearsal.

The gate opens for a change to how a user does something. Its door is two-way. Its blast radius is the answers added to the `/faq/` page.

The agent gets the questions and answers the Source supports right. The owner adds screenshots, article links and exact interface labels.

Each `## Q:` heading needs no claim, and each answer cites claims. No answer touches a topic listed in the Source's open questions.

The Check reads the block below.

```json
{
  "reader": "A customer or a support agent",
  "owner_role": "support-lead",
  "parts": ["question", "answer"],
  "uncited": ["## "],
  "lines": [4, 8],
  "words": [16, 160],
  "opens_for": "A change to how a user does something",
  "door": "two-way",
  "blast_radius": "The answers added to the /faq/ page",
  "rules": ["Each answer is under 40 words.", "No answer touches a topic listed in the Source's open questions."]
}
```
