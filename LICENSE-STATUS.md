# License status

**Status: MIT.** The full text is in [LICENSE](LICENSE).

Launch Factory is released under the MIT License: use it, fork it, modify it, ship it commercially. Keep the copyright notice, and understand it comes with no warranty.

`license_status` in manifests: `mit`.

## What the license does not cover

The MIT grant covers this repository's own code, prompts, schemas, and documentation. It does not extend to anything this repository does not own.

The Python validation tools use `jsonschema`; `pytest` runs their tests, as listed in
`requirements.txt`. The n8n preparation code runs in your own n8n installation, with
Node.js for its local tests. This repository doesn't vendor those runtimes or grant their
licenses.

Media providers, agent hosts, and optional rendering tools need your own installation,
account access, and applicable terms. Following the tool instructions and running a
successful local production doesn't transfer credentials, credits, or provider access to
you. Third-party reference packs and private production media aren't included in the
portable recipe.

Source material you feed in, and the assets a run produces from it, are yours, governed by
whatever terms already apply to that material. Launch Factory makes no claim on either.
