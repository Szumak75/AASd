# Changelog

## 1.0.19-DEV

- docs: documented that Poetry is development-only and `requirements.txt` is the production deployment source
- docs: updated project versioning rules so documentation-only changes do not require a version bump

## 1.0.18-DEV

- chore: refreshed production `requirements.txt` from the current Poetry runtime lock set

## 1.0.17-DEV

- docs: converted `TODO.md` into a prioritized operational refactoring plan with `P1/P2/P3` stages

## 1.0.16-DEV

- docs: updated `TODO.md` to reflect completed documentation work and the next refactoring stages

## 1.0.15-DEV

- docs: defined the public runtime API boundary versus the internal ORM layer
- docs: added API surface policy and aligned Sphinx release metadata with project version

## 1.0.14-DEV

- docs: normalized communication module docstrings in `modules/com/`
- docs: normalized ORM docstrings across `libs/db_models/`

## 1.0.13-DEV

- docs: normalized business module docstrings across `modules/run/`

## 1.0.12-DEV

- docs: normalized package, interface, key, template, and tool docstrings across `libs/` excluding `libs/db_models`

## 1.0.11-DEV

- docs: normalized daemon orchestration docstrings in `server/daemon.py`

## 1.0.10-DEV

- docs: clarified that classes in `libs/base/classes.py` are mixin-style helpers
- docs: added TODO entry for future naming refactor of mixin classes

## 1.0.9-DEV

- docs: normalized shared core docstrings in app, base classes, config, and messaging modules

## 1.0.8-DEV

- docs: corrected FreeBSD package examples in the installation guide for Python 3.11

## 1.0.7-DEV

- docs: added Mermaid support to the Sphinx documentation toolchain
- docs: enabled clean rendering of the flow diagram in generated HTML

## 1.0.6-DEV

- docs: added TODO recommendations for documentation and refactoring work
- docs: added Sphinx and MyST documentation toolchain
- docs: added generated API reference entry pages and build workflow

## 1.0.5-DEV

- docs: added architecture analysis for the current codebase
- docs: added business logic API reference for daemon, shared runtime, and modules
- docs: updated documentation indexes and module catalogue
