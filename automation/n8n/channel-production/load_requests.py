#!/usr/bin/env python3
"""Load four existing requests through the canonical workspace validator."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import jsonschema

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'engine'))
from scripts.specialist_route import REGISTRY, route_request

LANES = ['blog', 'email_segments', 'changelog', 'in_app_popup']


def read_json(path):
    def invalid_constant(value):
        raise ValueError('Non-finite JSON constant: ' + value)
    return json.loads(Path(path).read_text(), parse_constant=invalid_constant)


def load_batch(workspace, request_paths, batch_id, revisions=None):
    workspace = Path(workspace).resolve()
    requests = [read_json(path) for path in request_paths]
    if len(requests) != 4 or any(not isinstance(r, dict) or not isinstance(r.get('deliverable'), str) for r in requests) or sorted(r.get('deliverable', '') for r in requests) != sorted(LANES):
        raise ValueError('Supply exactly four distinct channel requests')
    requests.sort(key=lambda r: LANES.index(r['deliverable']))
    files, checks = {}, []
    for request in requests:
        projection = route_request(request, workspace)
        if projection['status'] != 'ready_for_protocol':
            raise ValueError(request['deliverable'] + ' held: ' + '; '.join(projection['holds']))
        for source in request['sources']:
            data = (workspace / source['path']).read_bytes()
            if hashlib.sha256(data).hexdigest() != source['sha256']:
                raise ValueError('SHA-256 changed while loading: ' + source['id'])
            content = data.decode('utf-8')
            if source['path'] in files and files[source['path']] != content:
                raise ValueError('Inconsistent source path')
            files[source['path']] = content
        checks.append({'task_id': request['task_id'], 'deliverable': request['deliverable'],
                       'role': projection['specialists'][0]['role'], 'context_digest': projection['context_digest']})
    for key in ['campaign_id', 'product_id', 'source_revision', 'requested_reviewer']:
        if len({r.get(key) for r in requests}) != 1:
            raise ValueError('Mixed ' + key)
    return {'schema_version': 'channel-production-preparation-request/v1', 'batch_id': batch_id,
            'review_mode': 'consolidated_end', 'requests': requests,
            'source_texts': [{'path': path, 'text': content} for path, content in sorted(files.items())],
            'email_segments': REGISTRY['routes']['email_segments']['segments'], 'revisions': revisions or [],
            'local_validation': {'status': 'passed_existing_route_validator', 'checks': checks,
                                 'human_approval_granted': False, 'authentication_verified': False}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', required=True, type=Path)
    parser.add_argument('--requests', required=True, nargs=4, type=Path)
    parser.add_argument('--batch-id', required=True)
    parser.add_argument('--revisions', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        result = load_batch(args.workspace, args.requests, args.batch_id,
                            read_json(args.revisions) if args.revisions else None)
    except (ValueError, OSError, UnicodeError, jsonschema.ValidationError) as exc:
        print(json.dumps({'status': 'refused', 'error': str(exc).split('\n')[0], 'human_approval_granted': False}))
        return 2
    encoded = json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + '\n'
    if args.output:
        args.output.write_text(encoded)
    else:
        print(encoded, end='')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
