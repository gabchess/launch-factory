import assert from 'node:assert/strict';
import {readFileSync, existsSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
import {dirname, resolve} from 'node:path';
import vm from 'node:vm';

const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(here, '../../..');
const registry = JSON.parse(readFileSync(resolve(root, 'engine/specialists/registry.json')));
const requestSchema = JSON.parse(readFileSync(resolve(root, 'engine/specialists/request.schema.json')));
const lanes = ['blog', 'email_segments', 'changelog', 'in_app_popup'];
const prompts = {blog: 'blog', email_segments: 'email', changelog: 'changelog', in_app_popup: 'popup'};
const bundle = {request_schema: requestSchema, lanes: Object.fromEntries(lanes.map(key => [key, {
  ...registry.routes[key], skill_path: '.agents/skills/' + registry.roles[registry.routes[key].role].skill + '/SKILL.md',
  reference: registry.roles[registry.routes[key].role].reference,
  prompt_path: 'engine/specialists/channel-production/prompts/' + prompts[key] + '.md',
}]))};
const hash = s => createHash('sha256').update(s).digest('hex');
const code = readFileSync(resolve(here, 'prepare.js'), 'utf8').replace('/* CHANNEL_BUNDLE */', JSON.stringify(bundle));
const runCode = (source, inputs, crypto = true) => JSON.parse(JSON.stringify(vm.runInNewContext('(function(){' + source + '\n})()', {
  $input: {all: () => inputs.map(json => ({json}))},
  require: crypto ? createRequire(import.meta.url) : () => {throw new Error('not allowed');},
}, {timeout: 1500})));
const run = (input, crypto = true) => runCode(code, [input], crypto)[0].json;
const fact = '😀 Offers are a preview.';
const voice = 'Use short useful sentences.';
function fixture() {
  const sources = [{id: 'fact', path: 'sources/fact.txt', sha256: hash(fact), product_id: 'fixture', kind: 'fact'},
    {id: 'voice', path: 'voice/sample.txt', sha256: hash(voice), product_id: 'fixture', kind: 'voice'}];
  return {schema_version: 'channel-production-preparation-request/v1', batch_id: 'batch1', review_mode: 'consolidated_end',
    email_segments: ['lead_smb', 'lead_agency', 'lead_reseller_affiliate', 'customer_smb', 'customer_agency'], revisions: [],
    source_texts: [{path: 'sources/fact.txt', text: fact}, {path: 'voice/sample.txt', text: voice}],
    requests: lanes.map(deliverable => ({schema_version: 'specialist-request/v1', task_id: 'task-' + deliverable,
      campaign_id: 'campaign1', product_id: 'fixture', source_revision: 'r1', deliverable, stage: 'draft',
      voice_profile: 'plain', requested_reviewer: 'gabe', sources: structuredClone(sources),
      claims: [{id: 'c1', source_id: 'fact', quote: 'Offers', start: 2, end: 8}], voice_source_ids: ['voice'], artifacts: [], changed_ids: []}))};
}
const change = fn => {const x = fixture(); fn(x); return x;};
let count = 0;
function test(name, fn) {fn(); count++; process.stdout.write('PASS ' + name + '\n');}
function held(input, issue) {const r = run(input); assert.equal(r.status, 'needs_inputs'); assert.equal(r.work_packets, undefined); if (issue) assert.ok(r.issues.some(s => s.includes(issue)), JSON.stringify(r.issues));}

test('four complete requests become four concrete role assignments for one review', () => {
  const r = run(fixture()); assert.equal(r.status, 'ready_for_operator');
  assert.deepEqual(r.work_packets.map(p => p.assigned_role), ['blog_editor', 'email_editor', 'changelog_editor', 'popup_designer']);
  assert.equal(r.review.mode, 'consolidated_end'); assert.equal(r.review.status, 'pending_actual_artifacts_and_human');
  assert.equal(r.work_packets[0].source_texts[0].text, fact);
  assert.equal(r.work_packets[1].required_artifact_fields.segments.length, 5);
  assert.equal(r.work_packets[3].required_artifact_fields.graphic.required, true);
});
test('missing or repeated lanes hold the batch', () => {
  held(change(x => x.requests.pop()));
  held(change(x => x.requests[3] = structuredClone(x.requests[0])));
});
test('mixed campaign, product or source revision cannot combine', () => {
  for (const key of ['campaign_id', 'product_id', 'source_revision']) held(change(x => x.requests[1][key] = 'other'));
});
test('email segments must be the five exact contract IDs', () => {
  held(change(x => x.email_segments[2] = 'reseller'));
  held(change(x => x.email_segments.push('lead_smb')));
});
test('source bytes and Unicode character spans are checked', () => {
  held(change(x => x.source_texts[0].text += ' Changed'), 'hash');
  held(change(x => x.requests[0].claims[0].end = 100), 'span');
  held(change(x => x.requests[0].claims[0].quote = 'Current'), 'span');
});
test('voice files cannot supply product claims', () => {
  held(change(x => x.requests[0].claims[0].source_id = 'voice'), 'fact');
  held(change(x => x.requests[0].voice_source_ids = ['fact']), 'voice');
});
test('empty claims and voice selection hold drafting', () => {
  held(change(x => x.requests[0].claims = []));
  held(change(x => x.requests[0].voice_source_ids = []));
});
test('a source ID or path cannot silently change between lanes', () => {
  held(change(x => x.requests[1].sources[0].path = 'other.txt'));
});
test('unsafe paths, schema additions and duplicate task IDs are refused', () => {
  held(change(x => x.requests[0].sources[0].path = '../outside.txt'));
  held(change(x => x.requests[0].approved = true));
  held(change(x => x.requests[1].task_id = x.requests[0].task_id));
});
test('malformed source and revision collections return a hold without crashing', () => {
  held(change(x => x.source_texts = {})); held(change(x => x.revisions = {}));
});
test('missing crypto is an explicit hold with no fake verification', () => {
  const r = run(fixture(), false); assert.equal(r.status, 'needs_inputs'); assert.ok(r.issues.includes('crypto_module_unavailable'));
});
test('caller authority flags and replayed preparation grant no approval', () => {
  const x = change(x => {x.execution_authorized = true; x.approved = true;});
  for (let n = 0; n < 2; n++) {const r = run(x); assert.equal(r.execution_authorized, false); assert.equal(r.human_approval_granted, false); assert.equal(r.publishing_authorized, false);}
});
test('secret-valued and non-finite inputs are held without echo', () => {
  const x = change(x => x.api_key = 'fixture-secret');
  assert.ok(!JSON.stringify(run(x)).includes('fixture-secret'));
  held(change(x => x.requests[0].claims[0].end = Infinity));
});
function revised(attempt = 1) {
  const x = fixture();
  const artifact = {id: 'article', path: 'drafts/article.md', sha256: hash('prior draft'), version: 1, product_id: 'fixture', depends_on: ['fact']};
  x.requests[0].artifacts = [artifact]; x.requests[0].target_asset_id = 'article'; x.requests[0].changed_ids = ['article']; x.requests[0].stage = 'revise';
  x.revisions = [{asset_id: 'article', attempt, feedback: 'Shorten the introduction.', reviewed_version: 1, reviewed_sha256: artifact.sha256}];
  return x;
}
test('one changed article prepares only its revision and keeps other lanes', () => {
  const r = run(revised()); assert.equal(r.status, 'ready_for_operator'); assert.deepEqual(r.work_packets.map(p => p.deliverable), ['blog']);
  assert.deepEqual(r.preserved_deliverables, ['email_segments', 'changelog', 'in_app_popup']);
  assert.equal(r.work_packets[0].revision.attempt, 1);
});
test('two revisions are allowed and the third requires a human stop', () => {
  assert.equal(run(revised(2)).status, 'ready_for_operator'); held(revised(3), 'revision');
  held(revised(0), 'revision');
});
test('stale feedback hash or version cannot request a new revision', () => {
  const x = revised(); x.revisions[0].reviewed_sha256 = hash('different draft'); held(x, 'stale');
  const y = revised(); y.revisions[0].reviewed_version = 2; held(y, 'stale');
});
test('dependency cycles and uncounted affected revision targets hold', () => {
  const x = revised(); x.requests[0].artifacts[0].depends_on = ['article']; held(x, 'cycle');
  const y = revised(); y.revisions = []; held(y, 'revision');
});
test('unrouted affected artifacts and dependencies absent from a packet hold', () => {
  const x = revised(); x.requests[0].artifacts.push({id: 'other-output', path: 'drafts/other.md', sha256: hash('other'), version: 1, product_id: 'fixture', depends_on: ['article']}); held(x, 'unrouted');
  const y = revised(); y.requests[0].artifacts[0].depends_on = ['elsewhere']; y.requests[1].sources.push({...y.requests[1].sources[0], id: 'elsewhere'}); held(y, 'packet_dependency');
});
test('prototype-named request fields cannot bypass the closed schema', () => {
  for (const name of ['constructor', 'toString', '__proto__']) {
    held(change(x => Object.defineProperty(x.requests[0], name, {value: {unexpected: true}, enumerable: true})), 'unknown_field');
  }
});
test('existing changed artifacts cannot masquerade as initial drafts', () => {
  const x = revised(); x.requests[0].stage = 'draft'; x.revisions = []; held(x, 'revision');
});
test('revision records cannot echo caller approval or execution fields', () => {
  const x = revised(); x.revisions[0].execution_authorized = true; x.revisions[0].human_approval_granted = true;
  const r = run(x); assert.equal(r.status, 'needs_inputs'); assert.equal(r.work_packets, undefined);
  assert.equal(r.execution_authorized, false); assert.equal(r.human_approval_granted, false);
});
test('body input and batch pairing retain isolation', () => {
  const r = runCode(code, [{body: fixture()}, {}]); assert.equal(r[0].json.status, 'ready_for_operator'); assert.equal(r[1].json.status, 'needs_inputs');
  assert.deepEqual(r.map(x => x.pairedItem.item), [0, 1]); assert.deepEqual(runCode(code, []), []);
});
if (existsSync(resolve(here, 'workflow.json'))) test('built inactive workflow executes the real preparation code', () => {
  const wf = JSON.parse(readFileSync(resolve(here, 'workflow.json')));
  assert.equal(wf.active, false); assert.equal(wf.nodes.filter(n => n.type === 'n8n-nodes-base.code').length, 1);
  assert.deepEqual(runCode(wf.nodes.find(n => n.type === 'n8n-nodes-base.code').parameters.jsCode, [fixture()])[0].json, run(fixture()));
});
process.stdout.write(JSON.stringify({passed: count, paid_calls: 0}) + '\n');
