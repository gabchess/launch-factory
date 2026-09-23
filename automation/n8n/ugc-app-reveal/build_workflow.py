#!/usr/bin/env python3
"""Build a portable n8n preparation workflow from the canonical video recipe."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RECIPE = ROOT / 'engine/specialists/video-production/recipes/ugc-app-reveal'


def encode(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'))


def build():
    recipe = json.loads((RECIPE / 'recipe.json').read_text())
    prompts = []
    for prompt in recipe['prompts']:
        path = (RECIPE / prompt['path']).resolve()
        path.relative_to(RECIPE.resolve())
        content = path.read_text()
        prompts.append({**prompt, 'text': content, 'sha256': hashlib.sha256(content.encode()).hexdigest()})
    payload = {'recipe': recipe, 'prompts': prompts}
    bundle = {**payload, 'sha256': hashlib.sha256(encode(payload).encode()).hexdigest()}
    code = (HERE / 'prepare.js').read_text().replace('/* RECIPE_BUNDLE */', encode(bundle))
    nodes = [
        {'id': 'receive-video-request', 'name': 'Receive video request', 'type': 'n8n-nodes-base.executeWorkflowTrigger', 'typeVersion': 1.2, 'position': [0, 0], 'parameters': {'inputSource': 'passthrough'}},
        {'id': 'prepare-video-work-packet', 'name': 'Prepare video work packet', 'type': 'n8n-nodes-base.code', 'typeVersion': 2, 'position': [300, 0], 'parameters': {'mode': 'runOnceForAllItems', 'language': 'javaScript', 'jsCode': code}},
    ]
    note = ('UGC APP REVEAL 1.0.0\n\nPreparation subworkflow. Call with the request shape in request.example.json. '
            'Returns five prompts, source bindings and review requirements. Invalid inputs return needs_inputs. '
            'No credentials or paid calls. ready_for_operator is not render or approval authority. '
            'The calling app must authenticate the human and dispatch a separately configured provider worker.')
    sample = {'status': 'needs_inputs', 'execution_authorized': False, 'publishing_authorized': False}
    lines = []
    for index, spec in enumerate(nodes):
        factory = 'trigger' if index == 0 else 'node'
        config = {'name': spec['name'], 'parameters': spec['parameters'], 'position': spec['position']}
        lines.append('const step' + str(index) + ' = ' + factory + '(' + encode({'type': spec['type'], 'version': spec['typeVersion'], 'config': config, 'output': [{}] if index == 0 else [sample]}) + ');')
    lines.append('const guide = sticky(' + encode(note) + ', [], {width: 640, height: 280, position: [0, 240]});')
    lines.append("export default workflow('lf-ugc-app-reveal-prepare', 'Launch Factory | UGC App Reveal | Prepare').add(step0).to(step1).add(guide);")
    (HERE / 'workflow.sdk.js').write_text('\n'.join(lines) + '\n')
    portable = {'name': 'Launch Factory | UGC App Reveal | Prepare', 'active': False,
                'nodes': nodes + [{'id': 'guide', 'name': 'Integration guide', 'type': 'n8n-nodes-base.stickyNote', 'typeVersion': 1, 'position': [0, 240], 'parameters': {'content': note, 'width': 640, 'height': 280}}],
                'connections': {'Receive video request': {'main': [[{'node': 'Prepare video work packet', 'type': 'main', 'index': 0}]]}},
                'settings': {'executionOrder': 'v1', 'callerPolicy': 'workflowsFromSameOwner', 'saveDataSuccessExecution': 'none', 'saveDataErrorExecution': 'none', 'saveManualExecutions': False},
                'pinData': {}}
    (HERE / 'workflow.json').write_text(json.dumps(portable, indent=2, ensure_ascii=False) + '\n')
    print(encode({'recipe': recipe['recipe_id'], 'version': recipe['version'], 'prompts': len(prompts), 'bundle_sha256': bundle['sha256'], 'nodes': len(portable['nodes'])}))


if __name__ == '__main__':
    build()
