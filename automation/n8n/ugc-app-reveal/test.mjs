import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname, join} from 'node:path';
import vm from 'node:vm';

const here = dirname(fileURLToPath(import.meta.url));
const workflow = JSON.parse(readFileSync(join(here, 'workflow.json'), 'utf8'));
const code = workflow.nodes.find(node => node.type === 'n8n-nodes-base.code').parameters.jsCode;
const example = JSON.parse(readFileSync(join(here, 'request.example.json'), 'utf8'));
const run = inputs => JSON.parse(JSON.stringify(vm.runInNewContext('(function(){' + code + '\n})()', {
  $input: {all: () => inputs.map(json => ({json}))},
}, {timeout: 1000})));
const alter = change => {const input = structuredClone(example); change(input); return input;};
let cases = 0;
function test(name, check) {check(); cases++; process.stdout.write('PASS ' + name + '\n');}

test('complete brief returns five unmodified prompts and full source text', () => {
  const result = run([example])[0].json;
  assert.equal(result.status, 'ready_for_operator');
  assert.equal(result.prompts.length, 5);
  assert.equal(result.bindings.story.text, example.bindings.story.text);
  assert.equal(result.run_context.request_id, example.request_id);
  for (const prompt of result.prompts) assert.ok(prompt.text.length > 100 && /^[a-f0-9]{64}$/.test(prompt.sha256));
});
test('no inputs returns a hold with no generated content', () => {
  const result = run([{}])[0].json;
  assert.equal(result.status, 'needs_inputs'); assert.equal(result.prompts, undefined);
});
test('missing source binding holds the request', () => {
  assert.ok(run([alter(x => delete x.bindings.source_facts)])[0].json.issues.includes('missing_or_invalid_binding_source_facts'));
});
test('invalid hashes and unsafe workspace paths hold the request', () => {
  const result = run([alter(x => {x.bindings.story.sha256 = 'approved'; x.bindings.story.uri = '../secrets';})])[0].json;
  assert.equal(result.status, 'needs_inputs'); assert.equal(result.prompts, undefined);
});
test('Social duration cap does not inherit the 60-second film allowance', () => {
  const result = run([alter(x => x.deliverable_scope = 'campaign_social_video')])[0].json;
  assert.ok(result.issues.includes('duration_must_be_within_30_seconds'));
});
test('720p output request is held, without claiming upscaling occurred', () => {
  assert.equal(run([alter(x => {x.format.width = 1280; x.format.height = 720;})])[0].json.status, 'needs_inputs');
});
test('caller approvals cannot authorize execution or publication', () => {
  const result = run([alter(x => {x.approved = true; x.execution_authorized = true; x.publishing_authorized = true;})])[0].json;
  assert.equal(result.execution_authorized, false); assert.equal(result.publishing_authorized, false); assert.equal(result.approved, undefined);
});
test('credentials are held and their values are omitted from outputs', () => {
  const result = run([alter(x => x.private_key = 'TEST-SECRET-NOT-A-REAL-KEY')])[0].json;
  assert.equal(result.status, 'needs_inputs'); assert.ok(!JSON.stringify(result).includes('TEST-SECRET'));
});
test('multiple requests retain distinct product and source bindings', () => {
  const second = alter(x => {x.request_id = 'second-request'; x.product.name = 'Second product'; x.bindings.story.text = 'Second story';});
  const results = run([example, second]);
  assert.equal(results[0].json.product.name, example.product.name);
  assert.equal(results[1].json.bindings.story.text, 'Second story');
  assert.deepEqual(results.map(x => x.pairedItem.item), [0, 1]);
});
test('body-wrapped input works and empty batches do not invent work', () => {
  assert.equal(run([{body: example}])[0].json.status, 'ready_for_operator'); assert.deepEqual(run([]), []);
});
test('non-string binding URI returns a hold instead of crashing', () => {
  assert.equal(run([alter(x => x.bindings.story.uri = 42)])[0].json.status, 'needs_inputs');
});
test('wrong recipe and unknown scopes are rejected', () => {
  const result = run([alter(x => {x.recipe_id = 'some-other-recipe'; x.deliverable_scope = 'auto-publish';})])[0].json;
  assert.equal(result.status, 'needs_inputs');
});
test('array hash values cannot pass string hash validation', () => {
  const result = run([alter(x => x.bindings.story.sha256 = [x.bindings.story.sha256])])[0].json;
  assert.ok(result.issues.includes('missing_or_invalid_binding_story'));
});
test('binding URI rejects unsupported schemes and absolute Windows paths', () => {
  for (const uri of ['javascript:alert(1)', 'C:\\private\\story.txt', 'http://example.com/story', '/tmp/story', 'release/../story', [], {}]) {
    assert.equal(run([alter(x => x.bindings.story.uri = uri)])[0].json.status, 'needs_inputs');
  }
});
test('long and malformed URLs cannot stall other requests', () => {
  const unusual = alter(x => x.product.url = 'https://' + 'a.'.repeat(27) + 'example.com:443');
  const malformed = alter(x => x.product.url = 'https://' + 'a.'.repeat(27) + 'example.com:bad');
  const results = run([example, unusual, malformed, example]);
  assert.deepEqual(results.map(x => x.json.status), ['ready_for_operator', 'ready_for_operator', 'needs_inputs', 'ready_for_operator']);
});
process.stdout.write(JSON.stringify({passed: cases, paid_calls: 0}) + '\n');
