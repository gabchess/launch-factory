# maintainer-source

**Never ship as runtime.**

This tree is for maintainers editing canonical skill source, release notes, and packaging inputs. Customer installs use `codex/`, `claude/*.zip` (when present), `docs/`, and product-root custody files.

If you are packaging a customer release, exclude this directory from the runtime artifact.
