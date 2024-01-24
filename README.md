# AASd

Autonomous Administrative System daemon.

## Purpose

The main goal of the project is to create a modular platform supporting UNIX system administration tasks in the field of monitoring environmental parameters and process status as well as responding to incidents. However, due to the assumed architecture of the platform, there is a lot of freedom in creating the functionalities of working modules.

The platform integrates two types of modules: intended for communication with the platform user: 'modules.com' and intended for performing tasks: 'modules.run'.

Modules are loaded dynamically based on rules defined in the main section of the configuration file.

Each module is launched in a separate thread and is executed independently of the other modules of the platform, according to the rules specified in its configuration section.

## Flow diagram

```mermaid
flowchart TB
    subgraph daemon
    A1[main\nprocess]-->A2[logger\nengine]
    LQ[logger\nqueue]<-->A2
    A1-->A3[logger\nclient]
    A3-->LQ
    A1-->CONF[configuration\nservice]
    A1-->A5[communication\ndispatcher]
    A5<-->CQ[communication\nqueues]
    A5-->A7[logger\nclient]
    A7-->LQ
    end
    A1-->com
    A1-->run
    subgraph com [communication modules]
    C1[module 1]-->C2[logger\nclient]
    CONF-->C1
    C2-->LQ
    CQ-->C1
    end
    subgraph run [running modules]
    R1[module 1]-->R2[logger\nclient]
    CONF-->R1
    R2-->LQ
    R1-->CQ
    end

```
