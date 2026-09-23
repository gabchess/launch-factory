# Troubleshooting

| Error or symptom | Next action |
|---|---|
| Missing FFmpeg or ffprobe | Install FFmpeg, then confirm its subtitles filter is available. |
| Missing or stale Claims Lock | Have the person review the current claims and run lock-claims in their terminal. |
| Quote mismatch | Check the exact source text and character offset; repeat Claims Lock after any source change. |
| Missing footage or invalid timing | Supply local MP4/MOV/WebM and captions within the chosen cut. |
| Output directory already exists | Choose a new revision folder. Earlier output is preserved. |
| Source or decision changed during build | Stop editing the inputs, review their current revision, then rebuild. |
| Modified package fails verify | Keep the previous verified package and build a fresh revision from source. |
| Skill files exist but the host cannot find them | Open the full repository and verify project skill discovery on that host. |

Run `python3 launch_factory.py --help` for command names. Build failures return a nonzero status and leave no completed output. If an input correction still fails, show the error and missing evidence to the operator before retrying again.
