# Architecture Analysis

**Scope:**
This document summarizes the current structure of the AASd codebase,
highlights the legacy runtime architecture still present in the repository, and
defines the architectural direction toward the plugin-only runtime model.

## Overview

AASd now exposes a plugin-based active runtime. The repository also preserves
an archived copy of the former module-based runtime for historical reference.

The active repository layout is organized into a small runtime core and a set
of plugin-oriented helpers:

- `aasd.py` is the process entry point.
- `server/daemon.py` contains the daemon orchestration logic.
- `libs/` contains shared runtime infrastructure, configuration helpers,
  communication objects, utility classes, and database connectors/models.
- `plugins/` contains active reference plugins for the new runtime model.
- `archive/modules/` contains archived outbound communication and worker plugins
  from the former runtime model.
- `tests/` contains a mixed set of regression and exploratory tests.

The active architecture is no longer based on `modules/com` and `modules/run`.
Those trees are now historical and already removed from the active runtime
path.

## Legacy Runtime Composition

### Process Entry

The daemon starts in [`aasd.py`](../aasd.py), switches the current working
directory to the repository root, constructs [`AASd`](../server/daemon.py), and
calls `run()`.

### Daemon Core

[`server/daemon.py`](../server/daemon.py) is the operational center of the
application. `AASd` is responsible for:

- creating the application identity object,
- configuring the logging engine and logging processor,
- loading and updating the configuration file,
- parsing command line arguments,
- creating the communication dispatcher,
- starting and stopping active plugin instances discovered from `plugins_dir`,
- reacting to `SIGTERM`, `SIGINT`, and `SIGHUP`.

The runtime model is thread-based. Each plugin instance runs independently in
its own runtime object and is supervised by the daemon.

## Core Infrastructure

### Application Identity

[`libs/app.py`](../libs/app.py) provides `AppName`, a small container exposing:

- application name,
- application version,
- host name.

This object is passed into runtime plugins and reused when building messages and
logs.

### Base Classes

[`libs/base/classes.py`](../libs/base/classes.py) contains the shared base layer.
The most important classes are:

- `ProjectClassMixin` for daemon-level objects,
- `PluginRuntimeMixin` for plugin implementations,
- `PluginConfigMixin` for typed access to shared config patterns,
- `LogsMixin`, `ComMixin`, `ConfigMixin`, `DebugMixin`, `VerboseMixin` for cross-cutting state.

This layer is the primary glue between `jsktoolbox` primitives and the project
runtime.

The package entry point [`libs/base/__init__.py`](../libs/base/__init__.py)
now exposes these symbols through lazy exports, so package-level imports such as
`from libs.base import PluginRuntimeMixin` do not load `libs.base.classes` until the
requested symbol is accessed.

The implementation file [`libs/base/classes.py`](../libs/base/classes.py) is
also normalized to the repository class-structure convention with explicit
section markers inside each class.

### Configuration Service

[`libs/conf.py`](../libs/conf.py) contains `AppConfig`, which acts as the
configuration service for the whole daemon. Its responsibilities include:

- locating the config file,
- loading and saving the config file,
- generating a default config when none exists,
- scanning available plugin instances in `plugins_dir`,
- collecting configuration schemas from plugin manifests,
- generating per-instance config sections for discovered plugins.

`AppConfig` is one of the most important runtime objects in the project because
it bridges file configuration, plugin discovery, and daemon startup.

### Messaging Subsystem

[`libs/com/message.py`](../libs/com/message.py) provides the internal
message-dispatching layer:

The implementation file is normalized to the repository class-structure
convention with explicit section markers inside each class.

- `Message` is the payload container passed from worker plugins to communication plugins,
- `Channel` handles interval-based notification schedules,
- `AtChannel` handles cron-like schedules,
- `ThDispatcher` routes messages from the shared queue to communication-plugin queues.

This subsystem is the key boundary between business events and outbound
delivery, and it is also the strongest candidate to remain in the future
plugin-based runtime.

### Utility Layer

The current business logic depends mainly on:

