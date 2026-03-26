# AASd v2

Autonomous Administrative System daemon version 2.

## Purpose

The main goal of the project is to create a modular platform supporting UNIX
system administration tasks in the field of monitoring environmental parameters
and process status as well as responding to incidents.

The active runtime is plugin-based and the daemon acts as a runtime host and
execution supervisor.

The repository still contains archived historical material from the former
module-oriented runtime, but that code is no longer part of the active
execution path.

The current architecture is plugin-based:

- plugins are discovered from the directory configured as `plugins_dir`,
- each plugin directory or symlink is one plugin instance,
- each instance gets its own config section derived from the entry name,
- plugin type is declared by the plugin API, not by directory category,
- worker plugins emit messages through the dispatcher,
- worker-side notification timing is handled by shared plugin helpers, not by the daemon,
- communication plugins consume routed messages from configured channels.

Standalone plugins may keep their own tests, changelog, and operational
documentation inside the mounted plugin repository. The local `plugins/email/`
repository is an example of that model.

The daemon must not assume direct plugin-to-plugin communication. Message
routing is valid only when the user defines matching channel rules in the
configuration file.

The legacy modules are preserved only as historical reference material under
`archive/`.

The project is entirely written in python3 and runs in a dedicated virtual environment.

The main process is executed in the foreground and it is assumed that it will be supervised by a service manager such as "**runit**" or "**daemontools**".

The project is dedicated and tested on FreeBSD platforms, most of the plugins should work properly in the Linux environment.

## Environment Policy

Poetry is used only in development environments for dependency management,
locking, testing, and documentation work.

Production and deployment environments should use `requirements.txt` as the
runtime installation source:

```bash
pip install -r requirements.txt
```

`requirements.txt` is treated as the deployment artifact generated from the
current Poetry runtime lock set.

At first startup, or after the daemon discovers new configuration sections or
options, AASd writes the missing defaults to the config file, logs an operator
review notice, and exits cleanly. Runtime startup resumes only after the
operator reviews the updated configuration and launches the daemon again.

During `load()` and `reload()`, the daemon also validates known plugin schedule
fields such as `message_channel` and `at_channel` and emits warning logs for
unsupported or suspicious values before plugin startup begins.

## Table of contents

1. [Installation](https://github.com/Szumak75/AASd/blob/master/docs/Installation.md)
1. [Archived Modules](https://github.com/Szumak75/AASd/blob/master/docs/Modules.md)
1. [Flow Diagram](https://github.com/Szumak75/AASd/blob/master/docs/Flow.md)
1. [Architecture Analysis](https://github.com/Szumak75/AASd/blob/master/docs/Architecture.md)
1. [Plugin API v1](https://github.com/Szumak75/AASd/blob/master/docs/PluginAPI.md)
1. [Plugin Migration Status](https://github.com/Szumak75/AASd/blob/master/docs/PluginMigration.md)
1. [Business Logic API](https://github.com/Szumak75/AASd/blob/master/docs/API.md)

## Documentation Build

The repository now includes a Sphinx-based documentation toolchain with MyST
Markdown support. This is a development workflow and assumes Poetry is
available in the local development environment.

```bash
make docs
```

Generated HTML output is written to `docs/_build/html/`.
