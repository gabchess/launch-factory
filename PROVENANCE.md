# Provenance

Launch Factory was built around a common release task: turn feature notes, a walkthrough, and footage into a campaign for human review.

V2 adds a local renderer and this project's own release example. Its source notes describe implemented behavior; the silent walkthrough records those notes in a browser. No example approval is claimed.

The shared channel specialists and optional production recipes keep their source notes under `engine/specialists/`. Recipes provide reusable methods. The operator supplies media and provider credentials. Historical decisions remain in `docs/adr/`. [ADR 0020](docs/adr/0020-v2-local-package-builder.md) defines v2.

`engine/fixtures/specialist-demo` contains labelled synthetic routing inputs. Supply your own product's writing examples in `voice-bank/`. Voice samples do not establish product facts.
