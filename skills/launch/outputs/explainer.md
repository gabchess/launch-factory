# Explainer

One HTML file of captioned scenes, plus a script. It has no video and no voice. Each scene shows a headline and a caption. The viewer presses Play, and the scenes advance on a clock. Nothing moves inside a scene. The page also lists its Sources and what was Not traced.

## Reader

The audience the briefing names. If the briefing names none, write for a general user of the product and ask one question at the end of the turn: "Who is this for?"

## The spec

The agent writes one JSON object.

| Field | Type | Rule |
|---|---|---|
| `title` | text | Shown above the scene and used as the page title. |
| `scenes` | list | One or more scenes, in the order they play. |
| `scenes[].headline` | text | Short on-screen headline, up to about 8 words. |
| `scenes[].caption` | text | One or two sentences. It is the line a person would read aloud. |
| `scenes[].duration` | number | Seconds the scene stays on screen. Above 0. Allow about 3 seconds for every 8 words of caption, rounded up to a whole second, and not less than 2. |
| `scenes[].source` | whole number, optional | A number from 1 that points to `sources[n-1]`. Shown as "Source 1". Mark a scene only when a numbered source says it. |
| `end.headline` | text | Headline of the end card. |
| `end.caption` | text | One line on the end card, such as where to start. |
| `sources` | list of text | One entry per source, in order. Required. It is drawn as the Sources list. Each entry is the link the user gave, or "pasted text: <first five words>". A link that was not used is listed as "not used, because <reason>" and no scene points to it. A new source from a redraft goes at the end. |
| `notTraced` | list of text | One entry per claim you could not trace to a source, or per open question. Required, and empty when nothing is untraced. It is drawn as the Not traced list. |

Every `source` number must point into `sources`. A `source` number with no `sources` list, or larger than the list, is an error.

All text fields are plain text. Markup is not read.

### Example

```json
{
  "title": "Saved views, in one minute",
  "scenes": [
    {"headline": "Teams lose their filters", "caption": "Every week, teams rebuild the same filters by hand.", "duration": 4, "source": 1},
    {"headline": "Saved views", "caption": "Now you save a filter once and share it with a link.", "duration": 4, "source": 2},
    {"headline": "One click to switch", "caption": "Switch between views from the sidebar.", "duration": 3}
  ],
  "end": {"headline": "Try saved views", "caption": "Open the sidebar and press Save view."},
  "sources": ["https://example.com/pull/12", "pasted text: Saved views let you"],
  "notTraced": ["Whether saved views reach every plan"]
}
```

## How the page plays

- Scene `n` is on screen from the sum of the earlier durations up to, but not including, the sum through `n`. After the last scene the end card shows and playback stops.
- The page does not start by itself. The viewer presses Play. Play and Pause start and stop the clock. Replay starts again from 0. The progress bar shows position over total time.
- The page shows scene, caption and end card as a pure function of time. `window.renderAt(seconds)` draws the page at that second. It is how a test or a still frame reads any moment.
- The Sources list and the Not traced list sit under the controls and stay visible while it plays.
- If the spec is wrong, the page shows "Spec error:" with the path of the bad field, for example `scenes[1].duration must be a number of seconds above 0`, and plays nothing.

## The script

The script is a plain text file in Markdown, saved beside the HTML, `explainer-script.md`. One line per scene, in scene order, and one last line for the end card. Each line is the words a person would read aloud, the same as that scene's caption.

```
Every week, teams rebuild the same filters by hand.
Now you save a filter once and share it with a link.
Switch between views from the sidebar.
Open the sidebar and press Save view.
```

The script has no headings, no numbers and no stage directions. The number of lines equals the number of scenes plus one. The Sources and Not traced lists live in the HTML only.

## How the agent fills the template

1. Copy `templates/explainer.html` to `launch/<name>/explainer.html` by reading it and writing it out whole.
2. Replace the JSON text inside the `<script type="application/json" id="launch-spec">` tag, between the `<!-- LAUNCH-SPEC-START -->` and `<!-- LAUNCH-SPEC-END -->` comment lines, with the new spec. Keep both comment lines and the script tags. Change nothing else in the file.
3. Write every `<` inside the JSON as `\u003C`, so that no text in a caption can end the block or start a tag. The page reads `\u003C` back as `<`, so the viewer sees the original text. Use double quotes and no trailing commas.
4. Write `explainer-script.md` from the same captions.
5. Check the spec against the table above. Open the page when this surface can, and look for "Spec error:". If you cannot open it, say "not opened" in the status line. If an error shows, fix the named field and open it again.

## A redraft

A redraft writes `explainer-vN.html` and `explainer-script-vN.md` together, with the same N, and changes nothing else. The first version stays as it was.
