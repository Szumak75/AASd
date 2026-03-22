# -*- coding: UTF-8 -*-
"""
Shared runtime key definitions.

Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 2023-11-06

Purpose: Define shared public key names used across internal data containers.
"""

from jsktoolbox.attribtool import ReadOnlyClass


class Keys(object, metaclass=ReadOnlyClass):
    """Expose shared public key names for internal storage containers."""

    APP_NAME: str = "__app_name__"
    CFH: str = "__config_handler__"
    CLOG: str = "__clog__"
    CONF: str = "__configuration_object__"
    DEBUG: str = "__debug__"
    HUP: str = "__hup_variable__"
    LOOP: str = "__loop__"
    PROC_LOGS: str = "__proc_logs__"
    QCOM: str = "__comms_queue__"
    SECTION: str = "__section_name__"
    VERBOSE: str = "__verbose__"


# #[EOF]#######################################################################
