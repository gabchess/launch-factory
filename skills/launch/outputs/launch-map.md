# Launch map

One HTML file with a flowchart, a diagram of the launch details and a closing summary. The launch is the center of the details map, and each branch is one part of it, such as audience, message, content, timeline and risks. Those names are examples. Draw a branch only when a source supports it, and never invent one to fill the diagram.

The file is `templates/launch-map.html`. It makes no network call and loads no external font, script or image. It uses locally available Proxima Nova or a system sans fallback. You write a small JSON spec, and the template's own script draws it, with a Sources list and a Not traced list under the map. Read `references/html-design.md` for the shared design, copy and inspection rules.

## Plan the flow

Include two to six steps with a clear order supported by the sources. Name that relationship in `flowTitle`, such as "How an admin exports responses". If the sources do not describe product steps, show the order of the supported launch story, or explicitly label proposed actions as a "Suggested launch plan" and record undecided actions in `notTraced`. Do not turn a story order into a causal claim or invent product behavior. Follow the flow with the existing details map, then end with one to three source-backed takeaways in `summary`.

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
| `flowTitle` | new drafts | Short heading that explains what the arrows mean. Required when `flow` is present. |
| `flow` | new drafts | A list of 2 to 6 steps in order. Each has `label` (required), `note` and `source` (optional), with no nested items. |
| `summary` | new drafts | A list of 1 to 3 non-empty takeaway sentences. Cite supported claims with inline source numbers, such as `[1]`. Closes the visual before the source appendix. |
| `center` | yes | The launch itself. An object with `label` (required), and `note` and `source` (optional). |
| `branches` | yes | A list of 1 to 8 branches. |
| `branches[].label` | yes | Short name, a few words. |
| `branches[].note` | no | One short sentence. |
| `branches[].source` | no | A whole number from 1. Points to `sources[n-1]` and shows as `[n]`. |
| `branches[].items` | no | Up to 6 smaller nodes under the branch. Each has `label` (required), `note` and `source` (optional). Items have no items of their own. |
| `sources` | yes | A list of text, one entry per source, in order. Each entry is the link the user gave, or "pasted text: <first five words>". A link that was not used is listed as "not used, because <reason>" and nothing points to it. A new source from a redraft goes at the end. |
| `notTraced` | yes | A list of text, one entry per claim you could not trace to a source, or per open question. Empty when nothing is untraced. |

Every `source` number, on the center, a flow step, a branch or an item, must point into `sources`. A `source` number with no `sources` list, or larger than the list, is an error. Earlier specs without `flow`, `flowTitle` and `summary` still render their original details map; all newly generated specs include them.

Fields not listed here are ignored. Keep labels short, because they sit in boxes. Mark a claim with `source` only when a numbered source says it.

## Example

```json
{
  "title": "Northwind Sync 2.0 launch",
  "subtitle": "Ship date 3 December, for existing customers first",
  "center": { "label": "Northwind Sync 2.0", "note": "Offline editing for the mobile apps", "source": 1 },
  "flowTitle": "The launch story",
  "flow": [
    { "label": "Field teams face poor signal", "source": 2 },
    { "label": "Edit while offline", "source": 1 },
    { "label": "Sync when back online", "source": 1 }
  ],
  "branches": [
    { "label": "Audience", "note": "Existing mobile customers on the Team plan", "source": 1,
      "items": [
        { "label": "Field teams", "note": "Work with poor signal", "source": 2 },
        { "label": "Admins" }
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
  "notTraced": ["Whether admins get a rollout switch"],
  "summary": ["Existing Team-plan mobile customers can edit offline and sync when back online. [1]"]
}
```

## What the page does

- The flow runs left to right on wide screens and top to bottom on narrow screens, with arrows showing the stated order.
- Wide details map: the launch sits in the middle, with branches on both sides joined by curves. These curves show membership, not a sequence.
- Narrow details map: the launch on top, then the branches in one column.
- The Sources list and the Not traced list sit under the map.
- The background always uses a black-to-blue gradient with high-contrast panels.
- A closing summary ends the visual, followed by the sources and open questions as an appendix.
- Every label is real text on the page, so it can be selected and searched.

## A redraft

A redraft writes `launch-map-vN.html` and changes nothing else. The first version stays as it was.
