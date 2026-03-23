# mlmstariff

## Purpose

The module performs scheduled checks of tariff assignments on nodes using
LMS/MLMS-backed data. It is intended to detect database-side states that should
result in outbound notifications through configured communication channels.

In practice, this module is a database-driven verification task. It uses a
cron-like trigger schedule and emits messages only when configured checks are
due.

## Configuration section

```ini
[mlmstariff]
# LMS tariff and node checker module.
# Variables:
# 'at_channel' [List[str]], comma separated communication channels list
# ['nr1:at', 'nr2:at']
# where 'at' means the date/time generating notifications for the given channel
# 'at' format: semicolon-separated numeric list
# format: 'minute;hour;day-month;month;day-week'
# It is allowed to use '*' character, the '-' range separator and lists
# separated by '|' character as field values.
# All fields must be defined.
# 'message_channel' [List[str]] - message channels for notifications.
# 'sql_server' [List[str]] - list of SQL servers IP addresses.
# 'sql_database' [str] - name of LMS database.
# 'sql_user' [str] - username for database connection.
# 'sql_password' [str] - password for database connection.
at_channel = ['1:0;0;7|10|12|13;*;*', '1:0;8|12|16|21;14;*;*']
message_channel = [1]
sql_server = []
sql_database =
sql_user =
sql_password =
# -----<end of section: 'mlmstariff'>-----
```

## Runtime dependencies

- database connectivity through `LmsMysqlDatabase`,
- LMS/MLMS SQLAlchemy models,
- communication subsystem for outbound message delivery.
