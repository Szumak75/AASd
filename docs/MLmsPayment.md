# mlmspayment

## Purpose

## Configuration section

```
[mlmspayment]
# LMS payment notification module.
# Variables:
# 'at_channel' [List[str]], comma separated communication channels list ['nr1:at', 'nr2:at']
#  where 'at' means the date/time generating notifications for given channel
#  'at' format: semicolon-separated numeric list
#  format: 'minute;hour;day-month;month;day-week'
#  It is allowed to use '*' character, the '-' range separator and lists separated
#  by '|' character as field values.
#  All fields must be defined.
# 'diagnostic_channel' [List[str]] - diagnostic channels for sending statistics.
# 'message_channel' [List[str]] - message channels for notifications sent to customers.
# 'skip_group_id' [List[int]] - list of lms group ids to skip.
# 'sql_server' [List[str]] - list of SQL servers IP addresses
# 'sql_database' [str] - name of lms database.
# 'sql_user' [str] - username for database connection.
# 'sql_password' [str] - password for database connection.
# 'payment_message' [list] - list of days from the payment expiration
# in which notifications are to be sent to the customer.
# 'lms_url' [str] - URL to customer information panel,
# usually: 'https://domain_name/?m=customerinfo&id='
# 'user_url' [str] - URL to individual customer panel,
at_channel = ['1:0;0;7|10|12|13;*;*', '1:0;8|12|16|21;14;*;*']
diagnostic_channel = []
message_channel = [1]
payment_message = [] # days of sending the notification after the due date
default_paytime = 7 # [int] - default payment date as the number of days from invoice issuance
cutoff_time = 14 # [int] - number of days after default_paytime after which the service will be disabled
skip_group_id = [] # List[int] - lms group ids
sql_server = []
sql_database = 
sql_user = 
sql_password = 
lms_url = ""
user_url = ""
message_footer = [] # List[str] - personal footer added to the email.
# -----<end of section: 'mlmspayment'>-----
```
