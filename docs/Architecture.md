# Architecture Analysis

**Scope:**
This document summarizes the current structure of the AASd codebase and
highlights the runtime architecture used by the daemon and its modules.

## Overview

AASd is a threaded daemon built around dynamically loaded modules. The project
is organized into a small runtime core and a set of pluggable implementations:

- `aasd.py` is the process entry point.
- `server/daemon.py` contains the daemon orchestration logic.
- `libs/` contains shared runtime infrastructure, configuration helpers,
  communication objects, utility classes, and database connectors/models.
- `modules/com/` contains outbound communication modules.
- `modules/run/` contains business-task modules that perform checks, queries, or
  scheduled actions.
- `tests/` contains a mixed set of regression and exploratory tests.

## Runtime Composition

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
- starting and stopping `modules/com` and `modules/run`,
- reacting to `SIGTERM`, `SIGINT`, and `SIGHUP`.

The runtime model is thread-based. Each module runs independently in its own
thread and is supervised by the daemon.

## Core Infrastructure

### Application Identity

[`libs/app.py`](../libs/app.py) provides `AppName`, a small container exposing:

- application name,
- application version,
- host name.

This object is passed into runtime modules and reused when building messages and
logs.

### Base Classes

[`libs/base/classes.py`](../libs/base/classes.py) contains the shared base layer.
The most important classes are:

- `BProjectClass` for daemon-level objects,
- `BModule` for module implementations,
- `BModuleConfig` for typed access to module configuration,
- `BImporter` for dynamic module discovery and imports,
- `BLogs`, `BCom`, `BConfig`, `BDebug`, `BVerbose` for cross-cutting state.

This layer is the primary glue between `jsktoolbox` primitives and the project
runtime.

### Configuration Service

[`libs/conf.py`](../libs/conf.py) contains `AppConfig`, which acts as the
configuration service for the whole daemon. Its responsibilities include:

- locating the config file,
- loading and saving the config file,
- generating a default config when none exists,
- scanning available modules,
- collecting configuration templates from modules,
- returning enabled communication and task modules.

`AppConfig` is one of the most important runtime objects in the project because
it bridges file configuration, module discovery, and daemon startup.

### Messaging Subsystem

[`libs/com/message.py`](../libs/com/message.py) provides the internal
message-dispatching layer:

- `Message` is the payload container passed from task modules to communication modules,
- `Channel` handles interval-based notification schedules,
- `AtChannel` handles cron-like schedules,
- `ThDispatcher` routes messages from the shared queue to communication-module queues.

This subsystem is the key boundary between business events and outbound delivery.

### Utility Layer

The current business logic depends mainly on:

- [`libs/tools/datetool.py`](../libs/tools/datetool.py) for date formatting and interval parsing,
- [`libs/tools/icmp.py`](../libs/tools/icmp.py) for ICMP and traceroute shell wrappers,
- [`libs/templates/modules.py`](../libs/templates/modules.py) for module configuration templates,
- [`libs/db_models/connectors.py`](../libs/db_models/connectors.py) for database connection pools.

## Business Logic Modules

### Communication Modules

Communication modules are consumers of `Message` objects. Currently the project
contains:

- `memailalert` - primary SMTP e-mail sender,
- `memailalert2` - secondary SMTP e-mail sender with equivalent behavior.

These modules are delivery adapters rather than independent business workflows.

### Task Modules

Task modules are the main holders of business logic:

- `micmp` - detects host reachability changes and emits incident notifications,
- `mlmspayment` - queries LMS/MLMS data and builds payment reminders,
- `mlmstariff` - queries LMS/MLMS data and checks tariff assignments on nodes,
- `mzfssnapshot` - manages ZFS snapshot creation and rotation,
- `memailtest` - test helper for outbound message generation,
- `mtest` - logger-oriented development test module.

In practice, the business value of the project currently lives mostly in the
`modules/run/` package.

## Data Access Layer

The project includes a large SQLAlchemy model tree under `libs/db_models/`.
This layer is important for persistence but should be treated as a schema and
integration layer, not as the primary business API.

The business modules currently depend directly on:

- `libs.db_models.connectors.LmsMysqlDatabase`,
- `libs.db_models.lms.*`,
- `libs.db_models.mlms.*`.

This means domain logic and data access are only partially separated at the
moment.

## Current Strengths

- Clear runtime split between daemon core, task modules, and communication modules.
- Dynamic module loading keeps deployment flexible.
- Shared message abstraction reduces direct coupling between producers and consumers.
- Configuration templates make default config generation practical.

## Current Structural Risks

- Business logic is concentrated inside thread classes, which mixes orchestration
  and domain behavior.
- Module configuration classes are typed, but docstring quality and API
  descriptions are inconsistent.
- The database-backed modules have direct knowledge of SQLAlchemy models and
  query details, which makes later refactoring harder.
- There is no dedicated documentation generator configured in the repository.
- Existing Markdown documentation covers selected modules but not the shared API surface.

## Recommended Documentation Strategy

Before the planned refactoring, the safest documentation-first path is:

1. Normalize docstrings in the shared infrastructure and business modules.
2. Keep a curated Markdown API reference for the current public runtime surface.
3. Document runtime contracts before extracting services or refactoring modules.
4. Separate operational docs from API docs and from future architecture notes.

This document is intended to serve as the project-wide architectural baseline
for that work.
