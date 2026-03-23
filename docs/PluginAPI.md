# Plugin API v1

**Source:** `docs/PluginAPI.md`

**Purpose:**
Define the target plugin runtime contract for AASd and replace the legacy
`modules.com/*` and `modules.run/*` loading model with a plugin-instance model
based on `plugins_dir`.

## Scope

This document describes the target API and runtime behavior for plugins loaded
by the daemon.

It is a design document for the next implementation phase. It is not a
description of the current runtime behavior.

The legacy `modules.*` model is considered historical only and is excluded from
the future runtime path.

## Goals

- Make the daemon a runtime host and supervisor instead of a business-logic container.
- Load plugin instances from a user-configured `plugins_dir`.
- Support plugin instancing by directory name and symbolic link name.
- Provide one stable, versioned plugin API for all plugin authors.
- Keep communication routing explicit and user-configured.
- Avoid direct plugin-to-plugin coupling outside the dispatcher contract.

## Non-Goals

- No backward compatibility with the legacy `modules.com/*` and `modules.run/*` loaders.
- No compatibility adapter for legacy modules.
- No automatic migration of old module implementations to the new plugin API.
- No implicit routing rules between worker and communication plugins.

## Runtime Model

The daemon should discover plugin instances from the directory configured as
`plugins_dir` in the main config section.

Each direct child entry in `plugins_dir` represents exactly one plugin
instance:

- a normal directory is one instance,
- a symbolic link to a plugin directory is also one instance,
- the instance name is derived from the entry name visible in `plugins_dir`.

The plugin implementation identity and the plugin instance identity must remain
separate:

- `plugin_id` identifies the implementation,
- `instance_name` identifies the configured runtime instance.

This separation allows one implementation to run multiple times with different
configuration sections.

## Plugin Directory Layout

The minimum required plugin layout is:

```text
plugins/
  example1/
    load.py
  example2/
    load.py
```

Recommended extended layout:

```text
plugins/
  email_primary/
    load.py
    README.md
    requirements.txt
    plugin/
      __init__.py
      runtime.py
      config.py
  email_secondary -> /opt/aasd-plugins/email-plugin
```

Rules:

- `load.py` is mandatory.
- The daemon should treat the plugin root directory as the plugin import root.
- Plugin-local helper packages may live under a plugin-owned subdirectory.
- A plugin may keep its own dependencies and packaging metadata.

## Entry-Point Contract

Each plugin instance must expose `load.py` as its daemon entry-point.

`load.py` must expose exactly one public factory function:

```python
def get_plugin_spec() -> "PluginSpec":
    ...
```

The daemon should import `load.py`, call `get_plugin_spec()`, validate the
result, and register the plugin before starting the runtime instance.

Why `get_plugin_spec()`:

- it keeps plugin loading explicit,
- it avoids side effects during import,
- it makes validation deterministic,
- it gives a stable contract for versioned API evolution.

## Plugin Kinds

`PluginSpec.plugin_kind` must define one of two allowed values:

- `communication`
- `worker`

No other kinds are supported by API v1.

The daemon must not infer plugin kind from path, module name, or class name.

## PluginSpec

`PluginSpec` is the manifest returned by `get_plugin_spec()`.

Required fields:

- `api_version: int`
- `plugin_id: str`
- `plugin_kind: str`
- `plugin_name: str`
- `runtime_factory: Callable[[PluginContext], PluginRuntime]`
- `config_schema: PluginConfigSchema`

Recommended optional fields:

- `plugin_version: str`
- `description: str`
- `author: str`
- `homepage: str`

Field meanings:

- `api_version`:
  The plugin API version expected by the implementation.
- `plugin_id`:
  Stable implementation identifier. It must not depend on the instance name.
- `plugin_kind`:
  Runtime role of the plugin.
- `plugin_name`:
  Human-readable implementation name.
- `runtime_factory`:
  Factory used by the daemon to build the runtime object.
- `config_schema`:
  Declarative configuration schema used to validate and render the instance
  config section.

## Instance Identity And Configuration

The daemon must derive `instance_name` from the plugin directory or symlink name
inside `plugins_dir`.

Example:

```text
plugins/
  email_primary/
  email_secondary -> /srv/aasd-plugins/email
```

