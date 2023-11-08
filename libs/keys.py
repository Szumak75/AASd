# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 06.11.2023

  Purpose:
"""

from jsktoolbox.attribtool import ReadOnlyClass


class Keys(object, metaclass=ReadOnlyClass):
    """Keys definition class.

    For internal purpose only.
    """

    CFH = "__config_handler__"
    CLOG = "__clog__"
    CONF = "__configuration_object__"
    DEBUG = "__debug__"
    HUP = "__hup_variable__"
    LOOP = "__loop__"
    PROC_LOGS = "__proc_logs__"
    QCOM = "__coms_queue__"
    SECTION = "__section_name__"
    VERBOSE = "__verbose__"


# #[EOF]#######################################################################
