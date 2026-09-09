#!/usr/bin/env bash
# run.sh — Launch Factory one-command door (ADR 0014).
# Usage: ./run.sh RELEASE_FOLDER
# Ingest → validate → package. STRUCTURAL_INTEGRITY_ONLY: nothing publishes.
# Reviewer review cards land in the built package (REVIEWER.md) and reviewer/ at root.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_ROOT"

if [ "$#" -ne 1 ]; then
  echo "usage: ./run.sh RELEASE_FOLDER" >&2
  exit 2
fi
RELEASE_FOLDER="$1"

if [ ! -d "$RELEASE_FOLDER" ]; then
  echo "FAIL: release folder not found: $RELEASE_FOLDER" >&2
  echo "safest re-entry: check the path and re-run ./run.sh RELEASE_FOLDER" >&2
  exit 2
fi

PY="$REPO_ROOT/.venv/bin/python"

banner() {
  echo ""
  echo "=================================================================="
  echo "== STAGE $1: $2"
  echo "=================================================================="
}

fail() {
  echo "" >&2
  echo "FAILED CHECK: $1" >&2
  echo "SAFEST RE-ENTRY: $2" >&2
  exit 1
}

# ---- venv ------------------------------------------------------------------
banner 0 "environment"
if [ ! -x "$PY" ]; then
  echo "creating .venv ..."
  python3 -m venv .venv || fail "python3 -m venv .venv" "install Python 3.10+ and re-run ./run.sh $RELEASE_FOLDER"
  "$PY" -m pip install --quiet --upgrade pip
fi
"$PY" -c "import jsonschema" 2>/dev/null || {
  echo "installing requirements ..."
  "$PY" -m pip install --quiet -r requirements.txt \
    || fail "pip install -r requirements.txt" "fix network/pip, then re-run ./run.sh $RELEASE_FOLDER"
}
echo "python: $("$PY" --version) — jsonschema present"

FOLDER_NAME="$(basename "$RELEASE_FOLDER")"
RUN_WS="runs/$FOLDER_NAME"
RECORD="$RUN_WS/release-record.json"

# ---- stage 1: init_release -------------------------------------------------
banner 1 "init_release — ingest + record skeleton"
if [ -f "$RECORD" ]; then
  echo "record exists at $RECORD — resuming (not overwriting)"
else
  "$PY" engine/scripts/init_release.py "$RELEASE_FOLDER" --workspace "$RUN_WS" \
    || fail "engine/scripts/init_release.py $RELEASE_FOLDER" "inspect the release folder, then re-run ./run.sh $RELEASE_FOLDER"
  echo "record: $RECORD"
fi
"$PY" engine/scripts/validate_record.py "$RECORD" >/dev/null \
  || fail "validate_record on fresh record" "delete $RECORD only if you mean to re-ingest; otherwise fix the record"

# ---- locate campaign + ledger ----------------------------------------------
CAMPAIGN=""
for candidate in "$RELEASE_FOLDER/release_campaign.json" "engine/fixtures/$FOLDER_NAME/release_campaign.json"; do
  if [ -f "$candidate" ]; then CAMPAIGN="$candidate"; break; fi
done
LEDGER=""
for candidate in "$RELEASE_FOLDER/claim_ledger.json" "engine/fixtures/$FOLDER_NAME/claim_ledger.json"; do
  if [ -f "$candidate" ]; then LEDGER="$candidate"; break; fi
done
if [ -z "$CAMPAIGN" ]; then
  fail "no release_campaign.json found in $RELEASE_FOLDER (or engine/fixtures/$FOLDER_NAME)" \
       "add a release_campaign.json to the release folder and re-run ./run.sh $RELEASE_FOLDER"
fi
echo "campaign: $CAMPAIGN"

# ---- stage 2: validate_ledger ----------------------------------------------
banner 2 "validate_ledger — evidence spans + kill-switch"
if [ -n "$LEDGER" ]; then
  "$PY" engine/scripts/validate_ledger.py "$LEDGER" \
    || fail "validate_ledger on $LEDGER" "kill-switch armed or evidence missing — fix the ledger (Claims Lock draft for Reviewer), then re-run ./run.sh $RELEASE_FOLDER"
else
  echo "no claim_ledger.json found — SKIP (draft the ledger with Reviewer before packaging for real)"
fi

# ---- stage 3: validate_campaign --------------------------------------------
banner 3 "validate_campaign — seven slots exist-or-held, Reviewer WIP=1"
"$PY" engine/scripts/validate_campaign.py "$CAMPAIGN" \
  || fail "validate_campaign on $CAMPAIGN" "a slot is missing/held-without-reason or Reviewer WIP≠1 — fix the campaign JSON, then re-run ./run.sh $RELEASE_FOLDER"

CADENCE_DIR="$(dirname "$CAMPAIGN")"
if [ -f "$CADENCE_DIR/cadence_binder.json" ]; then
  echo "campaign plan data shape (cadence_binder.json) present — checked by validate_campaign module"
fi

# ---- stage 4: build_package ------------------------------------------------
banner 4 "build_package — Drive-ready review package (auto_publish: false)"
"$PY" engine/scripts/build_package.py "$CAMPAIGN" packages --work-root "$(dirname "$CADENCE_DIR")/.." \
  || fail "build_package on $CAMPAIGN" "package assembly failed — check adapter paths in the campaign JSON, then re-run ./run.sh $RELEASE_FOLDER"

CAMP_ID="$("$PY" -c "import json,sys;print(json.load(open(sys.argv[1]))['id'])" "$CAMPAIGN")"
PKG="packages/$CAMP_ID"

echo ""
echo "=================================================================="
echo "== DONE — package: $PKG"
echo "== Record: $RECORD"
echo "== Reviewer review cards:"
echo "==   - this run:  $PKG/REVIEWER.md"
echo "==   - gates:     reviewer/claims-lock.md → reviewer/spot-check.md → reviewer/pack-approve.md"
echo "== Nothing publishes. Reviewer (human) is the gate."
echo "=================================================================="