Both entries may return the same `plugin_id`, but they must produce two
independent config sections:

```ini
[email_primary]
...

[email_secondary]
...
```

Configuration rules:

- one plugin instance maps to one config section,
- config section name equals instance name,
- the daemon must auto-create missing instance sections,
- the daemon must not delete user config when a plugin instance disappears,
- config generation must operate on discovered instances, not implementation ids.

## Shared Configuration Keys

Shared plugin configuration keys that are part of the public API should not be
redeclared as raw strings inside plugin code.

The package `libs.plugins.keys` provides public constant classes for this
purpose:

- `PluginCommonKeys`
  Shared keys used by multiple plugin types, for example `channel`,
  `message_channel`, and `sleep_period`.
- `PluginHostKeys`
  Daemon-reserved keys used for host-side lifecycle and management semantics,
  for example `autostart`, `start_delay`, and `restart_policy`.

Rules:

- plugin authors should import shared keys from `libs.plugins`,
- plugins may define private keys locally when they are plugin-specific,
- plugins must not redefine daemon-reserved host key semantics.

## PluginContext

The daemon should pass a `PluginContext` object to `runtime_factory`.

Minimum required fields:

- `app_name`
- `app_version`
- `app_host_name`
- `instance_name`
- `plugin_id`
- `plugin_kind`
- `config`
- `logger`
- `dispatcher`
- `debug`
- `verbose`

Purpose:

- isolate plugins from direct knowledge of daemon internals,
- make shared services explicit,
- stabilize the host-plugin boundary.

## Runtime Contract

The object returned by `runtime_factory` must implement the daemon runtime
contract.

Required methods:

```python
class PluginRuntime(Protocol):
    def initialize(self) -> None: ...
    def start(self) -> None: ...
    def stop(self, timeout: float | None = None) -> None: ...
    def state(self) -> PluginStateSnapshot: ...
    def health(self) -> PluginHealthSnapshot: ...
```

The daemon owns the lifecycle order:

1. build runtime from `runtime_factory`,
2. call `initialize()` for communication plugins,
3. call `initialize()` for worker plugins,
4. call `start()` for communication plugins,
5. call `start()` for worker plugins,
6. call `stop()` during shutdown.

The plugin owns its internal work loop and reports state through two snapshot
types:

- `PluginStateSnapshot` for lifecycle state:
  `created`, `initialized`, `starting`, `running`, `stopping`, `stopped`, `failed`
- `PluginHealthSnapshot` for operational condition:
  `unknown`, `healthy`, `degraded`, `unhealthy`

This keeps lifecycle supervision separate from runtime health reporting.

## Dispatcher API

The dispatcher remains the only supported exchange layer between worker and
communication plugins.

The plugin-facing dispatcher API should be role-specific.

For `communication` plugins:

- register a consumer channel,
- receive messages routed to configured channel ids,
- consume only messages addressed to their configured channels.

For `worker` plugins:

- publish `Message` objects to the dispatcher input,
- never assume the existence of any communication plugin,
- rely entirely on configured channel ids.

This means:

- a worker may emit to channel `10`,
- a communication plugin may listen on channel `10`,
- message delivery happens only if the user configures both sides consistently.

There must be no hidden direct plugin lookup by `plugin_id`, no automatic peer
binding, and no path-based wiring.

## Plugin Configuration Schema

Plugins must expose a schema through `PluginSpec.config_schema`.

The schema is the configuration contract of the plugin. It is not a direct
description of INI lines.

API v1 should introduce two dedicated descriptor objects:

- `PluginConfigField`
- `PluginConfigSchema`

### `PluginConfigField`

Represents one configuration field declared by the plugin.

Minimum required attributes:

- `name`
- `field_type`
- `default`
- `required`
- `description`

Recommended optional attributes:

- `secret`
- `nullable`
- `choices`
- `example`
- `deprecated`
- `aliases`
- `group`
- `restart_required`

### `PluginConfigSchema`

Represents the full configuration schema of the plugin instance.

Minimum required attributes:

- `title`
- `fields`

Recommended optional attributes:

- `description`
- `groups`
- `version`

The schema should be the single source of truth for:

- config generation,
- config parsing,
- config validation,
- future config documentation.

