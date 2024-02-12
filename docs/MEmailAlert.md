# memailalert

## Purpose

Module intended for sending e-mail notifications. There are two copies of this module with identical functionality: `memailalert` and `memailalert2`, thanks to which it is possible to create an alternative configuration of notification channels.

## Configuration section

```
[memailalert]
# Email alert configuration module.
# Variables:
# channel [int] - unique channel for communication method (default: 1)
# smtp_server [str] - server for outgoing emails.
# smtp_user [str] - smtp auth user for sending emails.
# smtp_pass [str] - smtp auth password for sending emails.
# address_from [str] - email from address, for example: 'no-reply@ltd',
# can be overridden by properties of the Message class if set.
# address_to [list] - destination list of emails,
# can be overridden by properties of the Message class if set.
channel = 1
smtp_server = 
smtp_user = 
smtp_pass = 
address_from = 
address_to = []
# -----<end of section: 'memailalert'>-----
```
