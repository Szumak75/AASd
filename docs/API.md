# Business Logic API

**Scope:**
This document describes the current API surface of the daemon runtime and the
plugin host contracts. It is intentionally focused on the daemon, shared
runtime services, worker plugins, and communication plugins.

## API Classification

### Public Runtime API

The following areas should currently be treated as the documented project API:

- daemon bootstrap and runtime orchestration,
- shared configuration contracts,
- messaging and dispatching abstractions,
- utility helpers used directly by plugins,
- communication plugins,
- worker plugins.

## Public Runtime Entry Points

### `aasd.py`

**Purpose:**
Bootstraps the process, changes the working directory to the project root, and
starts the daemon.

**Main flow:**

```python
server = AASd()
server.run()
```

### `server.daemon.AASd`

**Source:** `server/daemon.py`

**Purpose:**
Main application orchestrator.

**Key responsibilities:**

- initialize logging,
- load configuration,
- parse CLI arguments,
- stop startup after automatic config creation or extension until an operator reviews the file,
- start and stop plugin supervision,
- handle process signals,
- supervise plugin lifecycles through the registry service.

**Operational API:**

- `__init__()` - builds the application runtime.
- `run()` - starts the daemon loop.

**Important internal helpers:**

- `__start_subsystem()` - starts dispatcher and plugins.
- `__stop_subsystem()` - stops dispatcher and plugins.
- `__init_command_line()` - binds CLI options to config changes.
- `__password_encoding()` - updates encrypted passwords in config.

The implementation is normalized to the repository class layout rules with
sectioned class blocks and alphabetized members inside each block.

## Shared Runtime Contracts

### `libs`

**Purpose:**
Lazy package entry point for first-level shared runtime symbols.

**Package exports:**

- `AppName`
- `AppConfig`
- `Keys`

**Import contract:**

- `from libs import AppName` is supported,
- exported symbols are resolved from `libs.app`, `libs.conf`, or `libs.keys` on first access,
- direct imports from those first-level modules remain valid.

### `libs.app.AppName`

**Purpose:**
Carries the application name, version, and host name.

**Properties:**

- `app_name: str`
- `app_version: str`
- `app_host_name: str`

**Used by:**
daemon, worker plugins, communication plugins, message builders.

### `libs.conf.AppConfig`

**Purpose:**
Main configuration service for the daemon.

**Operational API:**

- `load() -> bool`
- `save() -> bool`
- `reload() -> bool`

**Configuration API:**

- `app_name`
- `config_file`
- `debug`
- `get_app_dir`
- `password`
- `update`
- `get_plugins`
- `cf`

**Key behavior:**

- creates the initial config file if missing,
- tracks whether the daemon must stop for operator review after automatic config creation or extension,
- exposes the absolute project directory that contains `aasd.py`,
- scans plugin instances from `plugins_dir`,
- reads plugin configuration schemas from plugin manifests,
- renders and updates per-instance config sections.

### `libs.base.classes.PluginConfigMixin`

**Purpose:**
Typed adapter over a plugin configuration section.

**Shared configuration keys exposed by the base class:**

- `at_channel`
- `channel`
- `message_channel`
- `sleep_period`

Worker and communication plugins can extend this class with their own typed
config accessors when a dedicated config wrapper is needed.

### `libs.base`

**Purpose:**
Lazy package entry point for the shared base layer.

**Package exports:**

- `AppNameMixin`
- `ComMixin`
- `ConfigHandlerMixin`
- `ConfigSectionMixin`
- `DebugMixin`
- `LogsMixin`
- `PluginConfigMixin`
- `ProjectClassMixin`
- `ThProcessorMixin`
- `VerboseMixin`

**Import contract:**

- `from libs.base import PluginRuntimeMixin` is supported,
- exported symbols are resolved from `libs.base.classes` on first access,
- direct imports from `libs.base.classes` remain valid for compatibility.

### `libs.plugins.keys.PluginCommonKeys`

**Purpose:**
Public constant class for shared plugin configuration keys.

The active host runtime reuses these constants in parser logic, plugin config
mixins, and helper defaults so shared field names stay centralized.

**Main keys:**

- `at_channel`
- `channel`
- `message_channel`
- `sleep_period`

Typical usage:

- communication plugins consume one `channel`,
- worker plugins emit to one or more `message_channel` targets,
- worker plugins may add cron-like schedules through `at_channel`.

### `libs.plugins.NotificationScheduler`

**Purpose:**
Plugin-facing helper that combines interval-based `message_channel` rules with
cron-like `at_channel` rules and returns the channels currently due for
emission.

### `libs.plugins.keys.PluginHostKeys`

**Purpose:**
Public constant class for daemon-reserved plugin configuration keys.

**Main keys:**

- `autostart`
- `start_delay`
- `restart_policy`

### `libs.templates.schema.PluginConfigField`

**Purpose:**
Schema-level descriptor of one plugin configuration field.

**Main fields:**