- [`libs/tools/datetool.py`](../libs/tools/datetool.py) for date formatting and interval parsing,
- [`libs/tools/icmp.py`](../libs/tools/icmp.py) for ICMP and traceroute shell wrappers,
- [`libs/templates/modules.py`](../libs/templates/modules.py) for internal config rendering helpers,
- [`libs/db_models/connectors.py`](../libs/db_models/connectors.py) for database connection pools.

## Archived Legacy Runtime

### Communication Modules

The former module-based runtime, its interfaces, and its business
implementations now live in the `archive/` tree and are no longer started by
the daemon. They remain available only as historical reference material.

## Target Plugin Architecture

The target architecture replaces module loading from repository paths with
plugin instance loading from the directory configured as `plugins_dir` in the
main daemon section.

Core rules:

- each direct child entry in `plugins_dir` is one plugin instance,
- normal directories and symbolic links are treated equally as instances,
- instance configuration section names are derived from entry names,
- plugin kind is declared by plugin API metadata, not by file system path,
- worker plugins emit messages through the dispatcher,
- communication plugins consume routed messages from dispatcher channels,
- message delivery depends only on explicit user configuration.

The target runtime should introduce:

- a plugin loader,
- a plugin registry,
- a plugin context object,
- a versioned plugin manifest,
- plugin lifecycle supervision,
- automatic per-instance config generation.

The target plugin entry-point convention is documented in
[`PluginAPI.md`](./PluginAPI.md).

## Data Access Layer

The project includes a large SQLAlchemy model tree under `libs/db_models/`.
This layer is important for persistence but should be treated as a schema and
integration layer, not as the primary business API.

The archived business logic implementations and future complex worker plugins depend directly on:

- `libs.db_models.connectors.LmsMysqlDatabase`,
- `libs.db_models.lms.*`,
- `libs.db_models.mlms.*`.

This means domain logic and data access are only partially separated at the
moment.

### API Boundary Decision

For documentation and refactoring purposes, the project should treat the
runtime layer as the public API and the ORM layer as internal infrastructure.

Public documentation surface:

- `server.daemon`
- `libs.app`
- `libs.keys`
- `libs.conf`
  The core runtime helper layer now follows the repository class-section layout
  for application identity, shared keys, and configuration services.
- `libs.base.classes`
- `libs.com.message`
- `libs.tools.*` used by runtime plugins
  The tools layer now follows the repository class-section layout for the
  datetime, interval, ICMP, and traceroute helpers.
- `libs.plugins.*`
- `libs.templates.schema`

Internal documentation surface:

- `libs.db_models.lms.*`
- `libs.db_models.mlms.*`
- `libs.db_models.base`
- `libs.db_models.connectors`

The ORM tree still needs docstrings and maintenance documentation, but it
should not be presented as the stable entry point for application behavior.

## Current Strengths

- Clear runtime split between daemon core, worker plugins, and communication plugins.
- Dynamic loading keeps deployment flexible and can be repurposed for the new
  plugin runtime.
- Shared message abstraction reduces direct coupling between producers and consumers.
- Configuration templates make default config generation practical.

## Current Structural Risks

- Business logic is concentrated inside thread classes, which mixes orchestration
  and domain behavior.
- The current runtime infers extension behavior from repository layout and file
  naming conventions.
- Module configuration classes are typed, but docstring quality and API
  descriptions are inconsistent.
- The database-backed worker implementations have direct knowledge of SQLAlchemy models and
  query details, which makes later refactoring harder.
- Existing Markdown documentation covers selected components but not the shared API surface.

## Migration Direction

The approved migration direction is:

1. Define and implement `Plugin API v1`.
2. Replace active module discovery with plugin discovery from `plugins_dir`.
3. Archive the legacy `modules.*` runtime tree and related loader logic.
4. Create new plugins from scratch against the new API.
5. Finalize the new runtime with two example plugins proving channel-based
   dispatch behavior.

## Recommended Documentation Strategy

Before and during the runtime rewrite, the safest documentation-first path is:

1. Document the target plugin contract before implementing the new loader.
2. Keep the legacy runtime documented only as historical architecture.
3. Document archive boundaries when the old runtime is removed from the active path.
4. Keep ORM models documented but outside the public plugin API reference.
5. Separate operational docs from API docs and from migration planning notes.

This document is intended to serve as the project-wide architectural baseline
for that work.
