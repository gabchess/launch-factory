# Launch map

One HTML file with a diagram of the launch. The launch is the center, and each branch is one part of it, such as audience, message, content, timeline and risks. Those names are examples. Draw a branch only when a source supports it, and never invent one to fill the diagram.

The file is `templates/launch-map.html`. It makes no network call and loads no font, script or image. You write a small JSON spec, and the template's own script draws it, with a Sources list and a Not traced list under the map.

## Reader

The audience the briefing names. If the briefing names none, write for a general user of the product and ask one question at the end of the turn: "Who is this for?"

## How to fill the template

1. Copy `templates/launch-map.html` to `launch/<name>/launch-map.html` by reading it and writing it out whole.
2. Replace the JSON text inside the `<script type="application/json" id="launch-spec">` tag, between the `<!-- LAUNCH-SPEC-START -->` and `<!-- LAUNCH-SPEC-END -->` comment lines, with the new spec. Keep both comment lines and the script tags.
3. Change nothing else in the file. Do not add CSS, HTML or script.
4. Write every `<` inside the JSON as `\u003C`, so that no text in a label can end the block or start a tag. The page reads `\u003C` back as `<`, so the viewer sees the original text. The spec is plain JSON, so use double quotes and no trailing commas.
5. Check the spec against the table below. Open the file when this surface can. A spec with a problem shows a red panel that names each bad field, for example `branches[1].label is missing`. Fix the spec and reload. If you cannot open it, say "not opened" in the status line.

## What the spec holds

| Field | Required | Meaning |
|---|---|---|
| `title` | yes | Page heading. Text. |
| `subtitle` | no | One line under the heading. Text. |
| `center` | yes | The launch itself. An object with `label` (required), and `note` and `source` (optional). |
| `branches` | yes | A list of 1 to 8 branches. |
| `branches[].label` | yes | Short name, a few words. |
| `branches[].note` | no | One short sentence. |
| `branches[].source` | no | A whole number from 1. Points to `sources[n-1]` and shows as `[n]`. |
| `branches[].items` | no | Up to 6 smaller nodes under the branch. Each has `label` (required), `note` and `source` (optional). Items have no items of their own. |
| `sources` | yes | A list of text, one entry per source, in order. Each entry is the link the user gave, or "pasted text: <first five words>". A link that was not used is listed as "not used, because <reason>" and nothing points to it. A new source from a redraft goes at the end. |
| `notTraced` | yes | A list of text, one entry per claim you could not trace to a source, or per open question. Empty when nothing is untraced. |

Every `source` number, on the center, a branch or an item, must point into `sources`. A `source` number with no `sources` list, or larger than the list, is an error.

Fields not listed here are ignored. Keep labels short, because they sit in boxes. Mark a claim with `source` only when a numbered source says it.

## Example

```json
{
  "title": "Northwind Sync 2.0 launch",
  "subtitle": "Ship date 3 December, for existing customers first",
  "center": { "label": "Northwind Sync 2.0", "note": "Offline editing for the mobile apps", "source": 1 },
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
    { "label": "Timeline", "note": "Beta on 19 November, general release 3 December", "source": 3 }
  ],
  "sources": [
    "https://example.com/pull/412",
    "pasted text: Field team feedback this",
    "https://example.com/issues/88"
  ],
  "notTraced": ["Whether admins get a rollout switch"]
}
```

## What the page does

- Wide screens: the launch sits in the middle, with branches on both sides joined by curves.
- Narrow screens: the launch on top, then the branches in one column.
- The Sources list and the Not traced list sit under the map.
- Light and dark follow the viewer's system setting.
- Every label is real text on the page, so it can be selected and searched.

## A redraft

A redraft writes `launch-map-vN.html` and changes nothing else. The first version stays as it was.
