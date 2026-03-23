# Changelog

## 2.0.14-DEV

- feat: allow `plugins_dir` in the main daemon section to be updated through `-U` on existing config files
- test: added regression coverage for `AppConfig` main-section updates of `plugins_dir`

## 2.0.13-DEV

- test: expanded regression coverage for `libs.com.message` across schedulers, message payloads, and dispatcher flows
- docs: documented the messaging coverage expansion for the current development release

## 2.0.12-DEV

- refactor: normalized `libs.app`, `libs.conf`, and `libs.keys` to the repository class section layout
- docs: documented the normalized structure of the core runtime helper layer

## 2.0.11-DEV

- refactor: normalized `libs.tools.datetool` and `libs.tools.icmp` to the repository class section layout
- docs: documented the normalized structure of the tools layer

## 2.0.10-DEV

- refactor: normalized `libs.templates.modules.TemplateConfigItem` to the repository class section layout
- docs: documented the normalized structure of the template helper layer

## 2.0.9-DEV

- refactor: normalized `libs.com.message` to the repository class section layout
- docs: documented the normalized structure of the messaging layer

## 2.0.8-DEV

- docs: clarified in `AGENTS.md` that the `EOF` section marker applies only to the end of a module file
- refactor: removed incorrect per-class `EOF` markers from `libs.base.classes`

## 2.0.7-DEV

- refactor: normalized `libs.base.classes` to the repository class section layout
- docs: documented the normalized structure of the shared base layer

## 2.0.6-DEV

- refactor: reorganized `server.daemon.AASd` into repository-mandated class sections
- refactor: tightened daemon typing around signal handlers, logger queue setup, and subsystem lifecycle
- docs: documented the normalized daemon class layout

## 2.0.5-DEV

- feat: added lazy package exports for the first-level `libs` package symbols
- refactor: switched first-level imports from `libs.app`, `libs.conf`, and `libs.keys` to `libs`
- test: added regression coverage for deferred loading and exported symbol discovery in `libs`

## 2.0.4-DEV

- test: expanded `libs.tools` coverage for project-specific datetime helpers
- test: added dedicated regression coverage for `Pinger` and `Tracert`

## 2.0.3-DEV

- feat: added lazy package exports for `libs.tools` and switched project imports to the package root
- test: added regression coverage for deferred loading and exported symbol discovery in `libs.tools`
- docs: documented the new `libs.tools` import contract

## 2.0.2-DEV

- feat: added lazy package exports for `libs.templates` and switched project imports to the package root
- refactor: rewrote `TemplateConfigItem.__repr__()` to avoid overlong source lines
- test: added regression coverage for deferred loading and exported symbol discovery in `libs.templates`
- docs: documented the new `libs.templates` import contract

## 2.0.1-DEV

- feat: added lazy package exports for `libs.interfaces` and switched project imports to the package root
- test: added regression coverage for deferred loading and exported symbol discovery in `libs.interfaces`
- docs: documented the new `libs.interfaces` import contract

## 2.0.0-DEV

- refactor: renamed shared `libs.base` mixins from the `B*` convention to explicit `*Mixin` names
- refactor: switched project imports to package-level lazy exports from `libs.base`
- docs: updated base-layer documentation for the new mixin naming and import contract

## 1.0.20-DEV

- feat: added lazy package exports for `libs.base` so shared mixins can be imported from the package root
- test: added regression coverage for deferred loading and exported symbol discovery in `libs.base`
- docs: documented the new `libs.base` import contract in the API and architecture guides

## 1.0.19-DEV

- docs: documented that Poetry is development-only and `requirements.txt` is the production deployment source
- docs: updated project versioning rules so documentation-only changes do not require a version bump
- docs: added the long-term plugin architecture direction to `TODO.md`

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
