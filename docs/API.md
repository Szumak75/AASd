# Business Logic API

**Scope:**
This document describes the current API surface of the existing business logic
and runtime contracts. It is intentionally focused on the daemon, shared
runtime services, worker plugins, and communication plugins. SQLAlchemy
schema models are listed only as dependencies, not as the primary API.

## API Classification

### Public Runtime API

The following areas should currently be treated as the documented project API:

- daemon bootstrap and runtime orchestration,
- shared configuration and importer contracts,
- messaging and dispatching abstractions,
- utility helpers used directly by plugins,
- communication plugins,
- worker plugins.

### Internal Integration API

The following areas are internal and should not be treated as stable entry
points for external integrations or higher-level business workflows:

- `libs.db_models.base`
- `libs.db_models.connectors`
- `libs.db_models.lms.*`
- `libs.db_models.mlms.*`

They remain important for maintenance, query tracing, and refactoring, but they
describe persistence structure rather than public application behavior.

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
- start and stop subsystems,
- handle process signals,
- supervise communication and task threads.

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
- exposes the absolute project directory that contains `aasd.py`,
- scans plugin instances from `plugins_dir`,
- asks plugins for configuration schemas,
- renders and updates per-instance config sections.

### `libs.base.classes.PluginConfigMixin`

**Purpose:**
Typed adapter over a plugin configuration section.

**Shared configuration keys exposed by the base class:**

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
- `ConfigMixin`
- `ConfigHandlerMixin`
- `ConfigSectionMixin`
- `DebugMixin`
- `LogsMixin`
- `PluginRuntimeMixin`
- `PluginConfigMixin`
- `ProjectClassMixin`
- `ThProcessorMixin`
- `VerboseMixin`

**Import contract:**

- `from libs.base import PluginRuntimeMixin` is supported,
- exported symbols are resolved from `libs.base.classes` on first access,
- direct imports from `libs.base.classes` remain valid for compatibility.

**Package exports:**

- `PluginConfigField`
- `PluginConfigSchema`
- `PluginConfigSchemaRenderer`

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
Schema-level descriptor of a complete plugin instance configuration.

**Main fields:**

- `title`
- `fields`
- `description`
- `version`

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

- `app_meta`
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
`load.py`.

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

### `libs.db_models.connectors.LmsMysqlDatabase`

**Purpose:**
Database connector used by LMS/MLMS-related workers.

**Main API:**

- `create_connections() -> bool`
- `create_connections_failover() -> bool`
- session and pool accessors exposed through internal state

**Used by:**
archived LMS-related worker implementations and future database-backed worker
plugins.

## Plugin Runtime API

### Plugin kinds

The active runtime distinguishes plugin roles through `PluginKind` rather than
directory-based categorization:

- `communication`
- `worker`

### Plugin contract

Each plugin instance is loaded from `plugins_dir/<instance_name>/load.py` and is
expected to expose `get_plugin_spec()`. The returned `PluginSpec` declares:

- `api_version`
- `plugin_id`
- `plugin_kind`
- `display_name`
- `config_schema`
- `runtime_factory`

### Runtime lifecycle

The daemon creates a `PluginContext`, parses the plugin section with
`PluginConfigParser`, and starts plugin runtime objects in two phases:

- communication plugins first, so channel consumers are registered,
- worker plugins second, so first-start messages are not lost.

### Dispatcher integration

- communication plugins register consumer queues for configured channels,
- worker plugins publish `Message` objects through the dispatcher adapter,
- plugin-to-plugin communication is configuration-driven and never implied by
  discovery alone.

## Current API Boundaries

### Stable Practical Boundary

The most stable practical API for future refactoring currently appears to be:

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

### Internal But Important Boundary

The following elements are highly coupled to current implementation details, but
are still essential for understanding the existing business logic:

- thread-based plugin runtime classes,
- SQLAlchemy model usage inside worker plugins,
- `LmsMysqlDatabase`,
- shell-based ICMP and ZFS utilities.

## Notes For The Upcoming Refactor

This API reference reflects the code as it exists today. It should be treated as
a baseline for documentation and refactoring, not as a claim that the current
surface is already cleanly separated into domain services.
