# Architecture Analysis

**Scope:**
This document summarizes the current structure of the AASd codebase,
highlights the boundary between the active plugin runtime and archived legacy
material, and describes the current architectural priorities.

## Overview

AASd exposes a plugin-based active runtime. The repository also preserves an
archived copy of the former module-based runtime for historical reference.

The active repository layout is organized into a small runtime core and a set
of plugin-oriented helpers:

- `aasd.py` is the process entry point.
- `server/daemon.py` contains the daemon orchestration logic.
- `libs/` contains shared runtime infrastructure, configuration helpers,
  communication objects, utility classes, and plugin host services.
- `plugins/` contains active reference plugins for the new runtime model.
- `archive/modules/` contains archived outbound communication and worker plugins
  from the former runtime model.
- `archive/libs/db_models/` contains archived historical ORM definitions.
- `tests/` contains regression coverage for the active runtime and shared helpers.

The active architecture is no longer based on `modules/com` and `modules/run`.
Those trees are now historical and already removed from the active runtime
path.

## Active Runtime Composition

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
- checking `plugins_dir`,
- delegating plugin startup and shutdown to `PluginRegistryService`,
- reacting to `SIGTERM`, `SIGINT`, and `SIGHUP`.

The runtime model is thread-based. Each plugin instance runs independently in
its own runtime object and is supervised through the registry service.

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
- `PluginConfigMixin` for typed access to shared config patterns,
- `LogsMixin`, `ComMixin`, `ConfigHandlerMixin`, `ConfigSectionMixin`,
  `DebugMixin`, and `VerboseMixin` for cross-cutting state.

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
- reading plugin manifests and configuration schemas,
- generating per-instance config sections for discovered plugins.

`AppConfig` is one of the most important runtime objects in the project because
it bridges file configuration, plugin discovery, and daemon startup.

### Plugin Host Layer

[`libs/plugins.runtime`](../libs/plugins/runtime.py),
[`libs/plugins.loader`](../libs/plugins/loader.py),
[`libs/plugins.config`](../libs/plugins/config.py),
[`libs/plugins.keys`](../libs/plugins/keys.py), and
[`libs/plugins.service`](../libs/plugins/service.py) define the active plugin
host model:

- `PluginSpec` describes one plugin implementation,
- `PluginContext` provides daemon-owned services to plugin factories,
- `PluginLoader` discovers plugin instances from `plugins_dir`,
- `PluginConfigParser` validates and parses plugin config sections,
- `PluginRegistryService` initializes, starts, and stops runtimes,
- `PluginServiceReport` records initialized, started, failed, and skipped instances.

The current supervision defaults are intentionally conservative:

- restart policy is `none`,
- health policy is `transitions_only`.

### Messaging Subsystem

[`libs/com/message.py`](../libs/com/message.py) provides the internal
message-dispatching layer:

The implementation file is normalized to the repository class-structure
convention with explicit section markers inside each class.
Class-local `BData` storage keys are scoped to private `__Keys` helpers inside
their owning classes, while the module-level `_Keys` container keeps only the
shared channel-mapping key used across schedulers.

- `Message` is the payload container passed from worker plugins to communication plugins,
- `Channel` handles interval-based notification schedules,
- `AtChannel` handles cron-like schedules,
- `NotificationScheduler` combines worker-facing interval and cron-like rules,
- `ThDispatcher` routes messages from the shared queue to communication-plugin queues.

This subsystem is the key boundary between business events and outbound
delivery, and it is the established exchange layer of the current plugin-based
runtime.

### Utility Layer

The current business logic depends mainly on:

- [`libs/tools/datetool.py`](../libs/tools/datetool.py) for date formatting and interval parsing,
- [`libs/tools/icmp.py`](../libs/tools/icmp.py) for ICMP and traceroute shell wrappers,
- [`libs/templates/schema.py`](../libs/templates/schema.py) for schema-based plugin configuration descriptors,
- [`libs/templates/modules.py`](../libs/templates/modules.py) for internal config rendering helpers.

## Archived Legacy Runtime

### Communication Modules

The former module-based runtime, its interfaces, and its business
implementations now live in the `archive/` tree and are no longer started by
the daemon. They remain available only as historical reference material.

## Active Plugin Architecture

The active architecture loads plugin instances from the directory configured as
`plugins_dir` in the main daemon section.

Core rules:

- each direct child entry in `plugins_dir` is one plugin instance,
- normal directories and symbolic links are treated equally as instances,
- instance configuration section names are derived from entry names,
- plugin kind is declared by plugin API metadata, not by file system path,
- worker plugins emit messages through the dispatcher,
- communication plugins consume routed messages from dispatcher channels,
- message delivery depends only on explicit user configuration.

This runtime already includes:

- a plugin loader,
- a registry service,
- a plugin context object,
- a versioned plugin manifest,
- plugin lifecycle supervision,
- automatic per-instance config generation.

The plugin entry-point convention is documented in
[`PluginAPI.md`](./PluginAPI.md).

## Data Access Layer

The historical SQLAlchemy model tree has been moved to `archive/libs/db_models/`.
It is preserved for reference only and is not part of the active runtime or
supported plugin API.

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

There is no active ORM documentation surface in the runtime API. Archived data
models remain reference material only.

## Current Strengths

- Clear runtime split between daemon core, worker plugins, and communication plugins.
- Dynamic loading keeps deployment flexible and supports instance-based plugin deployment.
- Shared message abstraction reduces direct coupling between producers and consumers.
- Schema-based configuration keeps generated config sections aligned with plugin manifests.
- The active plugin runtime has regression coverage for discovery, config parsing, lifecycle handling, and startup order.

## Current Structural Risks

- Business logic is concentrated inside thread classes, which mixes orchestration
  and domain behavior.
- Supervision policy is still intentionally minimal and not yet configurable.
- The plugin-host public API is broader in documentation than it is stabilized in code.
- Some documentation still needs periodic cleanup to avoid mixing historical and active concepts.

## Current Direction

The current architectural direction is no longer migration to plugins; that
migration is already in place. The next steps are:

1. harden plugin supervision and diagnostics,
2. stabilize the daemon-to-plugin host API,
3. tighten configuration and registration validation,
4. continue reducing exposure of historical helper layers,
5. keep `archive/` strictly outside the active runtime path.