## Config Rendering Contract

The daemon should convert `PluginConfigSchema` into the actual config section
written to disk.

This means the daemon must own a dedicated rendering layer:

- `PluginConfigSchema` is the API contract,
- INI generation is an output format,
- comments and default values are produced by the renderer.

The daemon should use the schema to:

- create a new section for a newly discovered plugin instance,
- append missing variables to an existing instance section,
- preserve existing user-edited values.

The schema must describe instance-local variables only.

The main daemon section remains responsible for host-level variables such as:

- `debug`
- `verbose`
- `salt`
- `plugins_dir`

## Why Not Reuse `TemplateConfigItem`

`TemplateConfigItem` is a useful legacy helper for building standardized config
files, but it is line-oriented and renderer-oriented.

The new plugin runtime needs a schema-oriented contract because:

- plugin configuration should be typed before it is rendered,
- validation should operate on fields, not on rendered lines,
- future tooling should be able to derive docs and validation rules from the
  same schema,
- plugin authors should describe configuration meaning, not output formatting.

`TemplateConfigItem` may still be reused internally as a renderer helper if
that reduces implementation cost, but it should not be the public plugin API
contract.

## Example Plugins Planned For API Finalization

Two minimal reference plugins should be created when the API implementation is
ready.

### `example1`

Worker plugin.

Behavior:

- emits one `Message` during daemon startup,
- sends it to one or more configured channel ids,
- does not assume any consumer exists.

### `example2`

Communication plugin.

Behavior:

- subscribes to configured channel ids,
- receives routed `Message` objects from the dispatcher,
- prints them to stdout.

The user must configure matching channels manually in the config file. Message
delivery must fail safely when channels are not configured to match.

## Loader And Registry Responsibilities

The future daemon core should introduce dedicated services:

- `PluginLoader`
  - scans `plugins_dir`,
  - imports `load.py`,
  - calls `get_plugin_spec()`,
  - validates API version and manifest shape.
- `PluginRegistry`
  - stores plugin instance metadata,
  - guards instance-name uniqueness,
  - separates discovery metadata from runtime objects.
- `PluginConfigService`
  - generates and updates config sections for discovered plugin instances.
- `PluginSupervisor`
  - starts and stops plugin runtime instances,
  - tracks health and shutdown state.

## Archive Plan For Legacy Runtime

The legacy runtime model should be moved out of the active execution path into
an archive tree with preserved structure.

Target archive shape:

```text
archive/
  modules/
    com/
    run/
  legacy_runtime/
    ...
```

Candidate archive sources:

- `modules/com/*`
- `modules/run/*`
- legacy loader logic in the daemon and config service
- legacy interfaces that exist only to support `modules.*`

Reusable shared infrastructure should stay active only if it can support the new
plugin API without carrying path-based or legacy module assumptions.

## Migration Sequence

Recommended implementation order:

1. Define `PluginSpec`, `PluginContext`, and the runtime protocol in code.
2. Build `PluginLoader`, `PluginRegistry`, and plugin config generation.
3. Replace active daemon startup so it uses plugin discovery from `plugins_dir`.
4. Move legacy runtime-loading logic and legacy modules into `archive/`.
5. Add `example1` and `example2`.
6. Add regression tests for discovery, config generation, dispatcher routing,
   symlinked instances, and shutdown behavior.

## Suggested Minimal API Sketch

The initial code-level shape may look like this:

```python
class PluginConfigField:
    name: str
    field_type: object
    default: object
    required: bool
    description: str
    secret: bool = False
    nullable: bool = False
    choices: list[object] | None = None
    example: object | None = None
    deprecated: bool = False
    aliases: list[str] | None = None
    group: str | None = None
    restart_required: bool = False
```

```python
class PluginConfigSchema:
    title: str
    fields: list[PluginConfigField]
    description: str | None = None
    version: int = 1
```

The daemon-side adapter should then perform:

1. schema validation,
2. config section rendering,
3. missing-field update handling,
4. parsed-value validation before plugin start.

## Open Decisions

- Whether plugin runtime objects should be threads directly or whether the
  daemon should own thread wrappers around plugin logic.
- Whether plugin-local dependency installation is managed by deployment tooling
  or merely documented by plugin authors.
