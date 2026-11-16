# Changelog entry

The reader is an admin who skims. The owner is the product marketer.

The parts come in this order. A heading. A status tag. A one line summary. Up to three change lines. The entry holds 4 to 6 lines and 8 to 60 words.

The gate opens for any change a user can see. Its door is two-way. Its blast radius is one entry on the `/changelog/` page.

The agent gets the parts and the status tag right. The owner adds the tone and the release date.

The status tag is one of beta, planned or released. It says released only when the Source gives a date.

The Check reads the block below. A heading line that starts with `# ` may cite no claim.

```json
{
  "reader": "Admins who skim",
  "owner_role": "product-marketer",
  "parts": ["heading", "status", "summary", "changes"],
  "uncited": ["# "],
  "lines": [4, 6],
  "words": [8, 60],
  "opens_for": "Any change a user can see",
  "door": "two-way",
  "blast_radius": "One entry on the /changelog/ page",
  "rules": ["The status tag is one of beta, planned or released, and says released only when the Source gives a date."]
}
```
