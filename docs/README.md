# Documentation Index

This directory contains project documentation, operational notes, module guides,
and generated API-oriented reference material for the current codebase.

Deployment documentation assumes `requirements.txt` is the production runtime
installation source, while Poetry remains a development-only tool.

## Core Documents

- [Installation](./Installation.md) - environment setup and service preparation.
- [Modules](./Modules.md) - module catalogue and configuration entry points.
- [Flow](./Flow.md) - runtime flow and subsystem relationships.
- [Architecture](./Architecture.md) - project-wide structural analysis.
- [API](./API.md) - business logic API and runtime contracts.
- [API Surface](./API-Surface.md) - boundary between public runtime API and internal ORM layer.

## Module Guides

- [MEmailAlert](./MEmailAlert.md)
- [MIcmp](./MIcmp.md)
- [MLmsPayment](./MLmsPayment.md)
- [MLmsTariff](./MLmsTariff.md)
- [MZfsSnapshot](./MZfsSnapshot.md)

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
