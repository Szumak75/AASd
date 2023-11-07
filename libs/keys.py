# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 06.11.2023

  Purpose:
"""

from jsktoolbox.attribtool import NoDynamicAttributes


class Keys(NoDynamicAttributes):
    """Keys definition class.

    For internal purpose only.
    """

    @classmethod
    @property
    def CLOG(cls) -> str:
        """Return CLOG Key."""
        return "__clog__"

    @classmethod
    @property
    def CONF(cls) -> str:
        """Return CONF Key."""
        return "__configuration_object__"

    @classmethod
    @property
    def HUP(cls) -> str:
        """Return HUP Key."""
        return "__hup_variable__"

    @classmethod
    @property
    def LOOP(cls) -> str:
        """Return LOOP Key."""
        return "__loop__"

    @classmethod
    @property
    def PROC_LOGS(cls) -> str:
        """Return PROC_LOGS Key."""
        return "__proc_logs__"


# #[EOF]#######################################################################
