# Modules

There are two types of modules: communication modules and task modules.

## Communication modules

Each configured communication module is identified by a unique `channel` configuration variable, which defines the communication queue number. This number is the qualifier for selecting the communication method for the work modules.

1. [memailalert](https://github.com/Szumak75/AASd/blob/master/docs/MEmailAlert.md)

    Module intended for sending e-mail notifications.

## Task modules

The method of configuring task modules may vary depending on their purpose and is described in the module documentation and in the configuration file.
Variables common to most modules are:

- sleep_period [float]: which defines the length of the break between subsequent executions of module tasks,
- message_channel [list]: which defines a list of communication channels (if used by the module) with optional additional information about the frequency of sent notifications.

1. [micmp](https://github.com/Szumak75/AASd/blob/master/docs/MIcmp.md)

    A module designed to test the network reachability of a configured list of IPv4 addresses.

1. [mlmspayment](https://github.com/Szumak75/AASd/blob/master/docs/MLmsPayment.md)

    A module compatible with the LMS panel, designed to generate notifications about overdue customer payments and summary reports for the customer service office.

