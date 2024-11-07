# mzfssnapshot

## Purpose

This module provides a simple way to create and rotate ZFS snapshots. 
Is dedicated and tested on the FreeBSD system.

At intervals specified by the optional `sleep_period` parameter (default: 5 seconds), the module checks whether the procedure startup time specified by the `snapshot_interval` parameter has been reached.

After this condition is met, the file system usage level is checked for each volume from the `volumes` list.

If the amount of free space is greater than the value of the `min_free_space` parameter, a new snapshot is created, and all older snapshots exceeding the value of the `max_snapshot_count` parameter are deleted.

If the amount of free space is less than or equal to the value of the `min_free_space` parameter, a warning message is generated and sent to the communication channel specified by the `message_channel` parameter according to the conditions specified for this channel.

The snapshot name is created according to the scheme: `%Y%m%d%H%M%S`.

## Configuration section

```
[mzfssnapshot]
# ZFS Snapshot automation configuration module.
# Variables:
# 'volumes' [List[str]] - List of ZFS volumes to monitor,
# for example:  ['tank/volume1', 'tank/volume2'].
# 'snapshot_interval' [str] - how often to take the snapshot,
# this is an integer representing 'seconds' or a numerical value with the suffix 's|m|h|d|w'.
# 'max_snapshot_count' [int] - maximum number of snapshots for rotation procedure.
# 'min_free_space' [int] - minimum percentage of free space needed to trigger a snapshot.
# After exceeding the above occupancy, a warning message will be generated
# if a communication channel has been configured for the module.
# 'message_channel' [List[str]], comma separated communication channels list,
# ['nr(:default delay=0)'|'nr1:delay', 'nr2:delay']
# where 'delay' means the time between generating
# subsequent notifications for a given channel and can be given in
# seconds or a numerical value with the suffix 's|m|h|d|w'
# Optional variables:
# 'sleep_period' [float], which determines the length of the break
# between subsequent executions of the program's main loop
message_channel = ['1']
volumes = [] # [List[str]]
max_snapshot_count = 24 # [int]
snapshot_interval = "1h" # [int|str]
min_free_space = 20 # [int]
```

## Example configuration

To create daily snapshots every 5 minutes for the `tank/data` volume, use the configuration as below:

```
[mzfssnapshot]
message_channel = ['1']
volumes = ['tank/data'] 
max_snapshot_count = 288
snapshot_interval = "5m" 
min_free_space = 20 
```
