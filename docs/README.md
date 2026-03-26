# Documentation Index

This directory contains project documentation, operational notes, and
API-oriented reference material for the active plugin-based runtime.

Deployment documentation assumes `requirements.txt` is the production runtime
installation source, while Poetry remains a development-only tool.

## Core Documents

- [Installation](./Installation.md) - environment setup and service preparation.
- [Modules](./Modules.md) - archived module model summary and historical context.
- [Flow](./Flow.md) - runtime flow and subsystem relationships.
- [Architecture](./Architecture.md) - project-wide analysis of the active daemon and plugin runtime.
- [API](./API.md) - active daemon and plugin runtime contracts.
- [API Surface](./API-Surface.md) - boundary between public runtime API and internal ORM layer.
- [Plugin API](./PluginAPI.md) - public contract for plugin implementations.
- [Plugin Author Checklist](./PluginChecklist.md) - practical checklist for implementing new plugins.
- [Plugin Repository Model](./PluginRepositoryModel.md) - recommended organization of plugins as separate repositories mounted into `plugins_dir`.
- [Plugin Migration](./PluginMigration.md) - migration status and remaining cleanup work.

## Operational Assets

- `runit/` - scripts for `runit`: <http://smarden.org/runit/>
- `systemd/` - sample service assets for Linux-based test environments

## Build Documentation

Generate the HTML documentation with:

```bash
make docs
```

Output directory:

```text
docs/_build/html/
```
