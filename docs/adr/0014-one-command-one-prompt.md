# ADR 0014: command-line and agent entry points

Date: 2026-09-07. Status: historical; current commands are in the root README.

## Decision

Provide a command-line entry point and a host-agent skill for the same release workflow. Both need source intake, claim review and a package the operator can inspect.

## Consequences

A host without the required runtime can prepare a draft, but must state which steps remain unexecuted. Installation in a host does not establish that a complete run passed there. V2 uses `launch_factory.py` for local builds and verification.
