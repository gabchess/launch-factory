#!/usr/bin/env python3
"""Offline one-rendition film packet checks. No provider calls or approval authority."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

import jsonschema

HERE = Path(__file__).resolve().parent
FINISHING = HERE.parent / "finishing"
if not FINISHING.is_dir():
    FINISHING = HERE.parent / "short-motion-finishing"
spec = importlib.util.spec_from_file_location("film_finishing_checks", FINISHING / "validate.py")
finishing = importlib.util.module_from_spec(spec)
spec.loader.exec_module(finishing)
read_json = finishing.read_json


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                    separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def span_matches(span, text):
    if not 0 <= span["start"] < span["end"] <= len(text) or text[span["start"]:span["end"]] != span["text"]:
        raise ValueError("Exact locked script span mismatch")


def bind_files(value, workspace):
    """Every typed file binding in this closed schema resolves inside one workspace."""
    if isinstance(value, dict):
        if {"path", "sha256", "version"} <= value.keys():
            finishing.verify_file(value, workspace)
        for child in value.values():
            bind_files(child, workspace)
    elif isinstance(value, list):
        for child in value:
            bind_files(child, workspace)


def decision_matches(record, subject):
    return record is not None and record["subject_digest"] == subject


def story_subject(job):
    return {"product_id": job["product_id"], "files": job["story"], "brief": job["brief"],
            "price_constraints": job["price_constraints"]}


def reference_subject(job):
    return {"references": job["references"], "continuity": {key: job["shot"][key] for key in (
        "speaker_id", "identity_reference_id", "voice_reference_id", "setting_reference_id",
        "wardrobe", "light_direction", "eyeline", "geography", "speech_input")}}


def validate(job, workspace):
    finishing.reject_nonfinite(job)
    jsonschema.Draft202012Validator(read_json(HERE / "production-job.schema.json")).validate(job)
    workspace = Path(workspace).resolve()
    bind_files(job, workspace)
    holds = []
    subjects = {"story": digest(story_subject(job)), "references": digest(reference_subject(job))}
    for label in ("story", "reference"):
        subject = subjects["references" if label == "reference" else "story"]
        record = job[label + "_decision"]
        if not decision_matches(record, subject) or record["decision"] != "accepted":
            holds.append(label + "_decision_missing_changed_or_requests_changes")
    refs = {ref["id"]: ref for ref in job["references"]}
    if len(refs) != len(job["references"]):
        raise ValueError("Duplicate reference ID")
    shot, brief = job["shot"], job["brief"]
    for role in ("identity", "voice", "setting"):
        ref = refs.get(shot[role + "_reference_id"])
        if not ref or ref["role"] != role:
            raise ValueError("Missing or wrong-role " + role + " reference")
    if brief["channel_max_duration_ms"] is not None and brief["film_duration_ms"] > brief["channel_max_duration_ms"]:
        raise ValueError("Film exceeds its explicit channel cap")
    if shot["edit_duration_ms"] > brief["film_duration_ms"] or shot["trim_start_ms"] + shot["edit_duration_ms"] > shot["generation_duration_ms"]:
        raise ValueError("Edit slot or trim exceeds its containing duration")
    if not 0 <= shot["action_start_ms"] < shot["action_end_ms"] <= shot["generation_duration_ms"]:
        raise ValueError("Action timing exceeds the source take")
    script = (workspace / job["story"]["script"]["path"]).read_text()
    if (shot["dialogue_source"] == "approved_audio") != (shot["speech_input"] is not None):
        raise ValueError("Only approved_audio requires an exact speech input file binding")
    if shot["dialogue_source"] == "silent":
        if shot["speech"] is not None or shot["audio"]["dialogue"]["mode"] != "off" or shot["audio"]["captions"]["mode"] != "off":
            raise ValueError("Silent actor take cannot contain speech or speech captions")
    else:
        if shot["speech"] is None or shot["audio"]["dialogue"]["mode"] != "on" or brief["audio"]["dialogue"]["mode"] != "on":
            raise ValueError("Spoken take requires exact dialogue and an explicit film dialogue plan")
        span_matches(shot["speech"], script)
    seen_prices = set()
    for price in job["price_constraints"]:
        if price["id"] in seen_prices:
            raise ValueError("Duplicate price constraint ID")
        seen_prices.add(price["id"])
        span_matches(price["source"], script)
        if price["spoken_form"] not in price["source"]["text"]:
            raise ValueError("Approved spoken price form is missing from its source span")
        if price["amount"] is None:
            holds.append("product_price_unknown:" + price["id"])
        else:
            compare = {"lt": lambda n: n < price["amount"], "lte": lambda n: n <= price["amount"], "eq": lambda n: n == price["amount"]}[price["comparator"]]
            if not all(compare(n) for n in price["illustrative_values"]):
                raise ValueError("Illustrative price violates its stated constraint")
    if job["route"]["capability_reference"] is None:
        holds.append("recipient_capability_unverified")
    budget, quote = job["budget"], job["quote"]
    if budget["film_spent"] > budget["film_ceiling"]:
        raise ValueError("Film budget already exceeded")
    if quote is None:
        holds.append("quote_unknown")
    else:
        if quote["producer"] != job["route"]["producer"] or quote["model"] != job["route"]["model"] or quote["duration_ms"] != shot["generation_duration_ms"]:
            raise ValueError("Quote producer, model or source duration mismatch")
        if quote["amount"] is None or quote["usd_estimate"] is None:
            holds.append("quote_cost_unknown")
        else:
            if quote["unit"] == "USD" and quote["amount"] != quote["usd_estimate"]:
                raise ValueError("USD quote and estimate differ")
            if quote["unit"] == "provider_credits" and quote["conversion_reference"] is None:
                holds.append("credit_to_usd_conversion_unverified")
            if quote["usd_estimate"] > budget["per_call_ceiling"] or quote["usd_estimate"] + budget["film_spent"] > budget["film_ceiling"]:
                raise ValueError("Quote exceeds the per-call or remaining film budget")
    previous = job["previous_rendition"]
    if job["purpose"] == "first_sample" and previous is not None:
        raise ValueError("First sample cannot inherit a previous rendition")
    if job["purpose"] != "first_sample":
        allowed = {"accepted", "request_changes"} if job["purpose"] == "revision" else {"accepted"}
        if previous is None or not decision_matches(previous["review"], digest(previous["subject"])) or previous["review"]["decision"] not in allowed:
            holds.append("previous_rendition_review_missing_changed_or_requests_changes")
    if job["purpose"] == "revision" and job["revision_scope"] is None:
        raise ValueError("Revision requires explicit feedback and changed scope")
    if job["purpose"] != "revision" and job["revision_scope"] is not None:
        raise ValueError("Revision scope belongs to a revision job")
    runtime, state = job["runtime"], job["state"]
    output = runtime["output"]
    if state == "prepared" and (runtime["job_id"] is not None or output is not None):
        raise ValueError("Prepared jobs cannot claim provider job or output IDs")
    if state in {"submitted", "returned"} and runtime["job_id"] is None:
        raise ValueError("Submitted job needs its returned provider job ID")
    if state != "returned" and output is not None:
        raise ValueError("Only a returned job can contain materialized output")
    subjects["job"] = digest({key: value for key, value in job.items() if key not in {"runtime", "state", "generation_review"}})
    subjects["rendition"] = None
    rendition_binding = None
    if state == "returned":
        if output is None:
            raise ValueError("Returned job needs materialized output")
        if output["producer"] != job["route"]["producer"] or output["model"] != job["route"]["model"]:
            raise ValueError("Actual output producer or model conflicts with the requested route")
        if output["version"] != output["media"]["version"]:
            raise ValueError("Output version conflicts with its media binding")
        manifest = read_json(workspace / output["manifest"]["path"])
        finishing.validate("manifest", manifest, workspace)
        asset = next((a for a in manifest["assets"] if a["id"] == output["asset_id"]), None)
        media = {key: output["media"][key] for key in ("path", "sha256")}
        if not asset or asset["status"] != "materialized" or asset["origin"] != "generated" or asset["media"] != media or asset["provider"] != output["producer"] or asset["job_id"] != runtime["job_id"] or asset["provider_receipt"] is None:
            raise ValueError("Output must match actual generated-media lineage and provider receipt")
        assets = {a["id"]: a for a in manifest["assets"]}
        ancestor_ids = set()

        def ancestors(asset_id):
            for parent in assets[asset_id]["input_asset_ids"]:
                if parent not in ancestor_ids:
                    ancestor_ids.add(parent)
                    ancestors(parent)

        ancestors(asset["id"])
        supplied = {(assets[aid]["media"]["path"], assets[aid]["media"]["sha256"])
                    for aid in ancestor_ids if assets[aid]["status"] == "materialized" and assets[aid]["media"]}
        inputs = [job["story"]["script"]] + [refs[shot[role + "_reference_id"]]["binding"] for role in ("identity", "voice", "setting")]
        if shot["speech_input"] is not None:
            inputs.append(shot["speech_input"])
        if not {(b["path"], b["sha256"]) for b in inputs} <= supplied:
            raise ValueError("Generated lineage omits the exact script or selected actor/voice/setting inputs")
        rendition_binding = {"job": subjects["job"], "job_id": runtime["job_id"], "output": output}
        subjects["rendition"] = digest(rendition_binding)
    review_matches = decision_matches(job["generation_review"], subjects["rendition"])
    if job["generation_review"] is not None and not review_matches:
        holds.append("rendition_review_subject_mismatch")
    next_gate = {"prepared": "operator_authority_check", "submitted": "reconcile_same_provider_job", "returned": "awaiting_human_review", "failed": "human_review_before_any_new_job"}[state]
    return {"schema_version": "production-projection/v1", "status": "held" if holds else "consistent_record",
            "workspace_root": str(workspace), "holds": holds, "subjects": subjects,
            "rendition_binding": rendition_binding, "next_gate": next_gate,
            "review_binding_matches": review_matches, "human_approval_granted": False,
            "execution_authorized": False, "authentication_verified": False, "event_applied": False,
            "scope": "Offline consistency only; receipts, latest human decisions, provider cost/access, rights, dialogue performance and media quality require actual verification"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--workspace", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = validate(read_json(args.input), args.workspace)
        print(json.dumps(result, indent=2, allow_nan=False))
        return 0 if result["status"] == "consistent_record" else 2
    except (ValueError, OSError, UnicodeError, jsonschema.ValidationError) as error:
        print(json.dumps({"status": "refused", "error": str(error).split("\n")[0], "human_approval_granted": False, "execution_authorized": False}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
