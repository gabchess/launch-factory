# ADR 0019: a hosted operator interface

Date: 2026-09-08. Status: planned; deferred from v2. [ADR 0020](0020-v2-local-package-builder.md) describes the shipped local workflow.

A future hosted interface should let an operator provide release sources, inspect drafts, request changes and download a package. Setup needs clear guidance for missing credentials. Progress and pending human decisions must survive a reload.

Before expanding the interface, verify one path from intake through a background job and its callback to a stored review decision. Long provider jobs need a worker outside the browser request. Each account also needs bounded costs and retries.

This remains future work. The local builder and optional n8n preparation workflows do not supply hosted authentication, provider workers or durable approval storage.
