"""Uses real temporary files and the existing router; no model/provider calls."""
import hashlib
import json
from pathlib import Path
import tempfile
import subprocess
import sys
import unittest

from load_requests import load_batch

LANES = ['blog', 'email_segments', 'changelog', 'in_app_popup']


class LoaderChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)
        self.fact = 'Offers are a preview.'
        self.voice = 'Use useful words.'
        (self.workspace / 'fact.txt').write_text(self.fact)
        (self.workspace / 'voice.txt').write_text(self.voice)
        sources = [dict(id='fact', path='fact.txt', sha256=hashlib.sha256(self.fact.encode()).hexdigest(), product_id='fixture', kind='fact'),
                   dict(id='voice', path='voice.txt', sha256=hashlib.sha256(self.voice.encode()).hexdigest(), product_id='fixture', kind='voice')]
        self.paths = []
        for lane in LANES:
            packet = dict(schema_version='specialist-request/v1', task_id=lane, campaign_id='fixture-campaign', product_id='fixture',
                          source_revision='fixture-r1', deliverable=lane, stage='draft', voice_profile='plain', requested_reviewer='gabe',
                          sources=sources, claims=[dict(id='c1', source_id='fact', quote=self.fact, start=0, end=len(self.fact))],
                          voice_source_ids=['voice'], artifacts=[])
            path = self.workspace / (lane + '.json')
            path.write_text(json.dumps(packet))
            self.paths.append(path)

    def test_real_workspace_produces_complete_inline_sources(self):
        batch = load_batch(self.workspace, self.paths, 'fixture-batch')
        self.assertIsInstance(batch, dict)
        self.assertEqual(len(batch['requests']), 4)
        self.assertEqual(batch['source_texts'], [{'path': 'fact.txt', 'text': self.fact}, {'path': 'voice.txt', 'text': self.voice}])
        self.assertEqual(batch['local_validation']['status'], 'passed_existing_route_validator')
        self.assertFalse(batch['local_validation']['human_approval_granted'])

    def test_changed_source_bytes_fail_existing_hash_check(self):
        (self.workspace / 'fact.txt').write_text('Other bytes')
        with self.assertRaisesRegex(ValueError, 'SHA-256'):
            load_batch(self.workspace, self.paths, 'fixture-batch')

    def test_exactly_four_lanes_are_required(self):
        with self.assertRaisesRegex(ValueError, 'four'):
            load_batch(self.workspace, self.paths[:3], 'fixture-batch')

    def test_invalid_schema_cli_returns_a_refused_envelope(self):
        packet = json.loads(self.paths[0].read_text()); packet['approved'] = True
        self.paths[0].write_text(json.dumps(packet))
        result = subprocess.run([sys.executable, str(Path(__file__).with_name('load_requests.py')), '--workspace', str(self.workspace), '--batch-id', 'fixture-batch', '--requests', *map(str, self.paths)], text=True, capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)['status'], 'refused')
        self.assertNotIn('Traceback', result.stderr)

    def test_missing_claims_returns_hold_without_fake_ready(self):
        packet = json.loads(self.paths[0].read_text()); packet['claims'] = []
        self.paths[0].write_text(json.dumps(packet))
        with self.assertRaisesRegex(ValueError, 'held'):
            load_batch(self.workspace, self.paths, 'fixture-batch')


if __name__ == '__main__':
    unittest.main()
