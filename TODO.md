# TODO

## Development Direction

- The daemon is now a plugin runtime host and execution supervisor, not the place where business logic should live.
- The legacy `modules.com/*` and `modules.run/*` trees are archived historical material and are no longer part of the active runtime model.
- No backward compatibility layer will be built for the archived module system.
- The active extension model is plugin-based: communication plugins and worker plugins are developed independently from the daemon core.
- Plugins must expose a shared registration and execution API so the daemon can load, supervise, configure, and coordinate them.
- Bidirectional communication must be handled through the daemon dispatcher as a controlled exchange layer between worker plugins and communication plugins.
- Plugins must not assume direct communication with other plugins; all routing rules must be explicitly configured by the user in the configuration file.
- Plugins may keep their own libraries, tools, runtime dependencies, and packaging metadata, including plugin-local `requirements.txt`.
- Plugins are expected to become independently developed components, most likely in separate repositories.
- Shared libraries tightly coupled to the archived implementation, especially `archive/libs/db_models/*`, are not part of the target architecture unless they can be cleanly adapted to the plugin API.
- The daemon must load plugin instances from the `plugins_dir` configured in the main section.
- Each directory entry in `plugins_dir`, including symbolic links, represents one plugin instance.
- The configuration section name for a plugin instance must be derived from the plugin directory or symlink name, not from the implementation identifier.
- This `TODO.md` is the active post-migration plan for hardening and extending the plugin runtime.

## Current Status

- The active runtime loads plugins from `plugins_dir` through `load.py` entry-points.
- `PluginSpec`, `PluginContext`, `PluginLoader`, `PluginConfigParser`, `PluginConfigField`, and `PluginConfigSchema` exist in the active codebase.
- `AppConfig` generates one configuration section per discovered plugin instance and keeps instance configuration separate from implementation identity.
- Legacy runtime code has been moved to `archive/` and is no longer used by the active execution path.
- `example1` and `example2` exist as the first reference plugins for the new runtime.
- Startup ordering ensures communication plugins are started before worker plugins to avoid losing the first message at daemon startup.
- Public documentation and active runtime terminology have been aligned with the plugin model.

## Completed Milestones

- Documented `Plugin API v1` assumptions and the repository migration plan in `docs/PluginAPI.md` and `docs/PluginMigration.md`.
- Implemented schema-based plugin configuration helpers in `libs.templates.schema` and exposed the schema API through package-level lazy exports.
- Implemented the first active plugin runtime foundation in `libs.plugins`.
- Switched `AppConfig` to plugin-instance discovery from `plugins_dir`.
- Added `example1` and `example2` as the first reference plugins for the new runtime model.
- Archived the inactive legacy runtime tree and removed its active execution path.
- Cleaned the active public API and terminology to describe plugins instead of modules.

## P1 - Immediate Work

### Runtime Supervision

- Define lifecycle hooks required by the daemon in a stricter form: initialization, start, stop, and state/health reporting.
- Introduce explicit health/state reporting for plugin runtime instances.
- Ensure plugin initialization errors do not break unrelated plugin instances.
- Define shutdown behavior for partially initialized plugin sets.
- Define restart or reinitialization expectations for failed plugins.

### Host API Stabilization

- Define the future public core surface that plugin authors may rely on.
- Stabilize `PluginContext` as the primary daemon-to-plugin service contract.
- Expose dispatcher and logger access only through stable host-side adapters.
- Separate plugin instance metadata from runtime objects more explicitly.
- Decide whether `PluginRuntime` should remain protocol-based or become a stricter concrete interface contract.

### Configuration And Validation

- Strengthen schema validation and parsed-value validation around `PluginConfigField` and `PluginConfigSchema`.
- Define which schema features are mandatory for API v1 and which remain optional.
- Decide whether `libs.templates.modules` remains only as an internal render layer or is fully replaced in the active runtime.
- Keep communication routing user-defined through config variables only.
- Ensure configuration mistakes in channel mapping are visible to the user and never create hidden cross-plugin coupling.

### Plugin Discovery And Registration

- Validate plugin API version before registration with stricter diagnostics.
- Reject invalid, incomplete, or duplicate plugin registrations with explicit logging.
- Harden symbolic-link-based instance duplication so section-name collisions and duplicate runtime registration are handled predictably.
- Decide whether plugin manifests should continue to be returned by `get_plugin_spec()` only, or whether another manifest form is needed in future API versions.

## P2 - Next Refactoring Stage

### Service Layer Extraction

- Build a dedicated plugin registry service responsible for discovery, validation, registration, and lifecycle control.
- Move plugin supervision concerns out of `server.daemon.AASd` into a clearer runtime-management layer.
- Keep plugin instance metadata, manifest data, and runtime object state separate.

### Shared Runtime Surface

- Review which parts of `libs.base`, `libs.com.message`, dispatcher logic, and selected `libs.tools` helpers should remain public and supported for plugin authors.
- Remove or further isolate helper classes that are only historical or internal implementation details.
- Decide which low-level runtime helpers remain stable API and which must stay daemon-internal.

### Data Access And Business Isolation

- Keep new business logic out of the archived `modules.*` tree.
- Retain only those helpers that are demonstrably reusable under the new plugin API.
- Keep `archive/libs/db_models/*` outside the supported plugin API unless a clean adapter boundary is introduced.

### Tests

- Add discovery tests for symlinked plugin instances in the active runtime test suite.
- Add lifecycle and shutdown tests for plugin supervision.
- Add tests for partial startup failure and isolated plugin initialization errors.
- Add more dispatcher integration tests for worker-to-communication routing configured by the user.
- Add tests for duplicate plugin identity and invalid registration edge cases.

## P3 - Structural Cleanup

### Runtime Simplification

- Continue removing daemon internals that still reflect the historical module-oriented implementation.
- Reduce public surface area where active code still exposes helper layers that are not meant to be stable plugin API.
- Keep `archive/` strictly non-runtime and non-imported from active code.

### Documentation Follow-Up

- Keep the plugin directory layout and the `load.py` entry-point convention documented and current.
- Keep the versioned plugin API and manifest structure synchronized with implementation changes.
- Keep configuration rules for instance naming and explicit channel routing synchronized with implementation changes.
- Document lifecycle, health/state reporting, and failure-handling rules once the supervision model is finalized.
- Expand example plugin documentation beyond `example1` and `example2` once the host API is considered stable.

## Backlog

- Decide whether plugin-local virtual environments are in or out of scope for the first production-ready plugin runtime.
- Decide whether plugin dependency installation and verification belong to the daemon scope or remain fully external.
- Decide whether plugin packaging conventions should be standardized beyond `load.py` and `requirements.txt`.
