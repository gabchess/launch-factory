# Launch Factory

<p align="center">
  <img src="docs/logo.svg" alt="Launch Factory mark" width="240" height="160">
</p>

<p align="center"><strong>Turn release files into a campaign your team can review.</strong></p>

<p align="center">
  <a href="https://github.com/gabchess/launch-factory/releases"><img src="https://img.shields.io/badge/version-2.0.0-d4a574?labelColor=221e18" alt="version: 2.0.0"></a>
  <a href="docs/OPERATE-LAUNCH-FACTORY.md"><img src="https://img.shields.io/badge/output-local%20package-d4a574?labelColor=221e18" alt="output: local package"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-d4a574?labelColor=221e18" alt="license: MIT"></a>
</p>

An AI agent writes in Codex or Claude Code. Python then validates and renders the files for your team's approval. Nothing publishes, sends or schedules.

The package includes a captioned social video, blog post, five email variants, changelog, login animation and in-app popup, with a two-week campaign plan.

## Try it

[Download the example package](https://github.com/gabchess/launch-factory/releases/download/v2.0.0/launch-factory-v2-example.zip), [see the review page](docs/review-preview.png), or build it locally:

```sh
git clone https://github.com/gabchess/launch-factory.git
cd launch-factory
./run.sh examples/v2-release --example --out runs/v2-example
python3 -m http.server 8768 --bind 127.0.0.1 --directory runs/v2-example
```

Open **http://127.0.0.1:8768**. Requires Python 3.10+ and FFmpeg with the `subtitles` filter. Building needs no Python packages or paid API calls. Install FFmpeg with `brew install ffmpeg` on macOS or `sudo apt install ffmpeg` on Ubuntu.

The example uses this project's release notes and recorded documentation walkthrough. It produces a labelled rehearsal without human approval.

## Use your release

Open this repository in Codex or Claude Code and ask:

> Use Launch Factory v2 on my release folder. Read the source files, prepare the claims for my review, then draft the assets and build a package. Keep the writing short.

The [operator skill](codex/launch-factory/SKILL.md) guides drafting and review. Use the [example release.json](examples/v2-release/release.json) as your input template.

A person checks the claims and records that decision from their own terminal:

```sh
python3 launch_factory.py inspect MY_RELEASE
python3 launch_factory.py lock-claims MY_RELEASE --reviewer "Your name"
./run.sh MY_RELEASE --out runs/my-release-v1
python3 launch_factory.py verify runs/my-release-v1
```

`lock-claims` requires an interactive human response. Agents must stop there. The record binds approval to the claims and source bytes; it is a local record, not an authenticated approval service.

Review the output with the [checklist](docs/OPERATE-LAUNCH-FACTORY.md). Use a new output folder for each revision.

## Checks and limits

Changed sources invalidate Claims Lock. Missing claims, channels, footage or invalid captions stop the build. FFmpeg creates and probes the movie; the package records each file's hash. A failed build leaves earlier output untouched.

You review whether the sources support each claim and whether the writing and video are ready to use.

Bring readable sources, drafts, timed captions and footage. The tool does not transcribe Loom URLs, generate actor footage or run as a hosted app. The login animation is an HTML/CSS preview; Lottie export and installation are outside its scope.

## Development

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/pytest -q
.venv/bin/python scripts/sync_specialists.py --check
```

Tests cover source changes, path escapes, build recovery and modified outputs. With FFmpeg installed, they also render and decode a movie.

[Operating guide](docs/OPERATE-LAUNCH-FACTORY.md) · [Audit](docs/V2-AUDIT.md) · [Changelog](CHANGELOG.md) · [MIT license](LICENSE)
