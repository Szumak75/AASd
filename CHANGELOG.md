# Changelog

## 2.1.15-DEV

- feat: added `libs.plugins.service` with `PluginRegistryService`, `PluginServiceReport`, `PluginFailure`, and `PluginSkip`
- refactor: moved plugin discovery and lifecycle orchestration out of `server.daemon.AASd` into the registry service
- feat: added partial startup failure reporting with explicit failed and skipped plugin instances
- test: split startup-order verification to the registry-service layer and added daemon delegation and failure-isolation coverage
- docs: updated the active API surface and `TODO.md` to reflect the new supervision service and report model

## 2.1.13-DEV

- style: wrapped the example2 stdout print payload string to align with the shorter line-length convention
- docs: updated `TODO.md` to reflect the implemented plugin lifecycle, shared plugin keys, archived data models, and the current supervision backlog

## 2.1.12-DEV

- style: wrapped an overlong configuration description string in `plugins/example2/load.py`

## 2.1.11-DEV

- refactor: removed an unused `BClasses` import from `libs.plugins.runtime` after the `DispatcherAdapter` typed-storage cleanup

## 2.1.10-DEV

- refactor: switched `DispatcherAdapter` to typed `BData` storage for dispatcher and queue references
- test: added regression coverage for `DispatcherAdapter` publish and consumer registration paths

## 2.1.9-DEV

- feat: added public shared plugin configuration key classes in `libs.plugins.keys`
- refactor: switched example plugins to use shared public plugin key constants instead of raw string literals
- test: added regression coverage for the public plugin key classes
- docs: documented `libs.plugins.keys` as part of the active plugin API surface

## 2.1.8-DEV

- refactor: moved `libs/db_models` to `archive/libs/db_models` as historical plugin-specific data-model definitions
- docs: removed `libs.db_models` from the active runtime documentation surface and updated migration notes

## 2.1.7-DEV

- fix: changed `PluginLoader` validation helper to return `PluginSpec` directly so static type checkers can narrow the loader return type correctly

## 2.1.6-DEV

- refactor: tightened `PluginLoader` typing with `cast` plus `TypeGuard` for `get_plugin_spec()` return validation

## 2.1.5-DEV

- refactor: aligned `PluginKind` with the project-standard `ReadOnlyClass` constant pattern

## 2.1.4-DEV

- fix: replaced `Enum`-based plugin lifecycle constants with the project-standard `ReadOnlyClass` constant pattern
- refactor: simplified plugin state and health snapshots to store string values compatible with the new constant classes

## 2.1.3-DEV

- feat: defined a stricter plugin runtime lifecycle with `initialize()`, `start()`, `stop()`, `state()`, and `health()`
- feat: added `PluginState`, `PluginHealth`, and snapshot types to the active plugin runtime API
- refactor: updated daemon startup and shutdown to use the new two-phase plugin lifecycle
- test: updated plugin runtime regression coverage for initialization, state, and health reporting
- docs: documented the stricter runtime lifecycle in the plugin API and active API reference

## 2.1.2-DEV

- refactor: renamed active base-layer mixins and main-config helpers from module-oriented names to plugin-oriented names
- refactor: removed the inactive `modules` main-section config entry from active configuration fixtures and main-config internals
- docs: aligned installation, API, architecture, flow, and API-surface guides with plugin-oriented runtime terminology
- docs: rewrote `TODO.md` as the active post-migration plan for hardening and extending the plugin runtime
- test: updated base-layer lazy-export coverage for the renamed plugin mixins

## 2.1.1-DEV

- refactor: removed `TemplateConfigItem` from the active `libs.templates` public export surface
- docs: cleaned the active API and architecture guides to describe only the plugin runtime public contract
- test: updated `libs.templates` lazy-export regression coverage for the schema-only public package surface

## 2.1.0-DEV

- feat: expanded plugin runtime tests for loader validation, config parsing, and daemon-level plugin-section generation
- refactor: archived the inactive `modules.*` runtime tree and removed legacy loader contracts from the active runtime API
- docs: updated the public API surface to describe only the active plugin runtime model

## 2.0.16-DEV

- feat: added schema-based plugin configuration helpers `PluginConfigField`, `PluginConfigSchema`, and `PluginConfigSchemaRenderer`
- feat: added the initial plugin runtime foundation with `PluginSpec`, `PluginContext`, `PluginLoader`, and `PluginConfigParser`
- feat: switched active config generation to plugin-instance discovery from `plugins_dir`
- feat: added `plugins/example1` and `plugins/example2` as the first reference plugins for the new runtime model
- test: added regression coverage for `libs.templates` lazy exports and schema rendering helpers
- test: added regression coverage for plugin discovery, config parsing, and plugin-section generation in `AppConfig`
- docs: documented the new schema helpers in the API reference and updated the active migration plan

## 2.0.15-DEV

- feat: added `AppConfig.get_app_dir` to expose the absolute directory containing `aasd.py`
- test: added regression coverage for the application root accessor
- docs: rewrote `TODO.md` to define the plugin-only target runtime, archival of the legacy module model, and the planned example communication flow
- docs: added `Plugin API v1` and migration planning documents and aligned architecture docs with the plugin-only target model
- docs: selected a schema-based plugin configuration contract built around `PluginConfigField` and `PluginConfigSchema`

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
