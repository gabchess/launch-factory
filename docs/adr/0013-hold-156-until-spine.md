# ADR 0013: hold media outputs until rendering exists

Date: 2026-09-07. Status: superseded for the v2 local builder by [ADR 0020](0020-v2-local-package-builder.md).

## Decision

The early workflow returned explicit holds for social video, login animation and popup graphics while their renderers were unfinished. Written outputs could proceed with source evidence and human review.

## Current behavior

The v2 builder renders these media outputs from supplied inputs. Missing or invalid inputs still stop the build. A storyboard or fixture cannot establish that an output was rendered.
