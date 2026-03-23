# API Surface Policy

**Purpose:**
This document defines which parts of the current codebase are treated as public
API documentation targets and which parts are treated as internal
implementation details.

## Public API

The public documentation surface currently includes:

- `aasd.py`
- `server.daemon`
- `libs.app`
- `libs.conf`
- `libs.base.classes`
- `libs.com.message`
- `libs.tools.datetool`
- `libs.tools.icmp`
- `libs.plugins.runtime`
- `libs.plugins.loader`
- `libs.plugins.config`
- `libs.plugins.keys`
- `libs.plugins.service`
- `libs.templates.schema`

These modules define the active plugin runtime contracts that shape daemon
startup, configuration loading, messaging, and plugin execution.

## Practical Rule

When adding or updating generated API docs:

1. Include runtime plugins and shared runtime helpers in the Sphinx autosummary tree.
2. Keep archived implementation details outside the active API reference.
3. Do not promote archived ORM models to the public API reference unless the
   project explicitly decides to expose a supported data-access contract.
