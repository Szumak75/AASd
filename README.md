# AASd

Autonomous Administrative System daemon.

## Purpose

The main goal of the project is to create a modular platform supporting UNIX system administration tasks in the field of monitoring environmental parameters and process status as well as responding to incidents. However, due to the assumed architecture of the platform, there is a lot of freedom in creating the functionalities of working modules.

The platform integrates two types of modules: intended for communication with the platform user: **_modules.com_** and intended for performing tasks: **_modules.run_**.

Modules are loaded dynamically based on rules defined in the main section of the configuration file.

Each module is launched in a separate thread and is executed independently of the other modules of the platform, according to the rules specified in its configuration section.

The project is entirely written in python3 and runs in a dedicated virtual environment.

The main process is executed in the foreground and it is assumed that it will be supervised by a service manager such as "**runit**" or "**daemontools**".

The project is dedicated and tested on FreeBSD platforms, most of the modules should work properly in the Linux environment.

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

## Table of contents

1. [Installation](https://github.com/Szumak75/AASd/blob/master/docs/Installation.md)
1. [Modules](https://github.com/Szumak75/AASd/blob/master/docs/Modules.md)
1. [Flow Diagram](https://github.com/Szumak75/AASd/blob/master/docs/Flow.md)
1. [Architecture Analysis](https://github.com/Szumak75/AASd/blob/master/docs/Architecture.md)
1. [Business Logic API](https://github.com/Szumak75/AASd/blob/master/docs/API.md)

## Documentation Build

The repository now includes a Sphinx-based documentation toolchain with MyST
Markdown support. This is a development workflow and assumes Poetry is
available in the local development environment.

```bash
make docs
```

Generated HTML output is written to `docs/_build/html/`.
