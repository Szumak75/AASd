# TODO

## Development Direction

- Target architecture: the daemon should become a runtime management and execution-control system, not the place where business logic lives.
- Current `modules.com/*` and `modules.run/*` are treated as archived historical material and are no longer part of the target runtime model.
- No backward compatibility layer will be built for the legacy module system.
- The target state is a plugin-based model where communication plugins and worker plugins are developed independently from the daemon core.
- Plugins must expose a shared registration and execution API so the daemon can load, supervise, configure, and coordinate them.
- Bidirectional communication must be handled through the daemon dispatcher as a controlled exchange layer between worker plugins and communication plugins.
- Plugins must not assume direct communication with other plugins; all routing rules must be explicitly configured by the user in the configuration file.
- Plugins should keep their own libraries, tools, and runtime dependencies, including their own `requirements.txt`.
- Plugins are expected to become independently developed components, most likely in separate repositories.
- Shared libraries tightly coupled to the legacy implementation, especially `libs.db_models/*`, are not part of the target architecture unless they can be cleanly adapted to the new plugin API.
- The daemon must load plugin instances from the `plugins_dir` configured in the main section.
- Each directory entry in `plugins_dir`, including symbolic links, represents one plugin instance.
- The configuration section name for a plugin instance must be derived from the plugin directory or symlink name, not from the implementation identifier.
- The current `TODO.md` should be treated as the active migration plan for replacing the legacy model with the plugin runtime.

## Status

- Legacy runtime model remains present in the repository and still defines the current execution flow.
- Target plugin loader, registry, manifest, and unified runtime API do not exist yet.
- Example replacement plugins are planned but not implemented.

## Completed Milestones

- Documented `Plugin API v1` assumptions and the repository migration plan in `docs/PluginAPI.md` and `docs/PluginMigration.md`.
- Implemented the first schema-based plugin configuration helpers in `libs.templates.schema` and exposed them through package-level lazy exports.

## P1 - Immediate Work

### Runtime Contracts

- Define the new plugin API boundary as the only supported extension model.
- Define a versioned plugin manifest structure returned by the plugin entry-point.
- Define a strict `plugin_kind` contract with exactly two supported values: `communication` and `worker`.
- Define lifecycle hooks required by the daemon: registration, initialization, start, stop, and health/state reporting.
- Define how a plugin receives daemon services during initialization: logger access, dispatcher access, configuration handler bound to the instance section, and application metadata.
- Define `PluginConfigField` and `PluginConfigSchema` as the public plugin configuration contract.
- Define the renderer and validator boundary so plugin authors describe schema semantics and the daemon renders the INI section format.

### Plugin Discovery And Loading

- Load plugins only from the path declared by `plugins_dir` in the main daemon section.
- Treat every direct child directory or symlink in `plugins_dir` as one plugin instance candidate.
- Ignore plugin categorization based on path naming; plugin type must come from the plugin API manifest.
- Adopt a folder-level entry-point convention based on `load.py`.
- Define the minimum required exports from `load.py`.
- Validate plugin API version before registration.
- Reject invalid, incomplete, or duplicate plugin registrations with explicit logging.

### Configuration Model

- Generate one configuration section per plugin instance using the plugin directory or symlink name.
- Keep plugin implementation identity separate from plugin instance identity.
- Ensure adding a new plugin instance automatically adds a new config section with default values.
- Ensure removing a plugin instance does not silently delete user configuration.
- Ensure config generation and config updates operate on plugin instances, not on implementation names.
- Keep communication routing user-defined through config variables only.
- Avoid any implicit message routing between worker and communication plugins.
- Replace `TemplateConfigItem` as the public plugin-facing contract with a schema-oriented descriptor model.

### Business Refactoring Preparation

- Identify which parts of `libs.base`, `libs.interfaces`, `libs.templates`, `libs.com.message`, and dispatcher logic can be retained and adapted to the plugin runtime.
- Identify which parts of the current runtime are legacy-only and should be moved to the archive tree without reuse.
- Define the future public core surface that plugin authors may rely on.
- Exclude legacy business implementations from future runtime planning.
- Decide whether `libs.templates` remains only as an internal render layer or is fully replaced in the active runtime.

### Functional Risks

- The current loader depends on file naming conventions and relative paths; this must be eliminated in the new model.
- The current config generation model is bound to importable Python modules under `modules.*`; this must be replaced with plugin instance discovery from `plugins_dir`.
- Symbolic-link-based instance duplication requires careful identity handling to avoid section-name collisions and duplicate runtime registration.
- Plugin initialization errors must not break unrelated plugin instances.
- Configuration mistakes in channel mapping must be visible to the user and must not result in hidden cross-plugin coupling.

## P2 - Next Refactoring Stage

### Service Layer Extraction

- Build a plugin registry service responsible for discovery, validation, registration, and lifecycle control.
- Build a plugin context object passed to plugins during initialization.
- Build dispatcher-facing adapters so plugin code depends on stable daemon services instead of internal daemon implementation details.
- Separate plugin instance metadata from runtime objects.

### Data Access

- Stop designing new business logic around the legacy `modules.*` tree.
- Move legacy business modules and legacy runtime-loading code to an archive tree with preserved structure.
- Remove legacy runtime code from the active execution path as soon as the plugin loader is ready.
- Retain only those helpers that are demonstrably reusable under the new plugin API.

### Tests

- Add discovery tests for plugin directories and symlinked plugin instances.
- Add validation tests for malformed `load.py` entry-points and invalid plugin manifests.
- Add config generation tests for per-instance sections created from plugin directory names.
- Add schema validation tests for `PluginConfigField` and `PluginConfigSchema`.
- Add dispatcher integration tests for worker-to-communication message routing configured by the user.
- Add shutdown and lifecycle tests for plugin supervision.

## P3 - Structural Cleanup

### Naming And Internal API Cleanup

- Remove daemon assumptions that plugin type can be inferred from import path.
- Replace legacy `modules.com` and `modules.run` terminology in active runtime code with plugin-oriented terminology.
- Introduce consistent naming for plugin implementation id, plugin instance name, and plugin kind.
- Archive or remove legacy mixins and interfaces that cannot be adapted cleanly.

### Documentation Follow-Up

- Document the plugin directory layout and the `load.py` entry-point convention.
- Document the versioned plugin API and the plugin manifest structure.
- Document configuration rules for instance naming and explicit channel routing.
- Document the absence of backward compatibility with the legacy module model.
- Document the migration of legacy runtime code to the archive area.
- Provide two example plugins when the API is finalized:
  - `example1`: worker plugin that emits one message at each daemon start
  - `example2`: communication plugin that consumes configured messages and prints them to stdout
- Document that message delivery between `example1` and `example2` depends entirely on user-defined channel configuration.

## Backlog

- Define archive placement rules for the legacy runtime tree while preserving historical structure for reference.
- Decide whether plugin-local virtual environments are in or out of scope for the first implementation.
- Decide whether plugin manifests should be returned by a function or by a manifest object exported from `load.py`.
