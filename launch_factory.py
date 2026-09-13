#!/usr/bin/env python3
"""Build a local launch package. AI drafts; code checks and renders; people approve."""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

VERSION = "2.0.0"
ROOT = Path(__file__).resolve().parent
CHANNELS = {
    "blog",
    "email",
    "changelog",
    "popup",
    "login",
    "linkedin",
    "x",
    "threads",
    "ig",
    "tiktok",
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_json(path: Path) -> dict:
    if path.stat().st_size > 1_000_000:
        raise ValueError(f"JSON exceeds 1 MB: {path.name}")
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object: {path.name}")
    return value


def local_file(root: Path, name: str, limit: int = 1_000_000) -> Path:
    if not isinstance(name, str) or not name or Path(name).is_absolute():
        raise ValueError("Source paths must be relative to the release folder")
    candidate = root / name
    if ".." in Path(name).parts or any(
        part.startswith(".") for part in Path(name).parts
    ):
        raise ValueError(f"Hidden or parent paths are not allowed: {name}")
    if any(
        p.is_symlink()
        for p in [candidate, *candidate.parents]
        if p != root and root in p.parents
    ):
        raise ValueError(f"Symlinks are not allowed: {name}")
    path = candidate.resolve()
    if (
        not path.is_relative_to(root)
        or not path.is_file()
        or path.stat().st_size > limit
    ):
        raise ValueError(f"Missing, outside, or oversized input: {name}")
    return path


def text(value, name: str, maximum: int = 12000) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise ValueError(f"{name} must contain 1–{maximum} characters")
    return value


def source_record(folder: Path, data: dict) -> tuple[list[dict], str]:
    if data.get("format") != "launch-factory/v2":
        raise ValueError("Expected format launch-factory/v2")
    for name in ("product", "title", "version"):
        text(data.get(name), name, 150)
    claims = data.get("claims")
    if not isinstance(claims, list) or not 1 <= len(claims) <= 40:
        raise ValueError("Supply 1–40 claims with exact source quotes")
    sources, ids = {}, set()
    for claim in claims:
        if not isinstance(claim, dict):
            raise ValueError("Each claim must be an object")
        cid = text(claim.get("id"), "claim ID", 50)
        if not re.fullmatch(r"[A-Za-z0-9_-]+", cid) or cid in ids:
            raise ValueError(
                "Claim IDs must be unique letters, digits, underscores or hyphens"
            )
        ids.add(cid)
        quote = text(claim.get("quote"), "quote", 2000)
        text(claim.get("text"), "claim", 2000)
        path = local_file(folder, claim.get("source"))
        raw = path.read_bytes()
        source = raw.decode("utf-8")
        start = claim.get("start")
        if (
            type(start) is not int
            or start < 0
            or source[start : start + len(quote)] != quote
        ):
            raise ValueError(
                f"{cid}: quote does not match the source at the stated character offset"
            )
        sources[claim["source"]] = {
            "path": claim["source"],
            "sha256": digest(raw),
            "bytes": len(raw),
        }
    records = sorted(sources.values(), key=lambda x: x["path"])
    lock = {
        "product": data["product"],
        "title": data["title"],
        "version": data["version"],
        "claims": claims,
        "sources": records,
    }
    return records, digest(
        json.dumps(lock, sort_keys=True, ensure_ascii=False).encode()
    )


def block(value: dict, ids: set[str]) -> str:
    if not isinstance(value, dict):
        raise ValueError("Copy must be a text block with claim IDs")
    body = text(value.get("text"), "copy")
    refs = value.get("claims")
    if not isinstance(refs, list) or not refs or any(ref not in ids for ref in refs):
        raise ValueError("Every copy block needs existing claim IDs")
    return body


def paragraphs(values, ids: set[str]) -> list[str]:
    if not isinstance(values, list) or not 1 <= len(values) <= 30:
        raise ValueError("Supply 1–30 copy blocks")
    return [block(v, ids) for v in values]


def validate(folder: Path, data: dict) -> tuple[list[dict], str]:
    sources, fingerprint = source_record(folder, data)
    ids = {c["id"] for c in data["claims"]}
    date.fromisoformat(data["start_date"])
    ZoneInfo(data["timezone"])
    cta = data["cta"]
    text(cta["label"], "CTA label", 80)
    if not re.fullmatch(r'https://[^\s<>"\x00-\x1f]+', cta["url"]):
        raise ValueError("CTA must be an HTTPS URL")
    for name in ("blog", "changelog", "popup", "animation"):
        item = data[name]
        text(block(item["headline"], ids), "headline", 100)
        paragraphs(item["body"], ids)
    emails = data["emails"]
    if (
        not isinstance(emails, list)
        or len(emails) != 5
        or len({e["segment"] for e in emails}) != 5
    ):
        raise ValueError("Supply exactly five distinct email segments")
    for email in emails:
        text(email["segment"], "segment", 80)
        block(email["subject"], ids)
        paragraphs(email["body"], ids)
    if not isinstance(data["written_social"], dict) or set(data["written_social"]) != {
        "linkedin",
        "x",
        "threads",
    }:
        raise ValueError("Written social must contain only linkedin, x, and threads")
    for name in ("linkedin", "x", "threads"):
        paragraphs(data["written_social"][name], ids)
    video = data["video"]
    path = local_file(folder, video["footage"], 200_000_000)
    if path.suffix.lower() not in {".mp4", ".mov", ".webm"}:
        raise ValueError("Footage must be MP4, MOV or WebM")
    start, duration = video.get("start", 0), video["duration"]
    if (
        type(start) not in (int, float)
        or not 0 <= start <= 3600
        or type(duration) not in (int, float)
        or not 1 <= duration <= 30
    ):
        raise ValueError(
            "Use a 1–30 second cut with a start between 0 and 3600 seconds"
        )
    captions = video["captions"]
    if not isinstance(captions, list) or not 1 <= len(captions) <= 50:
        raise ValueError("Supply 1–50 timed captions")
    previous = 0
    for caption in captions:
        block(caption, ids)
        if (
            len(caption["text"]) > 160
            or "-->" in caption["text"]
            or "\n" in caption["text"]
        ):
            raise ValueError("Each caption must be a single line under 160 characters")
        begin, end = caption["start"], caption["end"]
        if (
            type(begin) not in (int, float)
            or type(end) not in (int, float)
            or not previous <= begin < end <= duration
        ):
            raise ValueError("Caption timing must be ordered and fit within the cut")
        previous = end
    plan = data["campaign"]
    if not isinstance(plan, list) or not 7 <= len(plan) <= 30:
        raise ValueError("Supply 7–30 campaign rows")
    if {row["channel"] for row in plan} != CHANNELS:
        raise ValueError(
            "Campaign must cover blog, email, changelog, popup, login, LinkedIn, X, Threads, IG and TikTok"
        )
    for row in plan:
        if type(row["day"]) is not int or not 0 <= row["day"] <= 13:
            raise ValueError("Campaign days must be between 0 and 13")
        text(row["audience"], "audience", 100)
        block(row["message"], ids)
    return sources, fingerprint


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def inspect_sources(folder: Path) -> dict:
    data = read_json(local_file(folder, "release.json"))
    sources, fingerprint = source_record(folder, data)
    return {"claims_sha256": fingerprint, "sources": sources, "claims": data["claims"]}


def lock_claims(folder: Path, reviewer: str) -> None:
    if (folder / "claims-lock.json").is_symlink():
        raise ValueError("Claims Lock cannot be written through a symlink")
    report = inspect_sources(folder)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if not sys.stdin.isatty():
        raise ValueError(
            "Claims Lock requires an interactive human review. Agents must stop here."
        )
    print(
        "Read each claim and its quote. Type LOCK CLAIMS to approve this exact source revision."
    )
    if input("Decision: ").strip() != "LOCK CLAIMS":
        raise ValueError("Claims were not locked")
    write_json(
        folder / "claims-lock.json",
        {
            "claims_sha256": report["claims_sha256"],
            "reviewer": text(reviewer, "reviewer", 100),
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "decision": "approved",
            "authority": "local operator record; not authenticated identity",
        },
    )


def run_process(args: list[str], cwd: Path, timeout: int = 120) -> str:
    try:
        result = subprocess.run(
            args, cwd=cwd, capture_output=True, text=True, timeout=timeout, check=False
        )
    except subprocess.TimeoutExpired as error:
        raise ValueError(
            f"{args[0]} exceeded {timeout}s; no package was completed"
        ) from error
    if result.returncode:
        raise ValueError(f"{args[0]} failed: {result.stderr[-2000:]}")
    return result.stdout


def probe(path: Path) -> dict:
    return json.loads(
        run_process(
            [
                "ffprobe",
                "-v",
                "error",
                "-protocol_whitelist",
                "file,pipe",
                "-format_whitelist",
                "mov,matroska,webm",
                "-show_streams",
                "-show_format",
                "-of",
                "json",
                str(path),
            ],
            path.parent,
            30,
        )
    )


def stamp(seconds: float) -> str:
    ms = round(seconds * 1000)
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def markup(blocks: list[dict]) -> str:
    return "".join(
        f'<p>{html.escape(b["text"])} <small class="refs">[{html.escape(", ".join(b["claims"]))}]</small></p>'
        for b in blocks
    )


def page(title: str, body: str, *, css: str = "", script: str = "") -> str:
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title><style>
:root{{color-scheme:dark}}*{{box-sizing:border-box}}body{{overflow-wrap:anywhere;margin:0;background:#201d18;color:#f2eade;font:17px/1.65 system-ui,sans-serif}}main{{max-width:1060px;margin:auto;padding:48px 24px}}h1,h2{{font-family:Georgia,serif;line-height:1.15;font-weight:400}}h1{{font-size:clamp(36px,6vw,64px)}}h2{{font-size:30px}}a{{color:#efb77e}}button,.button{{padding:12px 18px;border:1px solid #efb77e;background:#efb77e;color:#201d18;border-radius:4px;cursor:pointer;font:inherit;min-height:44px}}:focus-visible{{outline:3px solid #efb77e;outline-offset:4px}}.eyebrow{{color:#efb77e;text-transform:uppercase;font-size:12px;letter-spacing:.12em}}.muted,.refs{{color:#c4baab}}.refs{{font-size:11px}}article,.card{{background:#29261f;border:1px solid #5b5142;border-radius:8px;padding:24px;margin:20px 0}}img,video,iframe{{max-width:100%}}video{{width:100%;background:#111}}iframe{{width:100%;height:420px;border:1px solid #5b5142;border-radius:8px}}.grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:20px}}.grid>*{{min-width:0}}table{{border-collapse:collapse;width:100%;font-size:14px}}td,th{{padding:12px;text-align:left;border-bottom:1px solid #5b5142}}.scroll{{overflow:auto}}@media(max-width:720px){{.grid{{grid-template-columns:1fr}}main{{padding:28px 20px}}}}@media(prefers-reduced-motion:reduce){{*,*::before,*::after{{animation:none!important;transition:none!important}}}}{css}</style></head><body><main>{body}</main>{script}</body></html>"""


def graphic(title: str, subtitle: str) -> str:
    import textwrap

    lines = textwrap.wrap(title, 34)[:3]
    words = "".join(
        f'<text x="64" y="{150 + i * 68}" font-family="Georgia,serif" font-size="54" fill="#f2eade">{html.escape(line)}</text>'
        for i, line in enumerate(lines)
    )
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630"><rect width="1200" height="630" fill="#201d18"/><rect x="30" y="30" width="1140" height="570" rx="12" fill="none" stroke="#786044"/>{words}<text x="64" y="526" font-family="sans-serif" font-size="24" fill="#efb77e">{html.escape(subtitle[:70])}</text></svg>'


def write_article(out: Path, name: str, item: dict, data: dict) -> None:
    md = (
        "# "
        + item["headline"]["text"]
        + "\n\n"
        + "\n\n".join(
            b["text"] + " [" + ", ".join(b["claims"]) + "]" for b in item["body"]
        )
    )
    md += f"\n\n[{data['cta']['label']}]({data['cta']['url']})\n"
    (out / f"{name}.md").write_text(md)
    image = '<img src="cover.svg" alt="Release title card">' if name == "blog" else ""
    (out / f"{name}.html").write_text(
        page(
            item["headline"]["text"],
            f'<p class="eyebrow">{html.escape(data["product"])} · v{html.escape(data["version"])}</p><h1>{html.escape(item["headline"]["text"])}</h1>{image}{markup(item["body"])}<a href="{html.escape(data["cta"]["url"], quote=True)}">{html.escape(data["cta"]["label"])}</a>',
        )
    )


def render(
    out: Path,
    folder: Path,
    data: dict,
    sources: list[dict],
    fingerprint: str,
    preview: bool,
    lock_bytes: bytes | None,
) -> None:
    esc = html.escape
    for directory in (
        "social",
        "blog",
        "emails",
        "changelog",
        "animation",
        "popup",
        "campaign",
        "evidence",
    ):
        (out / directory).mkdir()
    for name in ("blog", "changelog"):
        write_article(out / name, name, data[name], data)
    (out / "blog/cover.svg").write_text(
        graphic(data["blog"]["headline"]["text"], data["product"])
    )
    for i, email in enumerate(data["emails"], 1):
        item = {"headline": email["subject"], "body": email["body"]}
        write_article(out / "emails", f"{i:02d}", item, data)
    email_links = "".join(
        f'<li><a href="{i:02d}.html">{html.escape(e["segment"])}</a></li>'
        for i, e in enumerate(data["emails"], 1)
    )
    (out / "emails/index.html").write_text(
        page(
            "Email variants", "<h1>Choose an audience</h1><ul>" + email_links + "</ul>"
        )
    )
    popup = data["popup"]
    (out / "popup/graphic.svg").write_text(
        graphic(popup["headline"]["text"], data["product"])
    )
    popup_body = f'<p class="eyebrow">In-app preview</p><button id="open">Preview announcement</button><dialog aria-labelledby="popup-title"><button id="close" aria-label="Close announcement">Close</button><img src="graphic.svg" alt=""><h2 id="popup-title">{esc(popup["headline"]["text"])}</h2>{markup(popup["body"])}<a class="button" href="{esc(data["cta"]["url"], quote=True)}">{esc(data["cta"]["label"])}</a></dialog>'
    script = '<script>const d=document.querySelector("dialog");document.querySelector("#open").onclick=()=>d.showModal();document.querySelector("#close").onclick=()=>d.close();</script>'
    (out / "popup/index.html").write_text(
        page(
            "Announcement preview",
            popup_body,
            css="dialog{max-width:520px;width:calc(100% - 40px);background:#29261f;color:#f2eade;border:1px solid #786044;border-radius:12px;padding:24px}dialog::backdrop{background:#0009}dialog img{margin-top:20px}dialog .button{display:inline-block}",
            script=script,
        )
    )
    write_article(out / "popup", "copy", popup, data)
    animation = data["animation"]
    (out / "animation/poster.svg").write_text(
        graphic(animation["headline"]["text"], data["product"])
    )
    motion_body = f'<p class="eyebrow">{esc(data["product"])}</p><div class="motion"><span class="orb" aria-hidden="true"></span><h1>{esc(animation["headline"]["text"])}</h1>{markup(animation["body"])}</div><button id="motion" aria-pressed="false">Pause animation</button>'
    motion_css = ".motion{position:relative;overflow:hidden;padding:48px 24px;border:1px solid #786044;border-radius:12px}.motion>*:not(.orb){position:relative}.orb{position:absolute;width:240px;height:240px;border-radius:50%;background:radial-gradient(#efb77e55,transparent 70%);top:-60px;left:0;animation:drift 8s ease-in-out infinite alternate}@keyframes drift{to{transform:translate(260px,140px) scale(1.5)}}.paused .orb{animation-play-state:paused}"
    motion_script = '<script>const b=document.querySelector("#motion");b.onclick=()=>{const p=document.body.classList.toggle("paused");b.setAttribute("aria-pressed",p);b.textContent=p?"Play animation":"Pause animation"};</script>'
    (out / "animation/index.html").write_text(
        page("Login animation", motion_body, css=motion_css, script=motion_script)
    )
    video = data["video"]
    captions = "".join(
        f"{i}\n{stamp(c['start'])} --> {stamp(c['end'])}\n{c['text']}\n\n"
        for i, c in enumerate(video["captions"], 1)
    )
    (out / "social/captions.srt").write_text(captions)
    footage = local_file(folder, video["footage"], 200_000_000)
    footage_hash = digest(footage.read_bytes())
    info = probe(footage)
    if (
        not any(s["codec_type"] == "video" for s in info["streams"])
        or float(info["format"]["duration"]) + 0.05
        < video.get("start", 0) + video["duration"]
    ):
        raise ValueError(
            "Footage is shorter than the selected cut or has no video stream"
        )
    # Only local files reach FFmpeg. Never interpolate input names into its filter language.
    run_process(
        [
            "ffmpeg",
            "-nostdin",
            "-hide_banner",
            "-loglevel",
            "error",
            "-protocol_whitelist",
            "file,pipe",
            "-format_whitelist",
            "mov,matroska,webm",
            "-ss",
            str(video.get("start", 0)),
            "-i",
            str(footage),
            "-t",
            str(video["duration"]),
            "-map",
            "0:v:0",
            "-map",
            "0:a?",
            "-vf",
            "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,subtitles=captions.srt",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "23",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-movflags",
            "+faststart",
            "video.mp4",
        ],
        out / "social",
    )
    if digest(footage.read_bytes()) != footage_hash:
        raise ValueError("Footage changed during rendering")
    write_json(
        out / "evidence/footage.json",
        {
            "path": video["footage"],
            "sha256": footage_hash,
            "start": video.get("start", 0),
            "duration": video["duration"],
        },
    )
    for name, blocks in data["written_social"].items():
        (out / f"campaign/{name}.md").write_text(
            "\n\n".join(b["text"] + " [" + ", ".join(b["claims"]) + "]" for b in blocks)
            + "\n"
        )
    paths = {
        "blog": "../blog/blog.html",
        "email": "../emails/index.html",
        "changelog": "../changelog/changelog.html",
        "popup": "../popup/index.html",
        "login": "../animation/index.html",
        "linkedin": "linkedin.md",
        "x": "x.md",
        "threads": "threads.md",
        "ig": "../social/video.mp4",
        "tiktok": "../social/video.mp4",
    }
    rows = []
    for row in sorted(data["campaign"], key=lambda r: r["day"]):
        rows.append(
            {
                "date": str(
                    date.fromisoformat(data["start_date"]) + timedelta(days=row["day"])
                ),
                "timezone": data["timezone"],
                "channel": row["channel"],
                "audience": row["audience"],
                "message": row["message"]["text"],
                "asset": paths[row["channel"]],
                "status": "needs human review",
            }
        )
    with (out / "campaign/plan.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    k: ("'" + v if v.lstrip().startswith(("=", "+", "-", "@")) else v)
                    for k, v in row.items()
                }
            )
    table = (
        '<div class="scroll"><table><thead><tr><th>Date</th><th>Channel</th><th>Audience</th><th>Message</th><th>Asset</th></tr></thead><tbody>'
        + "".join(
            f'<tr><td>{r["date"]}</td><td>{r["channel"]}</td><td>{esc(r["audience"])}</td><td>{esc(r["message"])}</td><td><a href="{r["asset"]}">Review</a></td></tr>'
            for r in rows
        )
        + "</tbody></table></div>"
    )
    (out / "campaign/index.html").write_text(
        page(
            "Campaign plan",
            f'<p class="eyebrow">Proposed · {esc(data["timezone"])}</p><h1>Two-week campaign</h1><p>Every row needs human review. Nothing is scheduled.</p>{table}',
        )
    )
    for i, source in enumerate(sources, 1):
        raw = local_file(folder, source["path"]).read_bytes()
        if digest(raw) != source["sha256"]:
            raise ValueError(
                "A source changed during the build; restart from Claims Lock"
            )
        (out / f"evidence/source-{i:02d}.txt").write_bytes(raw)
        source["package_path"] = f"evidence/source-{i:02d}.txt"
    write_json(
        out / "evidence/claims.json",
        {"claims_sha256": fingerprint, "claims": data["claims"], "sources": sources},
    )
    write_json(out / "evidence/drafts.json", data)
    if not preview:
        if local_file(folder, "claims-lock.json").read_bytes() != lock_bytes:
            raise ValueError(
                "Claims decision changed during the build; restart from Claims Lock"
            )
        (out / "evidence/claims-lock.json").write_bytes(lock_bytes)
    (out / "REVIEW.md").write_text(
        "# Review this package\n\nStatus: draft.\n\nCheck claim meaning against each source. Read all five emails and the campaign sequence. Play the video with sound and inspect caption timing. Test the animation with reduced motion. Open and dismiss the popup. Check CTA targets before approval.\n\nRecord requested changes against the MANIFEST.json hash. Any changed source requires a new Claims Lock; any changed output needs another review. This local package cannot authenticate a reviewer or publish anything.\n"
    )
    checks = {
        "video": probe(out / "social/video.mp4"),
        "copy": "all blocks cite existing claim IDs; meaning requires human review",
        "media": "encoded video; browser/audio inspection required",
        "claims_lock": "example rehearsal; no human approval"
        if preview
        else "local operator record; identity not authenticated",
    }
    write_json(out / "checks.json", checks)
    cards = [
        (
            "01",
            "Social video",
            "social/video.mp4",
            '<video controls playsinline preload="metadata" src="social/video.mp4"></video>',
        ),
        ("02", "Blog", "blog/blog.html", '<img src="blog/cover.svg" alt="Blog cover">'),
        (
            "03",
            "Email variants",
            "emails/index.html",
            "<ul>"
            + "".join(
                f'<li><a href="emails/{i:02d}.html">{esc(e["segment"])}</a></li>'
                for i, e in enumerate(data["emails"], 1)
            )
            + "</ul>",
        ),
        (
            "04",
            "Changelog",
            "changelog/changelog.html",
            markup(data["changelog"]["body"]),
        ),
        (
            "05",
            "Login animation",
            "animation/index.html",
            '<iframe title="Login animation preview" src="animation/index.html"></iframe>',
        ),
        (
            "06",
            "In-app popup",
            "popup/index.html",
            '<img src="popup/graphic.svg" alt="Popup graphic">',
        ),
    ]
    body = f'<p class="eyebrow">Launch Factory · v{VERSION} · Review draft</p><h1>{esc(data["title"])}</h1><p class="muted">{esc(data["product"])} · Release {esc(data["version"])}</p><p>{"Example rehearsal. No human approval is recorded." if preview else "Claims Lock recorded locally. The finished assets still need human review."}</p><div class="grid">'
    body += "".join(
        f'<article><p class="eyebrow">{n}</p><h2>{title}</h2>{embed}<a href="{link}">Open {title.lower()} ↗</a></article>'
        for n, title, link, embed in cards
    )
    body += '</div><article><p class="eyebrow">Campaign</p><h2>One release, two weeks</h2><a href="campaign/index.html">Review the campaign plan ↗</a></article><p><a href="evidence/claims.json">Sources and claims</a> · <a href="REVIEW.md">Review checklist</a> · <a href="checks.json">Build checks</a></p>'
    (out / "index.html").write_text(page(data["title"], body))


def build(folder: Path, destination: Path, *, example: bool = False) -> Path:
    folder, destination = folder.resolve(), destination.resolve()
    if destination.exists() or destination.is_relative_to(folder):
        raise ValueError("Choose a new output directory outside the release folder")
    data = read_json(local_file(folder, "release.json"))
    sources, fingerprint = validate(folder, data)
    lock_bytes = None
    if example:
        if folder != (ROOT / "examples/v2-release").resolve():
            raise ValueError("--example is limited to the bundled, labelled rehearsal")
    else:
        lock_bytes = local_file(folder, "claims-lock.json").read_bytes()
        lock = json.loads(lock_bytes)
        if not isinstance(lock, dict):
            raise ValueError("Claims Lock must be a JSON object")
        if (
            lock.get("decision") != "approved"
            or lock.get("claims_sha256") != fingerprint
            or not lock.get("reviewer")
        ):
            raise ValueError(
                "Claims Lock is absent or stale. Have the human reviewer run lock-claims again."
            )
    for binary in ("ffmpeg", "ffprobe"):
        if not shutil.which(binary):
            raise ValueError(f"{binary} is required. Install FFmpeg before building.")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".launch-", dir=destination.parent) as temp:
        out = Path(temp) / "package"
        out.mkdir()
        render(out, folder, data, sources, fingerprint, example, lock_bytes)
        files = {
            str(p.relative_to(out)): digest(p.read_bytes())
            for p in sorted(out.rglob("*"))
            if p.is_file()
        }
        write_json(
            out / "MANIFEST.json",
            {
                "version": VERSION,
                "status": "review_draft",
                "human_approved": False,
                "example": example,
                "claims_sha256": fingerprint,
                "files": files,
            },
        )
        verify(out)
        out.rename(destination)
    return destination


def verify(folder: Path) -> dict:
    manifest = read_json(folder / "MANIFEST.json")
    if (
        manifest.get("version") != VERSION
        or manifest.get("human_approved") is not False
    ):
        raise ValueError("Expected a v2 review draft, not a claimed approval")
    files = manifest["files"]
    entries = list(folder.rglob("*"))
    if any(p.is_symlink() for p in entries):
        raise ValueError("Package symlinks are not allowed")
    actual = {
        str(p.relative_to(folder))
        for p in entries
        if p.is_file() and p != folder / "MANIFEST.json"
    }
    if actual != set(files):
        raise ValueError("Package file set has changed")
    for name, expected in files.items():
        path = local_file(folder, name, 200_000_000)
        if digest(path.read_bytes()) != expected:
            raise ValueError(f"Output changed: {name}")
    required = {
        "evidence/footage.json",
        "evidence/claims.json",
        "evidence/drafts.json",
        "emails/index.html",
        "index.html",
        "social/video.mp4",
        "social/captions.srt",
        "blog/blog.html",
        "blog/blog.md",
        "blog/cover.svg",
        "changelog/changelog.md",
        "animation/index.html",
        "animation/poster.svg",
        "popup/graphic.svg",
        "popup/index.html",
        "campaign/plan.csv",
        "campaign/index.html",
    } | {f"emails/{i:02d}.html" for i in range(1, 6)}
    if not required <= actual:
        raise ValueError("A required deliverable is missing")
    info = probe(folder / "social/video.mp4")
    if not 0.9 <= float(info["format"]["duration"]) <= 30.1 or not any(
        s["codec_type"] == "video" for s in info["streams"]
    ):
        raise ValueError("Encoded video failed duration/stream checks")
    return {"ok": True, "files": len(files), "human_approved": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", action="version", version=VERSION)
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("inspect", "lock-claims", "build", "verify"):
        p = sub.add_parser(command)
        p.add_argument("folder", type=Path)
        if command == "lock-claims":
            p.add_argument("--reviewer", required=True)
        if command == "build":
            p.add_argument("--out", required=True, type=Path)
            p.add_argument("--example", action="store_true")
    args = parser.parse_args()
    try:
        if args.command == "inspect":
            print(
                json.dumps(
                    inspect_sources(args.folder.resolve()), indent=2, ensure_ascii=False
                )
            )
        elif args.command == "lock-claims":
            lock_claims(args.folder.resolve(), args.reviewer)
        elif args.command == "build":
            print(build(args.folder, args.out, example=args.example))
        else:
            print(json.dumps(verify(args.folder.resolve()), indent=2))
        return 0
    except (
        ValueError,
        KeyError,
        TypeError,
        OSError,
        subprocess.SubprocessError,
    ) as error:
        print(f"STOP: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
