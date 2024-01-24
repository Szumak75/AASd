# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 06.11.2023

  Purpose: Public keys container class definition.
"""

from jsktoolbox.attribtool import ReadOnlyClass


class Keys(object, metaclass=ReadOnlyClass):
    """Keys definition class.

    For internal purpose only.
    """

    CFH: str = "__config_handler__"
    CLOG: str = "__clog__"
    CONF: str = "__configuration_object__"
    DEBUG: str = "__debug__"
    HUP: str = "__hup_variable__"
    LOOP: str = "__loop__"
    PROC_LOGS: str = "__proc_logs__"
    QCOM: str = "__coms_queue__"
    SECTION: str = "__section_name__"
    VERBOSE: str = "__verbose__"


# #[EOF]#######################################################################
