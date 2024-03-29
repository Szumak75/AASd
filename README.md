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

## Table of contents

1. [Installation](https://github.com/Szumak75/AASd/blob/master/docs/Installation.md)
1. [Modules](https://github.com/Szumak75/AASd/blob/master/docs/Modules.md)
1. [Flow Diagram](https://github.com/Szumak75/AASd/blob/master/docs/Flow.md)
