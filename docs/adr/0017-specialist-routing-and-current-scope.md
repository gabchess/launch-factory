# ADR 0017: specialist routing

Date: 2026-09-08. Status: implemented. [ADR 0020](0020-v2-local-package-builder.md) defines the current local builder.

## Decision

Use a shared registry, role references, packet schemas and an offline routing helper. Generated project entry points expose the same roles to supported coding agents. The operator selects a role and follows its protocol, with an inline fallback when delegation is unavailable.

Specialists return drafts and review findings. A named human decides whether to accept the exact artifact. Review subjects bind its version, hash and relevant inputs. The helper compares these bindings; it does not authenticate or store human decisions.

## Revisions

A revision affects the changed asset and its dependencies. Campaign dates remain separate from final artifact bindings, so changing a date need not regenerate unchanged copy. Missing tools and media checks remain visible in the result.

## Scope

This layer supplies reusable routing and preparation. Each run needs its own sources and human decisions. Provider execution, durable approval storage and publishing require separate implementations.
