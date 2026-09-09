// Execute the bundled preparation Code node locally, without n8n or providers.
import {readFileSync, writeFileSync} from 'node:fs';
import * as crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {dirname, join} from 'node:path';
import vm from 'node:vm';

if (!process.argv[2]) throw new Error('Usage: node run.mjs INPUT.json [OUTPUT.json]');
const workflow = JSON.parse(readFileSync(join(dirname(fileURLToPath(import.meta.url)), 'workflow.json')));
const input = JSON.parse(readFileSync(process.argv[2]));
const code = workflow.nodes.find(node => node.type === 'n8n-nodes-base.code').parameters.jsCode;
const result = vm.runInNewContext('(function(){' + code + '\n})()', {
  $input: {all: () => [{json: input}]},
  require: name => {if (name !== 'crypto') throw new Error('Only crypto is available'); return crypto;},
}, {timeout: 2000})[0].json;
const encoded = JSON.stringify(result, null, 2) + '\n';
if (process.argv[3]) writeFileSync(process.argv[3], encoded); else process.stdout.write(encoded);
if (result.status !== 'ready_for_operator') process.exitCode = 2;
