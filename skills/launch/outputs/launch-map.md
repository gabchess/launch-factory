# Output 5: Launch map

One HTML file with a diagram of the launch. The launch is the center, and each branch is one part of it, such as audience, message, content, timeline and risks.

The file is `templates/launch-map.html`. It makes no network call and loads no font, script or image. You write a small JSON spec, and the template's own script draws it.

## How to fill the template

1. Copy `templates/launch-map.html` to `launch/<name>/launch-map.html`.
2. Replace the JSON between the two comment lines `<!-- LAUNCH-SPEC-START -->` and `<!-- LAUNCH-SPEC-END -->`. Keep the `<script type="application/json" id="launch-spec">` tag around it.
3. Change nothing else in the file. Do not add CSS, HTML or script.
4. Write `</script>` inside a text as `<\/script>`. The spec is plain JSON, so use double quotes and no trailing commas.
5. Open the file. A spec with a problem shows a red panel that names each bad field, for example `branches[1].label is missing`. Fix the spec and reload.

## What the spec holds

| Field | Required | Meaning |
|---|---|---|
| `title` | yes | Page heading. Text. |
| `subtitle` | no | One line under the heading. Text. |
| `center` | yes | The launch itself. An object with `label` (required) and `note` (optional). |
| `branches` | yes | A list of 1 to 8 branches. |
| `branches[].label` | yes | Short name, a few words. |
| `branches[].note` | no | One short sentence. |
| `branches[].source` | no | A whole number from 1. Points to `sources[n-1]` and shows as `[n]`. |
| `branches[].items` | no | Up to 6 smaller nodes under the branch. Each has `label` (required), `note` and `source` (optional). Items have no items of their own. |
| `sources` | no | A list of text, one per source. A `source` number must not be larger than the list. |

Fields not listed here are ignored. Keep labels short, because they sit in boxes. Mark a claim with `source` only when a numbered source says it.

## Example

```json
{
  "title": "Northwind Sync 2.0 launch",
  "subtitle": "Ship date 3 December, for existing customers first",
  "center": { "label": "Northwind Sync 2.0", "note": "Offline editing for the mobile apps" },
  "branches": [
    { "label": "Audience", "note": "Existing mobile customers on the Team plan", "source": 1,
      "items": [
        { "label": "Field teams", "note": "Work with poor signal", "source": 2 },
        { "label": "Admins", "note": "Need the rollout switch" }
      ] },
    { "label": "Message", "note": "Edit anywhere, sync when you are back online", "source": 1 },
    { "label": "Content", "note": "Six drafts, one per channel",
      "items": [
        { "label": "Blog post", "note": "Long form walkthrough" },
        { "label": "Changelog entry", "note": "Three lines" },
        { "label": "FAQ update", "note": "Conflict handling questions" }
      ] },
    { "label": "Timeline", "note": "Beta on 19 November, general release 3 December", "source": 3 },
    { "label": "Risks", "note": "Merge conflicts on shared documents",
      "items": [ { "label": "Support load", "note": "Prepare two macros" } ] }
  ],
  "sources": [
    "Pull request 412: offline queue",
    "Slack thread: field team feedback",
    "Issue 88: release plan"
  ]
}
```

## What the page does

- Wide screens: the launch sits in the middle, with branches on both sides joined by curves.
- Narrow screens: the launch on top, then the branches in one column.
- Light and dark follow the viewer's system setting.
- Every label is real text on the page, so it can be selected and searched.
