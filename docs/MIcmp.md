# micmp

## Purpose

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