- `name`
- `field_type`
- `default`
- `required`
- `description`
- `secret`
- `nullable`
- `choices`
- `example`
- `deprecated`
- `aliases`
- `group`
- `restart_required`

### `libs.templates.schema.PluginConfigSchema`

**Purpose:**
Schema-level descriptor of a full plugin configuration section.

**Main fields:**

- `title`
- `description`
- `version`
- `fields`

### `libs.plugins.runtime`

**Purpose:**
Defines the active plugin runtime contract exposed to plugin authors.

**Main types:**

- `PluginSpec`
- `PluginContext`
- `PluginRuntime`
- `PluginKind`
- `PluginState`
- `PluginHealth`
- `PluginStateSnapshot`
- `PluginHealthSnapshot`
- `DispatcherAdapter`

### `libs.plugins.mixins`

**Purpose:**
Provides typed mixins shared by thread-based plugin runtimes.

`ThPluginMixin` keeps its internal `BData` storage keys in a private class-local
`__Keys` helper instead of a module-level key container.

**Main types:**

- `ThPluginMixin`

### `libs.plugins.loader`

**Purpose:**
Discovers plugin instances from `plugins_dir`, imports `load.py` under an
isolated package context, and validates the returned `PluginSpec`.

### `libs.plugins.config`

**Purpose:**
Parses and validates plugin configuration sections against
`PluginConfigSchema`.

### `libs.plugins.service`

**Purpose:**
Provides plugin supervision for discovery results, runtime construction,
initialization, startup ordering, shutdown, and reporting.

**Main runtime behavior:**

- communication plugins are initialized before worker plugins,
- communication plugins are started before worker plugins,
- startup failures are reported per instance,
- shutdown covers all initialized runtimes,
- current supervision defaults are `restart_policy=none` and
  `health_policy=transitions_only`.

### `libs.templates.schema.PluginConfigSchemaRenderer`

**Purpose:**
Daemon-side helper that renders `PluginConfigSchema` into config-template rows.

The package entry point `libs.templates` exposes `PluginConfigField`,
`PluginConfigSchema`, and `PluginConfigSchemaRenderer` through lazy exports, so
package-level imports do not load the backing implementation module until the
symbols are accessed.

## Messaging API

### `libs.com.message.Message`

**Purpose:**
Message payload exchanged between worker plugins, the dispatcher, and
communication plugins.

**Main fields:**

- `channel`
- `diagnostic_source`
- `to`
- `subject`
- `sender`
- `reply_to`
- `footer`
- `messages`
- `mmessages`

**Multipart support:**

- `Multipart.PLAIN`
- `Multipart.HTML`

**Usage contract:**

Worker plugins create `Message` instances and place them on the shared queue.
Communication plugins consume the routed messages and deliver them externally.
The payload internals keep class-specific `BData` keys private to the `Message`
class instead of sharing one module-wide key registry.
`diagnostic_source` can carry a technical producer identifier used by the
dispatcher when it logs discarded messages addressed to unregistered channels.

## Plugin Runtime API

### `libs.plugins.runtime.PluginKind`

**Purpose:**
Expose the supported plugin kinds used by the daemon runtime.

**Constants:**

- `COMMUNICATION`
- `WORKER`

### `libs.plugins.runtime.PluginContext`

**Purpose:**
Runtime context object passed to plugin factories.

**Main fields:**

- `app_meta: AppName`
- `config`
- `config_handler`
- `debug`
- `dispatcher`
- `instance_name`
- `logger`
- `plugin_id`
- `plugin_kind`
- `qlog`
- `verbose`

**Identity access pattern:**

- `context.app_meta.app_name`
- `context.app_meta.app_version`
- `context.app_meta.app_host_name`

### `libs.plugins.runtime.PluginSpec`

**Purpose:**
Manifest returned by plugin `load.py` entry-points.

**Main fields:**

- `api_version`
- `config_schema`
- `plugin_id`
- `plugin_kind`
- `plugin_name`
- `runtime_factory`

### `libs.plugins.loader.PluginLoader`

**Purpose:**
Discover plugin instances from `plugins_dir` and load `PluginSpec` from
`load.py` with support for plugin-local relative imports.

### `libs.plugins.config.PluginConfigParser`

**Purpose:**
Validate and parse plugin config values using `PluginConfigSchema`.

### `libs.com.message.Channel`

**Purpose:**
Interval-driven notification scheduler.

**Input format example:**

```python
["1", "2:300s", "3:3h"]
```

**Main API:**

- `check -> bool`
- `get -> list[str]`
- `channels -> list[str]`

### `libs.com.message.AtChannel`

**Purpose:**
Cron-like scheduler for message emission.

### `libs.com.message.NotificationScheduler`

**Purpose:**
Stateful helper used by worker plugins to decide which notification channels
should emit at a given moment.

**Input format example:**

```python
["1:0;8|12|16;*;*;1-5"]
```

**Main API:**

- `check -> bool`
- `get -> list[str]`
- `channels -> list[str]`

