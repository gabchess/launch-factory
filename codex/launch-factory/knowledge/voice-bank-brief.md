# Voice Bank brief: how voice checks work

Voice checks run against:

- **Canonical brief:** `voice-bank/tone-and-style-brief.md`, derived from your
  own corpus, ending in a numbered "Voice rules for adapters" section.
- **Corpus:** `voice-bank/corpus/`, the product's own writing you collected
  yourself, each item with a source and a retrieval date. See
  `voice-bank/README.md` for how to build it.
- **Gaps:** `voice-bank/gaps.md`: what is missing versus a real brand guide.
  Ask the brand owner for what closes the gap; do not invent.
- **Provenance:** `voice-bank/provenance.md`: how the corpus was collected,
  and the guarantees that collection meets (public sources, no fabricated
  quotes, no login circumvention).

Rules while the bank is interim (before a canonical brand guide supersedes
it):

1. Every voice judgment cites a corpus item or a brief rule by number.
2. The brief is a warning system, not a truth oracle: it flags drift; the
   human reviewer decides.
3. When a canonical brand guide arrives, it supersedes this brief: keep the
   corpus, re-derive the brief against the real guide, and bump its version.
