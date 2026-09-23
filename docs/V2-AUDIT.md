# V2 audit

Reviewed 13 September 2026. Scope: a local, agent-assisted package builder. The included example uses Launch Factory's own v2 release notes and a silent browser recording of those notes.

## What changed

The v1 command copied adapter instructions into output folders and printed DONE. Its 72 passing tests did not establish real media output. V2 replaces that path with a local validator and renderer. The generated package includes a captioned MP4, blog, five emails, changelog, HTML/CSS animation, popup, and two-week campaign.

Removed the retired campaign state machine, instruction-copying adapters, placeholder fixtures, old walkthroughs, and two duplicate repository inventories. Git preserves their history. Channel specialists and their active checks remain. The plugin entry point now uses the canonical operator protocol.

## Executed checks

| Check | Result |
|---|---|
| `pytest -q` | 67 passed; includes 17 v2 cases and retained specialist tests |
| `python scripts/sync_specialists.py --check` | 78 generated entry-point files match |
| `ruff check --isolated --select E4,E7,E9,F launch_factory.py tests/test_v2.py` | Passed; Ruff was a local development tool |
| Build bundled v2 example, then `verify` | 36 hashed files; `human_approved: false` |
| FFmpeg decode of the full rendered MP4 | Passed; 12-second video |
| Chromium, 390 and 1440 px | 24 page checks; no horizontal overflow or JavaScript errors |
| Automated accessibility scan on those pages | No WCAG A/AA violations reported by axe |
| Interactive behavior | Video advances; pause works; popup opens and dismisses with Escape; reduced motion stops animation |
| Visual inspection | Review-page screenshot and captioned video frame inspected |
| Optional preparation workflows | 23 channel cases, 15 UGC cases, 5 loader cases; generated workflow matches |
| Forge SOP lint | 0 errors; 5 acronym warnings |

FFprobe and FFmpeg restrict accepted media formats and local protocols. A playlist disguised as footage is refused.

The tests stop on stale source quotes, absent Claims Lock, escaping paths, unexpected social keys, changed inputs during render, modified outputs, and symlinks in packages. An extra nested MANIFEST.json is detected as a changed file set.

Recovery was exercised: a failed render removes its partial directory, preserves an earlier package, and refuses overwrite. The test also confirms the prior manifest bytes remain unchanged when a rebuild targets an existing folder.

## Independent review

A separate Forge reviewer checked the operating procedure against the code and reproduced its material findings. Fixes cover output path escape, source/decision changes during rendering, and package file-set checks. Targeted regression tests pass. The SOP remains **Ready for Owner Review**; an engineering pass does not approve a company's policy or the campaign's content.

SDS A1/B1 mapped source, drafting, rendering, and human decision boundaries. A2 examined the risk of treating a successful build as content approval. The output page, manifest, and operating guide keep that decision with the person.

Ponytail audit and review removed unused execution paths and duplicate instructions. The renderer uses Python's standard library, FFmpeg, and native browser components. No provider framework, queue, or approval database was added.

## Limits of this evidence

The example has no human approval. The video is silent; its audio-mixing quality has not been assessed. Automated accessibility checks do not replace a person's usability review. Source hashes and claim IDs cannot judge meaning, brand fit, or creative quality.

The AI host prepares drafts using the supplied protocols. The CLI makes no model or provider calls. Native host delegation, transcription, hosted intake, authenticated approvals, and publication were not tested or added. The manifest detects edits to a trusted local package; it is not a signature.

Find Skills and Skill Scout located existing evaluation and review skills. The requested production-agent article exposed only its introduction before a paywall. No tool was selected on the basis of its unavailable list.