### `libs.com.message.ThDispatcher`

**Purpose:**
Routes `Message` objects from the shared communication queue to registered
communication-module queues.

**Main API:**

- `register_queue(channel: int) -> Queue`
- `run() -> None`

**Contract:**

- worker plugins write to one shared queue,
- communication plugins register per-channel queues,
- dispatcher fans out messages by `message.channel`.

## Utility API Used By Business Logic

### `libs.tools.datetool.MDateTime`

**Purpose:**
Project-specific date formatting helpers.

**Key methods:**

- `date_now()`
- `datetime_now()`
- `email_date()`
- `mfi_date()`
- `zfs_snapshot_date()`

### `libs.tools.datetool.MIntervals`

**Purpose:**
Converts interval strings such as `5m`, `2h`, or `1d` to seconds.

**Main API:**

- `convert(value: str) -> int`

### `libs.tools.icmp.Pinger`

**Purpose:**
Wrapper over system ICMP tools (`fping` or `ping`) used by `micmp`.

**Main API:**

- `is_alive(ip: str) -> bool`

**Behavior notes:**

- one `is_alive(...)` call performs one system-level ICMP attempt,
- retry policy should be implemented by the caller when multiple attempts are
  required,
- this keeps timeout and shutdown behavior easier to control in worker
  runtimes.

### `libs.tools`

**Purpose:**
Lazy package entry point for shared date and ICMP helpers.

**Package exports:**

- `MDateTime`
- `MIntervals`
- `Pinger`
- `Tracert`

**Import contract:**

- `from libs.tools import MDateTime` is supported,
- exported symbols are resolved from `libs.tools.datetool` or `libs.tools.icmp` on first access,
- direct imports from `libs.tools.datetool` and `libs.tools.icmp` remain valid.

## Plugin Runtime API

### Plugin kinds

The active runtime distinguishes plugin roles through `PluginKind` rather than
directory-based categorization:

- `communication`
- `worker`

### Plugin contract

Each plugin instance is loaded from `plugins_dir/<instance_name>/load.py` under
an isolated package context and is expected to expose `get_plugin_spec()`. The
returned `PluginSpec` declares:

- `api_version`
- `plugin_id`
- `plugin_kind`
- `plugin_name`
- `config_schema`
- `runtime_factory`

### Runtime lifecycle

The daemon creates a `PluginContext`, parses the plugin section with
`PluginConfigParser`, builds the runtime object, and executes the lifecycle in
two phases:

- `initialize()` for communication plugins first,
- `initialize()` for worker plugins second,
- `start()` for communication plugins third, so channel consumers are registered,
- `start()` for worker plugins last, so first-start messages are not lost.

Active runtime state reporting uses:

- `PluginStateSnapshot` for lifecycle state,
- `PluginHealthSnapshot` for operational health.

### Dispatcher integration

- communication plugins register consumer queues for configured channels,
- worker plugins publish `Message` objects through the dispatcher adapter,
- plugin-to-plugin communication is configuration-driven and never implied by
  discovery alone.

### Supervision service

The active runtime uses `PluginRegistryService` to coordinate:

- discovery ordering,
- configuration parsing,
- plugin initialization,
- plugin startup,
- plugin shutdown,
- supervision result reporting through `PluginServiceReport`.

The supervision report currently distinguishes:

- `initialized`
- `managed_runtimes`
- `health_policy`
- `restart_policy`
- `started`
- `failed`
- `skipped`

Current supervision defaults are:

- no automatic restart of failed plugin instances during the active daemon
  cycle,
- `health()` is inspected at lifecycle transition boundaries only,
- shutdown stops all initialized runtimes in reverse order, including runtimes
  that never reached `start()`.

### Config-schema validation

`PluginLoader` validates plugin config schemas before a plugin instance is
accepted into the active runtime.

Current validation rules include:

- daemon-reserved keys from `PluginHostKeys` must not be used as plugin field
  names,
- daemon-reserved keys from `PluginHostKeys` must not be used as plugin field
  aliases,
- field names and aliases must be unique within one plugin schema.

## Current API Boundaries

### Stable Practical Boundary

The most stable practical API boundary in the current codebase is:

- `AASd`
- `AppConfig`
- `AppName`
- `Message`
- `Channel`
- `AtChannel`
- `ThDispatcher`
- `PluginSpec`
- `PluginContext`
- `PluginConfigSchema`
- `PluginConfigParser`
- `PluginLoader`
- `PluginHealthPolicy`
- `PluginRegistryService`
- `PluginRestartPolicy`
- `PluginServiceReport`

### Internal But Important Boundary

The following elements are highly coupled to current implementation details, but
are still essential for understanding the existing business logic:

- thread-based plugin runtime classes,
- shell-based ICMP and ZFS utilities.

## Notes For The Upcoming Refactor

This API reference reflects the code as it exists today. It should be treated as
a practical documentation baseline, not as a claim that every exposed helper is
already a fully stabilized long-term contract.
