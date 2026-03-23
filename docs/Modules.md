# Modules

This document describes the legacy module model that still exists in the
repository but is no longer the target runtime architecture.

The future runtime will use plugins loaded from `plugins_dir`. See
[PluginAPI](./PluginAPI.md) for the target extension model.

## Legacy Types

The historical runtime contains two legacy module types:

- communication modules,
- task modules.

## Legacy Communication Modules

Each configured communication module is identified by a unique `channel`
configuration variable, which defines the communication queue number. This
number is the qualifier for selecting the communication method for the legacy
work modules.

1. [memailalert](https://github.com/Szumak75/AASd/blob/master/docs/MEmailAlert.md)

   Legacy module intended for sending e-mail notifications.

## Legacy Task Modules

The method of configuring legacy task modules may vary depending on their
purpose and is described in the module documentation and in the configuration
file. Variables common to most legacy modules are:

- `sleep_period` [float]: which defines the length of the break between subsequent executions of module tasks,
- `message_channel` [list]: which defines a list of communication channels (if used by the module) with optional additional information about the frequency of sent notifications.

1. [micmp](https://github.com/Szumak75/AASd/blob/master/docs/MIcmp.md)

   A legacy module designed to test the network reachability of a configured list of IPv4 addresses.

1. [mlmspayment](https://github.com/Szumak75/AASd/blob/master/docs/MLmsPayment.md)

   A legacy module compatible with the LMS panel, designed to generate notifications about overdue customer payments and summary reports for the customer service office.

1. [mlmstariff](https://github.com/Szumak75/AASd/blob/master/docs/MLmsTariff.md)

   A legacy module compatible with LMS/MLMS data models, designed to inspect tariff assignments on nodes and emit scheduled notifications based on database state.

1. [mzfssnapshot](https://github.com/Szumak75/AASd/blob/master/docs/MZfsSnapshot.md)

   A legacy module designed to create and rotate snapshots of the ZFS file system.
