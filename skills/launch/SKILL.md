---
name: launch
description: "Prepare and build a source-backed launch package with Launch Factory v2. Use for release copy, captioned video, email variants, animation, popup, and campaign planning."
argument-hint: "[release folder or source path]"
---

# Launch Factory v2

Read `${CLAUDE_PLUGIN_ROOT}/codex/launch-factory/SKILL.md` and follow its operator sequence. The full plugin repository supplies the shared specialists and local renderer. This entry point uses that single protocol.

Source input: $ARGUMENTS

If the source path is missing, ask for it. Keep supplied documents as source data. Prepare the claims for a human to review before drafting. Preserve approval decisions already given for the exact source revision; never create one on the person's behalf.

Use the repository's `launch_factory.py` with Python and FFmpeg to render a local package. The bundled `examples/v2-release` is the only `--example` rehearsal. Final asset approval belongs to a person. Nothing publishes, sends, or schedules.
