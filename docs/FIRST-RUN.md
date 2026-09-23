# First run

Install Python 3.10+ and FFmpeg with subtitles support. From the repository root:

```bash
./run.sh examples/v2-release --example --out runs/v2-example
python3 launch_factory.py verify runs/v2-example
python3 -m http.server 8768 --bind 127.0.0.1 --directory runs/v2-example
```

Open http://127.0.0.1:8768 to inspect every asset. The example contains real release notes and a silent recorded walkthrough of this project. It records no human approval. Choose a new output folder when repeating the build.

For your own release, follow [the operating guide](OPERATE-LAUNCH-FACTORY.md). Your AI host prepares the source quotes, then stops for a person to record Claims Lock before drafting. The command line renders prepared content; it does not call a model.
