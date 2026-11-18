"""Build the standalone launch-factory skill from the plugin's skills/launch/ folder.

Usage: python scripts/build_skill.py [--out DIR]

Writes DIR/launch-factory/ (a skill folder) and DIR/launch-factory-skill.zip, whose top entry is
launch-factory/SKILL.md. DIR defaults to dist/ in the repository. It refuses to overwrite an earlier build.
Standard library only. Exits 1 with a message, and writes nothing, when the source no longer matches
what the build expects.
"""
import argparse
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
    (f" Starts only when the user types {PLUGIN_COMMAND}.",
     f" Use when the user types {SKILL_COMMAND}, or pastes a briefing, links or a team thread about a product launch"
     " and asks for launch drafts."),
]


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
    return head + rest


def converted_files():
    """Return (relative path, bytes) for every file of the skill, after the plugin-to-skill rewrite."""
    if not (SOURCE / "SKILL.md").is_file():
        raise BuildError(f"no SKILL.md in {SOURCE}")
    out = []
    top = SOURCE / "SKILL.md"
    for src in sorted((p for p in SOURCE.rglob("*") if p.is_file()), key=lambda p: (p != top, p.as_posix())):  # SKILL.md first
        rel = src.relative_to(SOURCE).as_posix()
        data = src.read_bytes()
        if src.suffix == ".md":
            text = data.decode("utf-8")
            if rel == "SKILL.md":
                text = skill_text(text)
            text = text.replace(PLUGIN_COMMAND, SKILL_COMMAND)
            data = text.encode("utf-8")
        out.append((rel, data))
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
