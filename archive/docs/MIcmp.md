# micmp

## Purpose

At intervals specified by `sleep_period`, the module checks the network availability of IPv4 addresses from the `hosts` list.

If there is no response, a notification is generated with information about the time of the event for the appropriate IP address.

If the event persists longer than the `delay` value specified in the `message_channel` variable, another message will be generated informing that the event is still ongoing.

After restoring communication with the address to which the recorded event concerned, a message is generated informing about the end of the event and its duration.

## Configuration section

```
[micmp]
# ICMP configuration for module.
# 'sleep_period' [float], which determines the length of the break
# between subsequent executions of the program's main loop
# 'message_channel' [List[str]], comma separated communication channels list,
# ['nr(:default delay=0)'|'nr1:delay', 'nr2:delay']
# where 'delay' means the time between generating
# subsequent notifications for a given channel and can be given in
# seconds or a numerical value with the suffix 's|m|h|d|w'
# 'hosts' [List[str]], list of hosts IP addresses for reachability test
sleep_period = 15 # [second]
message_channel = ['1:30m']
hosts = []
# -----<end of section: 'micmp'>-----
```
