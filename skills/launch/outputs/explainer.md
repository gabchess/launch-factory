# Explainer

One HTML file of captioned scenes that advance on their own, plus a script. It has no video and no voice. Each scene shows a headline and a caption. Nothing moves inside a scene.

## The spec

The agent writes one JSON object.

| Field | Type | Rule |
|---|---|---|
| `title` | text | Shown above the scene and used as the page title. |
| `scenes` | list | One or more scenes, in the order they play. |
| `scenes[].headline` | text | Short on-screen headline, up to about 8 words. |
| `scenes[].caption` | text | One or two sentences. It is the line a person would read aloud. |
| `scenes[].duration` | number | Seconds the scene stays on screen. Above 0. Allow about 3 seconds for every 8 words of caption, and not less than 2. |
| `scenes[].source` | number or text, optional | The source marker, such as `1`, matching the numbered Sources list of the launch. Shown as "Source 1". |
| `end.headline` | text | Headline of the end card. |
| `end.caption` | text | One line on the end card, such as where to start. |

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
  "end": {"headline": "Try saved views", "caption": "Open the sidebar and press Save view."}
}
```

## How the page plays

- Scene `n` is on screen from the sum of the earlier durations up to, but not including, the sum through `n`. After the last scene the end card shows and playback stops.
- The page shows scene, caption and end card as a pure function of time. `window.renderAt(seconds)` draws the page at that second. It is how a test or a still frame reads any moment.
- Play and Pause start and stop the clock. Replay starts again from 0. The progress bar shows position over total time.
- If the spec is wrong, the page shows "Spec error:" with the path of the bad field, for example `scenes[1].duration must be a number of seconds above 0`, and plays nothing.

## The script

The script is a plain text file in Markdown, saved beside the HTML, `explainer-script.md`. One line per scene, in scene order, and one last line for the end card. Each line is the words a person would read aloud, the same as that scene's caption.

```
Every week, teams rebuild the same filters by hand.
Now you save a filter once and share it with a link.
Switch between views from the sidebar.
Open the sidebar and press Save view.
```

The script has no headings, no numbers and no stage directions. The number of lines equals the number of scenes plus one.

## How the agent fills the template

1. Copy `templates/explainer.html` to `launch/<name>/explainer.html`.
2. Replace the JSON between `<!-- LF:SPEC-BEGIN -->` and `<!-- LF:SPEC-END -->` with the new spec. Keep the `<script type="application/json" id="launch-spec">` tags. Change nothing else in the file.
3. Write `explainer-script.md` from the same captions.
4. Open the page and check that no "Spec error:" shows. If it does, fix the named field and open it again.
