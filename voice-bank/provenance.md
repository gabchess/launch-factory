# Provenance: Voice Bank

Fill this in once you build a real corpus in `corpus/`. It is the record of
how you collected the material the tone-and-style brief is derived from, so a
reviewer (or a future teammate) can check the brief's claims against a real
paper trail instead of taking them on faith.

## What to record

- **Collection date(s).** When each item was retrieved. Corpus items age; a
  three-year-old blog post is weaker evidence of current voice than last
  month's.
- **Collector.** Who or what gathered the corpus (a person, a research
  agent). Say so plainly if a tool did the collecting.
- **Method.** Exactly what you did: which pages you pulled from, which search
  queries you ran, whether you used a scraper or copied by hand. If you used
  an internal document someone shared with you (an email, a Slack export),
  name that explicitly and separately from public-web collection.
- **What you excluded and why.** Logins you did not use, paywalls you did not
  cross, platforms you decided not to attempt. This belongs here or in
  `gaps.md`; do not silently omit it.
- **Fabrication check.** A one-line statement that nothing in the corpus is
  an invented or paraphrased-as-verbatim quote, except where explicitly
  marked (see below).
- **Corpus inventory.** A table of item counts by source type and by voice
  attribution (company-voiced vs. a named individual's byline), so gaps in
  channel or author coverage are visible at a glance.

## Guarantees to state and hold to

- **Public sources only**, with the single exception of a non-public seed
  item explicitly provided to you for this purpose (label it as such, and
  paraphrase rather than reproduce it verbatim if the repository is public).
- **No private personal data**, beyond what a person has made public
  themselves.
- **No login or paywall circumvention.** Anything behind one goes in
  `gaps.md`, not in the corpus.
- **Excerpts are verbatim**, aside from the one labeled exception above.
  Where extraction introduces artifacts (broken line wraps, mangled
  characters), preserve the wording and mark artifacts `[sic]`; mark
  elisions in long items `[...]`.

## Worked example (fictional, for shape only)

The block below shows the shape of a filled-in provenance record for a
fictional B2B product, Quorum Desk. Replace it entirely with your own.

> **Collection date:** 2026-01-14 (all items retrieved that date).
> **Collector:** the product marketing lead, by hand.
> **Method:** direct copy from quorumdesk.example's public site (homepage,
> pricing page, three blog posts) and the last four posts on the company
> LinkedIn page. One internal onboarding email, shared by the founder as a
> voice seed, is included as item `01` and paraphrased in this repository.
> **Excluded:** the company's private Slack, its customer newsletter archive
> (no export available yet, see `gaps.md`), and any personal social accounts
> of employees.
> **Fabrication check:** no invented quotes; two items with truncated
> LinkedIn text are marked with trailing `[...]`.
>
> | source_type | count |
> |---|---|
> | website | 5 |
> | blog | 3 |
> | linkedin | 4 |
> | email | 1 (paraphrased seed) |

## Derivation chain

State plainly that `tone-and-style-brief.md` is derived only from the corpus
files, with every observation citing the corpus filename(s) it came from, and
that `gaps.md` records what could not be collected.
