# Business Logic API

**Scope:**
This document describes the current API surface of the existing business logic
and runtime contracts. It is intentionally focused on the daemon, shared
runtime services, business-task modules, and communication modules. SQLAlchemy
schema models are listed only as dependencies, not as the primary API.

## API Classification

### Public Runtime API

The following areas should currently be treated as the documented project API:

- daemon bootstrap and runtime orchestration,
- shared configuration and importer contracts,
- messaging and dispatching abstractions,
- utility helpers used directly by modules,
- communication modules,
- business-task modules.

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

- `__start_subsystem()` - starts dispatcher and modules.
- `__stop_subsystem()` - stops dispatcher and modules.
- `__init_command_line()` - binds CLI options to config changes.
- `__password_encoding()` - updates encrypted passwords in config.

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
daemon, task modules, communication modules, message builders.

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
- `password`
- `update`
- `module_conf`
- `get_com_modules`
- `get_run_modules`
- `cf`

**Key behavior:**

- creates the initial config file if missing,
- scans `modules.com` and `modules.run`,
- asks modules for configuration templates,
- returns only enabled modules listed in config.

### `libs.base.classes.ModuleConfigMixin`

**Purpose:**
Typed adapter over a module configuration section.

**Shared configuration keys exposed by the base class:**

- `channel`
- `message_channel`
- `sleep_period`

Each business module extends this class with its own typed config accessors.

### `libs.base.classes.ImporterMixin`

**Purpose:**
Dynamic module discovery and import helper.

**Operational API:**

- `import_name_list(package: str) -> list`
- `import_module(package: str, name: str) -> object | None`

**Naming contract:**

- module file starts with `m`,
- imported class name is derived from the file name,
- current convention strongly influences runtime discovery.

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
- `ImporterMixin`
- `LogsMixin`
- `ModuleMixin`
- `ModuleConfigMixin`
- `ProjectClassMixin`
- `ThProcessorMixin`
- `VerboseMixin`

**Import contract:**

- `from libs.base import ModuleMixin` is supported,
- exported symbols are resolved from `libs.base.classes` on first access,
- direct imports from `libs.base.classes` remain valid for compatibility.

### `libs.templates.modules.TemplateConfigItem`

**Purpose:**
Single configuration template row used during config generation.

**Fields:**

- `varname`
- `value`
- `desc`

**Used by:**
all modules implementing `template_module_variables()`.

The package entry point `libs.templates` exposes `TemplateConfigItem` through a
lazy export, so `from libs.templates import TemplateConfigItem` does not load
`libs.templates.modules` until the symbol is accessed.

## Messaging API

### `libs.com.message.Message`

**Purpose:**
Message payload exchanged between `modules/run` and `modules/com`.

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

Task modules create `Message` instances and place them on the shared queue.
Communication modules consume the routed messages and deliver them externally.

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

- task modules write to one shared queue,
- communication modules register per-channel queues,
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
Database connector used by LMS/MLMS-related modules.

**Main API:**

- `create_connections() -> bool`
- `create_connections_failover() -> bool`
- session and pool accessors exposed through internal state

**Used by:**
`mlmspayment`, `mlmstariff`.

## Communication Module API

### `modules.com.memailalert.MEmailalert`

**Purpose:**
SMTP-based outbound e-mail delivery module.

**Runtime role:**
Consumes `Message` objects from a dedicated channel queue and sends email.

**Config API:**

- `channel`
- `smtp_server`
- `smtp_user`
- `smtp_pass`
- `address_from`
- `address_to`
- `debug_bcc`
- `sleep_period`

### `modules.com.memailalert2.MEmailalert2`

**Purpose:**
Second SMTP delivery module with the same delivery contract as `MEmailalert`.

**Runtime role:**
Allows alternative mail configuration without changing the producer side.

## Task Module API

### `modules.run.micmp.MIcmp`

**Purpose:**
Detects IPv4 reachability changes and generates incident notifications.

**Dependencies:**

- `Pinger`
- `Channel`
- `Message`
- `MDateTime`

**Config API:**

- `hosts`
- `message_channel`
- `sleep_period`

**Related helper type:**

- `Ipv4Test` - tracks host state transitions and timestamps.

### `modules.run.mlmspayment.MLmspayment`

**Purpose:**
Generates payment reminders and diagnostic summaries using LMS/MLMS data.

**Dependencies:**

- `AtChannel`
- `Message`
- `LmsMysqlDatabase`
- `libs.db_models.lms`
- `libs.db_models.mlms`

**Config API:**

- `at_channel`
- `diagnostic_channel`
- `message_channel`
- `payment_message`
- `default_paytime`
- `cutoff_time`
- `skip_groups`
- `sql_server`
- `sql_database`
- `sql_user`
- `sql_pass`
- `lms_url`
- `user_url`
- `message_footer`

**Business role:**
This is one of the central domain modules in the current codebase.

### `modules.run.mlmstariff.MLmstariff`

**Purpose:**
Checks tariff assignments for nodes using LMS/MLMS-backed data.

**Dependencies:**

- `AtChannel`
- `LmsMysqlDatabase`
- `libs.db_models.lms`
- `libs.db_models.mlms`

**Config API:**

- `at_channel`
- `message_channel`
- `sql_server`
- `sql_database`
- `sql_user`
- `sql_pass`
- `sleep_period`

**Business role:**
Database-driven scheduled verification module for tariff consistency.

### `modules.run.mzfssnapshot.MZfssnapshot`

**Purpose:**
Automates ZFS snapshot creation and rotation.

**Dependencies:**

- shell access to `zfs` tools,
- `Channel`,
- `ZfsData`,
- `ZfsProcessor`,
- `MIntervals`,
- `Message`.

**Config API:**

- `volumes`
- `snapshot_interval`
- `max_snapshot_count`
- `min_free_space`
- `message_channel`
- `sleep_period`

**Related helper types:**

- `ZfsData` - parsed representation of ZFS command output,
- `ZfsProcessor` - volume-oriented snapshot workflow helper.

### `modules.run.memailtest.MEmailtest`

**Purpose:**
Development/test module for producing sample multipart e-mail messages.

**Config API:**

- `message_channel`
- `sleep_period`

### `modules.run.mtest.MTest`

**Purpose:**
Development/test module for periodic logging.

**Config API:**

- `sleep_period`

## Interface Contract For Modules

### `libs.interfaces.IRunModule` and `IComModule`

All runtime modules are expected to implement the following contract:

- `debug`
- `verbose`
- `module_conf`
- `_apply_config()`
- `run()`
- `sleep()`
- `stop()`
- `_stopped`
- `module_stopped`
- `template_module_name()`
- `template_module_variables()`

This interface is the current canonical runtime contract for both module types.

The package entry point `libs.interfaces` exposes these interfaces through lazy
exports, so package-level imports such as `from libs.interfaces import IRunModule`
do not load `libs.interfaces.modules` until the requested symbol is accessed.

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
- `ModuleConfigMixin`
- module configuration templates

### Internal But Important Boundary

The following elements are highly coupled to current implementation details, but
are still essential for understanding the existing business logic:

- thread-based module classes,
- SQLAlchemy model usage inside task modules,
- `LmsMysqlDatabase`,
- shell-based ICMP and ZFS utilities.

## Notes For The Upcoming Refactor

This API reference reflects the code as it exists today. It should be treated as
a baseline for documentation and refactoring, not as a claim that the current
surface is already cleanly separated into domain services.
