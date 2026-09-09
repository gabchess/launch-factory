# Voice Bank

The Voice Bank is how Launch Factory learns to write like your brand instead of
like a generic model. It has two parts:

- **`corpus/`** (you build this): a small set of your own published writing,
  each item tagged with its source and the date you collected it.
- **`tone-and-style-brief.md`** (you derive this from the corpus): a short set
  of checkable rules that every draft gets compared against.

`provenance.md` records how you collected the corpus and what guarantees that
collection meets. `gaps.md` records what you could not collect and what would
close the gap. Neither file ships with real content in this template; each
carries instructions for what to put there.

## Why this exists

A writer role with no brand reference defaults to marketing filler: hype
adjectives, empty transitions, listicle rhythm. The Voice Bank gives every
Launch Factory writer seat something concrete to check a draft against, and
gives the human reviewer a paper trail: every voice judgment should cite a
corpus item or a brief rule by number, not a vibe.

## Build your own voice bank

1. **Collect 15 to 30 items of your own writing**, across the channels you
   actually publish in. Aim for range, not volume: one email is not a corpus,
   it is one data point. A workable starting spread:
   - Website copy (homepage, one or two product pages)
   - A handful of blog posts, spanning at least two authors or bylines if you
     have more than one
   - Social posts (whichever platforms you actually run)
   - At least one email (a newsletter, an announcement, a transactional email)
   - Anything with a distinct register worth capturing separately: a founder's
     LinkedIn voice, a support macro, a changelog
2. **Save each item as its own file** in `corpus/`, numbered
   (`01-...`, `02-...`), with the verbatim excerpt plus a short front-matter
   block: source URL or origin, retrieval date, author or voice attribution
   (company-voiced vs. an individual's byline), and any confidence flag
   (`[sic]`, `[LOW CONFIDENCE]`, `[...]` for elisions).
3. **Record how you collected it** in `provenance.md`: method, what counts as
   in-bounds (public sources, an internal document someone explicitly shared
   with you), what you refused to do (no logins, no scraping past a
   paywall), and how you handle the one non-public item if you use one (for
   example, an internal email someone forwarded you as a seed: paraphrase it
   in the public-facing copy of the repo and say so, rather than shipping
   someone's private writing verbatim).
4. **Log what you could not get** in `gaps.md`: channels you could not reach,
   registers that are underrepresented (one email is not enough to derive an
   email rule from), and what a real brand guide would add that inference
   from public copy cannot (approved vocabulary lists, audience personas,
   an official claims list). This file is the honest difference between what
   you built and a real brand guide.
5. **Derive `tone-and-style-brief.md`** only from the corpus you just built.
   Every rule cites the corpus item(s) it came from. See that file for the
   sections a usable brief needs.

## Guardrails, whichever product you run this for

- **Public sources by default.** If you include one non-public seed (an
  internal email, a Slack message, an unpublished draft) someone gave you
  explicitly for this purpose, label it as the exception it is, and do not
  reproduce private material verbatim in a public repository.
- **No fabricated quotes.** Anything you cannot verify as real and current
  gets excluded and logged in `gaps.md`, never guessed.
- **No personal data beyond what the person made public themselves** (a
  professional bio line, a byline). Never scrape private profile data.
- **The corpus is evidence, not the product's whole voice.** It is what you
  could collect within these guardrails: label it interim if a canonical
  brand guide exists and has not been folded in yet.

## How the engine uses this

Writer seats check drafts against `tone-and-style-brief.md`'s rules and cite
corpus item numbers for specific phrasing choices. The brief flags drift; it
does not replace human judgment. The reviewer role defined in `reviewer/` is
always the final voice arbiter, exactly as it is the final arbiter on claims.
When a canonical brand guide exists, it supersedes the derived brief: keep the
corpus, re-derive the brief against the real guide, and bump its version.
