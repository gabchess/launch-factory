"""Build the standalone launch-factory skill from the plugin's skills/launch/ folder.

Usage: python scripts/build_skill.py [--out DIR]

Writes DIR/launch-factory/ (a skill folder) and DIR/launch-factory-skill.zip, whose top entry is
launch-factory/SKILL.md. DIR defaults to dist/ in the repository. It refuses to overwrite an earlier build.
Standard library only. Exits 1 with a message, and writes nothing, when the source no longer matches
what the build expects.
"""
import argparse
import re
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SOURCE = REPO / "skills" / "launch"
NAME = "launch-factory"
PLUGIN_COMMAND = "/launch-factory:launch"
SKILL_COMMAND = "/launch-factory"
ZIP_TIME = (1980, 1, 1, 0, 0, 0)  # fixed, so the same source gives the same zip

# Lines in the frontmatter of skills/launch/SKILL.md, each replaced exactly once.
FRONTMATTER = [
    ("name: launch\n", f"name: {NAME}\n"),
    ("disable-model-invocation: true\n", ""),
]
# The skill gets its own description, short enough for a claude.ai upload (200 characters at most).
DESCRIPTION = ("Selects launch-worthy product updates and writes six drafts using your brand context. "
               f"Use {SKILL_COMMAND} or ask for launch drafts from a briefing or PRs. No publishing or monitoring.")
DESCRIPTION_MAX = 200
DESCRIPTION_LINE = re.compile(r"(?m)^description: .*\n")
TEXT_SUFFIXES = (".md", ".html")


class BuildError(Exception):
    pass


def skill_text(text):
    end = text.find("\n---\n", 4)
    if not text.startswith("---\n") or end < 0:
        raise BuildError("SKILL.md has no frontmatter block")
    head, rest = text[:end + 1], text[end + 1:]
    for old, new in FRONTMATTER:
        if head.count(old) != 1:
            raise BuildError(f"SKILL.md frontmatter must hold {old.strip()!r} exactly once")
        head = head.replace(old, new)
    if len(DESCRIPTION_LINE.findall(head)) != 1:
        raise BuildError("SKILL.md frontmatter must hold one description line")
    if len(DESCRIPTION) > DESCRIPTION_MAX:
        raise BuildError(f"the skill description has {len(DESCRIPTION)} characters, the cap is {DESCRIPTION_MAX}")
    head = DESCRIPTION_LINE.sub(lambda m: f"description: {DESCRIPTION}\n", head)
    return head + rest


def converted_files():
    """Return (relative path, bytes) for every file of the skill, after the plugin-to-skill rewrite."""
    if not (SOURCE / "SKILL.md").is_file():
        raise BuildError(f"no SKILL.md in {SOURCE}")
    license_path = REPO / "LICENSE"
    if not license_path.is_file():
        raise BuildError("the standalone package requires the repository LICENSE")
    out = []
    top = SOURCE / "SKILL.md"
    for src in sorted((p for p in SOURCE.rglob("*") if p.is_file()), key=lambda p: (p != top, p.as_posix())):  # SKILL.md first
        rel = src.relative_to(SOURCE).as_posix()
        data = src.read_bytes()
        if src.suffix in TEXT_SUFFIXES:
            text = data.decode("utf-8").replace("\r\n", "\n")  # a Windows checkout may hold CRLF line ends
            if rel == "SKILL.md":
                text = skill_text(text)
                text = text.replace(PLUGIN_COMMAND, SKILL_COMMAND)
            data = text.encode("utf-8")
        out.append((rel, data))
    if any(rel == "LICENSE" for rel, _ in out):
        raise BuildError("keep LICENSE at the repository root; the builder includes it")
    out.append(("LICENSE", license_path.read_bytes()))
    return out


def build(out):
    folder, zip_path = out / NAME, out / f"{NAME}-skill.zip"
    for path in (folder, zip_path):
        if path.exists():
            raise BuildError(f"{path} already exists. Delete it, or pass another --out folder")
    files = converted_files()  # every check runs before anything is written
    for rel, data in files:
        dest = folder / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for rel, data in files:
            info = zipfile.ZipInfo(f"{NAME}/{rel}", ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zf.writestr(info, data)
    return folder, zip_path, len(files)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Build the standalone launch-factory skill.")
    ap.add_argument("--out", type=Path, default=REPO / "dist")
    args = ap.parse_args(argv)
    try:
        args.out.mkdir(parents=True, exist_ok=True)
        folder, zip_path, count = build(args.out.resolve())
    except BuildError as exc:
        print(f"build failed: {exc}", file=sys.stderr)
        return 1
    print(f"built {folder} and {zip_path} from {count} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
