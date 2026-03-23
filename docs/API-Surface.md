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
- `libs.templates.schema`

These modules define the active plugin runtime contracts that shape daemon
startup, configuration loading, messaging, and plugin execution.

## Internal API

The internal documentation surface currently includes:

- `libs.db_models.base`
- `libs.db_models.connectors`
- `libs.db_models.lms.*`
- `libs.db_models.mlms.*`

These modules define persistence mapping, SQLAlchemy relationships, and
database integration details. They are documented for maintainers, but they are
not considered the stable application API.

## Practical Rule

When adding or updating generated API docs:

1. Include runtime plugins and shared runtime helpers in the Sphinx autosummary tree.
2. Keep ORM models documented with source docstrings.
3. Do not promote ORM models to the public API reference unless the project
   explicitly decides to expose a supported data-access contract.
