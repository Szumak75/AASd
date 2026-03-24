# Modules

This document describes the legacy module model that has been archived and is
no longer part of the active runtime architecture.

The active runtime now uses plugins loaded from `plugins_dir`. See
[PluginAPI](./PluginAPI.md) for the current extension model.

## Legacy Types

The historical runtime contained two legacy component types:

- communication modules,
- task modules.

## Legacy Communication Modules

Each configured communication module was identified by a unique `channel`
configuration variable, which defines the communication queue number. This
number selected the delivery path for legacy worker logic.

1. `memailalert`

   Legacy module intended for sending e-mail notifications. Source and
   historical documentation were moved to the `archive/` tree.

## Legacy Task Modules

The method of configuring legacy task modules varied depending on their
purpose and was described in the module documentation and in the configuration
file. Variables common to most legacy modules were:

- `sleep_period` [float]: which defines the length of the break between subsequent executions of module tasks,
- `message_channel` [list]: which defines a list of communication channels (if used by the module) with optional additional information about the frequency of sent notifications.

1. `micmp`

   A legacy module designed to test the network reachability of a configured
   list of IPv4 addresses.

1. `mlmspayment`

   A legacy module compatible with the LMS panel, designed to generate
   notifications about overdue customer payments and summary reports for the
   customer service office.

1. `mlmstariff`

   A legacy module compatible with LMS/MLMS data models, designed to inspect
   tariff assignments on nodes and emit scheduled notifications based on
   database state.

1. `mzfssnapshot`

   A legacy module designed to create and rotate snapshots of the ZFS file
   system.

## Current Status

These historical modules are not loaded by the daemon anymore. The active
runtime model is:

- plugin instance discovery from `plugins_dir`,
- one config section per discovered plugin instance,
- worker plugins publishing messages through the dispatcher,
- communication plugins consuming messages from configured channels,
- explicit routing rules defined by the user in the configuration file.

The archived module list remains useful only as reference material for old
deployments and migration history.
