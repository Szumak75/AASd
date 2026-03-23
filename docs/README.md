# Documentation Index

This directory contains project documentation, operational notes, and
API-oriented reference material for the active plugin-based runtime.

Deployment documentation assumes `requirements.txt` is the production runtime
installation source, while Poetry remains a development-only tool.

## Core Documents

- [Installation](./Installation.md) - environment setup and service preparation.
- [Modules](./Modules.md) - archived module model summary and migration context.
- [Flow](./Flow.md) - runtime flow and subsystem relationships.
- [Architecture](./Architecture.md) - project-wide structural analysis.
- [API](./API.md) - business logic API and runtime contracts.
- [API Surface](./API-Surface.md) - boundary between public runtime API and internal ORM layer.
- [Plugin API](./PluginAPI.md) - public contract for plugin implementations.
- [Plugin Migration](./PluginMigration.md) - migration plan and archive boundary.

## Operational Assets

- `runit/` - scripts for `runit`: <http://smarden.org/runit/>

## Build Documentation

Generate the HTML documentation with:

```bash
make docs
```

Output directory:

```text
docs/_build/html/
```
