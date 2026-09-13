"""Behavior checks for the real package path, including failure and recovery."""

import shutil

import pytest

import launch_factory as lf

EXAMPLE = lf.ROOT / "examples/v2-release"


@pytest.fixture
def release(tmp_path):
    root = tmp_path / "source"
    shutil.copytree(EXAMPLE, root)
    data = lf.read_json(root / "release.json")
    return root, data


def test_sources_bind_quote_bytes_and_revision(release):
    root, data = release
    _, before = lf.source_record(root, data)
    source = root / data["claims"][0]["source"]
    source.write_text(source.read_text() + "\nChanged revision.\n")
    _, after = lf.source_record(root, data)
    assert before != after
    data["claims"][0]["quote"] = "Invented feature"
    with pytest.raises(ValueError, match="quote"):
        lf.source_record(root, data)


@pytest.mark.parametrize(
    "kind",
    [
        "traversal",
        "symlink",
        "missing",
        "too_many",
        "bad_caption",
        "bad_claim",
        "missing_channel",
        "extra_social",
    ],
)
def test_bad_inputs_stop(release, tmp_path, kind):
    root, data = release
    if kind == "traversal":
        data["claims"][0]["source"] = "../secret.txt"
    elif kind == "symlink":
        p = root / "link.txt"
        p.symlink_to(root / data["claims"][0]["source"])
        data["claims"][0]["source"] = "link.txt"
    elif kind == "missing":
        data["video"]["footage"] = "absent.mp4"
    elif kind == "too_many":
        data["emails"].append(data["emails"][0])
    elif kind == "bad_caption":
        data["video"]["captions"][0]["end"] = 40
    elif kind == "bad_claim":
        data["blog"]["body"][0]["claims"] = ["unknown"]
    elif kind == "extra_social":
        data["written_social"]["../../escaped"] = data["written_social"]["x"]
    else:
        data["campaign"] = [r for r in data["campaign"] if r["channel"] != "x"]
    with pytest.raises((ValueError, OSError)):
        lf.validate(root, data)


def test_claims_lock_required_and_stale(release, tmp_path):
    root, _ = release
    out = tmp_path / "output"
    with pytest.raises(ValueError, match="claims-lock.json"):
        lf.build(root, out)
    lf.write_json(
        root / "claims-lock.json",
        {
            "decision": "approved",
            "reviewer": "TEST FIXTURE ONLY",
            "claims_sha256": "stale",
        },
    )
    with pytest.raises(ValueError, match="stale"):
        lf.build(root, out)
    assert not out.exists()
    with pytest.raises(ValueError, match="bundled"):
        lf.build(root, out, example=True)


def test_noninteractive_agent_cannot_lock(release, monkeypatch):
    root, _ = release
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)
    with pytest.raises(ValueError, match="interactive human"):
        lf.lock_claims(root, "not a human decision")
    assert not (root / "claims-lock.json").exists()


@pytest.mark.skipif(
    not shutil.which("ffmpeg"), reason="FFmpeg is needed for real media"
)
def test_real_six_output_build_and_tamper_detection(tmp_path):
    out = lf.build(EXAMPLE, tmp_path / "package", example=True)
    result = lf.verify(out)
    assert result["ok"] and not result["human_approved"]
    assert len(list((out / "emails").glob("[0-9][0-9].html"))) == 5
    assert (out / "popup/graphic.svg").read_text().startswith("<svg")
    assert "<dialog" in (out / "popup/index.html").read_text()
    assert "@keyframes" in (out / "animation/index.html").read_text()
    info = lf.probe(out / "social/video.mp4")
    assert 11.9 <= float(info["format"]["duration"]) <= 12.1
    # Decode all frames, not just a header probe.
    lf.run_process(
        [
            "ffmpeg",
            "-nostdin",
            "-v",
            "error",
            "-i",
            str(out / "social/video.mp4"),
            "-f",
            "null",
            "-",
        ],
        tmp_path,
    )
    manifest = (out / "MANIFEST.json").read_bytes()
    with pytest.raises(ValueError, match="new output"):
        lf.build(EXAMPLE, out, example=True)
    assert (out / "MANIFEST.json").read_bytes() == manifest
    (out / "evidence/MANIFEST.json").write_text("{}")
    with pytest.raises(ValueError, match="file set"):
        lf.verify(out)
    (out / "evidence/MANIFEST.json").unlink()
    (out / "linked").symlink_to(out / "evidence", target_is_directory=True)
    with pytest.raises(ValueError, match="symlinks"):
        lf.verify(out)
    (out / "linked").unlink()
    (out / "blog/blog.md").write_text("changed")
    with pytest.raises(ValueError, match="Output changed"):
        lf.verify(out)


def test_failed_render_leaves_prior_package_and_no_partial_output(
    tmp_path, monkeypatch
):
    previous = tmp_path / "previous"
    previous.mkdir()
    (previous / "keep").write_text("unchanged")
    destination = tmp_path / "next"

    def fail(*args):
        (args[0] / "partial.txt").write_text("partial")
        raise ValueError("render failed")

    monkeypatch.setattr(lf, "render", fail)
    with pytest.raises(ValueError, match="render failed"):
        lf.build(EXAMPLE, destination, example=True)
    assert not destination.exists()
    assert (previous / "keep").read_text() == "unchanged"
    assert not list(tmp_path.glob(".launch-*"))


@pytest.mark.skipif(
    not shutil.which("ffmpeg"), reason="FFmpeg is needed for real media"
)
@pytest.mark.parametrize("changed", ["source", "footage", "lock"])
def test_inputs_changed_during_render_abort(release, tmp_path, monkeypatch, changed):
    root, data = release
    _, fingerprint = lf.validate(root, data)
    # Test-only record exercises the normal path; it is never shipped as approval.
    lock = root / "claims-lock.json"
    lf.write_json(
        lock,
        {
            "decision": "approved",
            "reviewer": "TEST FIXTURE ONLY",
            "claims_sha256": fingerprint,
        },
    )
    target = {
        "source": root / data["claims"][0]["source"],
        "footage": root / data["video"]["footage"],
        "lock": lock,
    }[changed]
    original = lf.run_process

    def mutate_after_encoding(args, cwd, timeout=120):
        result = original(args, cwd, timeout)
        if args[0] == "ffmpeg":
            target.write_bytes(target.read_bytes() + b"\n")
        return result

    monkeypatch.setattr(lf, "run_process", mutate_after_encoding)
    out = tmp_path / "changed-package"
    with pytest.raises(ValueError, match="changed"):
        lf.build(root, out)
    assert not out.exists()
    assert not list(tmp_path.glob(".launch-*"))


@pytest.mark.skipif(not shutil.which("ffprobe"), reason="FFprobe is needed")
def test_playlist_disguised_as_footage_is_refused(tmp_path):
    disguised = tmp_path / "not-a-movie.mp4"
    disguised.write_text(
        "#EXTM3U\n#EXT-X-TARGETDURATION:10\n#EXTINF:10,\nfile:///outside.ts\n#EXT-X-ENDLIST\n"
    )
    with pytest.raises(ValueError, match="failed"):
        lf.probe(disguised)
