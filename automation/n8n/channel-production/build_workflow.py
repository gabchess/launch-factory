#!/usr/bin/env python3
"""Build the inactive four-channel preparation workflow; no API calls."""
import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PROMPTS = {'blog': 'blog', 'email_segments': 'email', 'changelog': 'changelog', 'in_app_popup': 'popup'}


def build():
    registry = json.loads((ROOT / 'engine/specialists/registry.json').read_text())
    lanes = {}
    for deliverable, prompt in PROMPTS.items():
        route = registry['routes'][deliverable]
        role = registry['roles'][route['role']]
        lanes[deliverable] = {**route, 'skill_path': '.agents/skills/' + role['skill'] + '/SKILL.md',
                              'reference': role['reference'],
                              'prompt_path': 'engine/specialists/channel-production/prompts/' + prompt + '.md'}
    bundle = {'request_schema': json.loads((ROOT / 'engine/specialists/request.schema.json').read_text()), 'lanes': lanes}
    code = (HERE / 'prepare.js').read_text().replace('/* CHANNEL_BUNDLE */', json.dumps(bundle, separators=(',', ':')))
    return {'name': 'Launch Factory | Four Channels | Prepare', 'active': False,
            'nodes': [
                {'id': 'channel-input', 'name': 'Receive channel batch', 'type': 'n8n-nodes-base.executeWorkflowTrigger',
                 'typeVersion': 1.2, 'position': [0, 0], 'parameters': {'inputSource': 'passthrough'}},
                {'id': 'channel-prepare', 'name': 'Prepare channel work packets', 'type': 'n8n-nodes-base.code',
                 'typeVersion': 2, 'position': [300, 0], 'parameters': {'mode': 'runOnceForAllItems', 'language': 'javaScript', 'jsCode': code}},
                {'id': 'channel-boundary', 'name': 'Preparation boundary', 'type': 'n8n-nodes-base.stickyNote',
                 'typeVersion': 1, 'position': [0, 220], 'parameters': {'width': 620, 'height': 250,
                    'content': 'FOUR CHANNELS / PREPARATION ONLY\n\nBlog, five email segments, changelog, popup.\nUse load_requests.py on the release workspace first. Code requires the built-in crypto module.\nReturn ready_for_operator or needs_inputs. Draft roles, provider adapters and the durable human decision store are not wired here.\nConsolidated review follows actual session authority. No automatic publishing or paid retries.'}},
            ],
            'connections': {'Receive channel batch': {'main': [[{'node': 'Prepare channel work packets', 'type': 'main', 'index': 0}]]}},
            'settings': {'executionOrder': 'v1'}, 'pinData': {}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    path = HERE / 'workflow.json'
    content = json.dumps(build(), indent=2, ensure_ascii=False) + '\n'
    if args.check:
        if not path.exists() or path.read_text() != content:
            raise SystemExit('workflow.json differs; rebuild it')
        print('workflow.json matches the source, registry and schema')
    else:
        path.write_text(content)
        print('Built inactive workflow.json')
