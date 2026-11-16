"""The Snapshot step: fetch a merged pull request with `gh api` and start its run record.

Usage: python snapshot.py OWNER/REPO NUMBER --runs RUNS_FOLDER

The model never writes the Snapshot. Code saves the title, the body, the merge date and the diff
exactly as GitHub returned them. A run record that already exists is left untouched, so a second wake
on the same pull request continues the first run instead of starting a new one.
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

MONTHS = ("January", "February", "March", "April", "May", "June", "July", "August", "September",
          "October", "November", "December")


class NotMerged(Exception):
    pass


def run_gh(args):
    return subprocess.run(["gh", *args], capture_output=True, text=True, encoding="utf-8", check=True).stdout


def merged_on(stamp):
    day = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    return f"{day.day} {MONTHS[day.month - 1]} {day.year}"


def fetch(repo, number, runs, gh=run_gh):
    folder = Path(runs) / f"pr-{number}"
    if (folder / "run.json").is_file():
        return folder
    api = ["api", f"repos/{repo}/pulls/{number}"]
    pull = json.loads(gh(api))
    if not pull.get("merged"):
        raise NotMerged(f"pull request {number} in {repo} is not merged")
    diff = gh([*api, "-H", "Accept: application/vnd.github.diff"])
    body = (pull.get("body") or "").replace("\r\n", "\n").strip()
    text = f"# {pull['title']}\n\n{body}\n\nMerged on {merged_on(pull['merged_at'])}.\n\n## Diff\n\n{diff}"
    run = {
        "id": folder.name,
        "source": {"kind": "pull_request", "title": pull["title"], "link": pull.get("html_url", ""),
                   "author": pull.get("user", {}).get("login", ""), "received": pull["merged_at"],
                   "do_not_say": [], "open_questions": []},
        "record_link": f"https://github.com/{repo}/tree/launch-log/runs/{folder.name}",
        "mode": "suggest",
        "claims": [],
        "gates": {},
        "steps": {"snapshot": "done"},
        "times": {"received": pull["merged_at"]},
    }
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "snapshot.md").write_text(text, "utf-8", newline="\n")
    (folder / "run.json").write_text(json.dumps(run, indent=2) + "\n", "utf-8", newline="\n")
    return folder


def main(argv=None):
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Save the Snapshot of a merged pull request.")
    parser.add_argument("repo")
    parser.add_argument("number", type=int)
    parser.add_argument("--runs", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        print(fetch(args.repo, args.number, args.runs))
    except NotMerged as problem:
        print(f"FAIL {problem}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
