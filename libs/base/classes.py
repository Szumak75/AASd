# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 06.11.2023

  Purpose:
"""

from inspect import currentframe
from typing import Optional

from jsktoolbox.attribtool import NoDynamicAttributes
from jsktoolbox.raisetool import Raise
from jsktoolbox.libs.base_data import BData
from jsktoolbox.logstool.logs import LoggerClient

from libs.keys import Keys


class BClasses(BData, NoDynamicAttributes):
    """Base class for project."""

    @property
    def c_name(self) -> str:
        """Return class name."""
        return self.__class__.__name__

    @property
    def f_name(self) -> str:
        """Return current method name."""
        frame = currentframe().f_back
        method_name = frame.f_code.co_name
        return method_name

    @property
    def logs(self) -> Optional[LoggerClient]:
        """Return LoggerClient object or None."""
        if Keys.CLOG not in self._data:
            self._data[Keys.CLOG] = None
        return self._data[Keys.CLOG]

    @logs.setter
    def logs(self, logs: LoggerClient) -> None:
        """Set LoggerClient."""
        if not isinstance(logs, LoggerClient):
            raise Raise.error(
                f"LoggerClient type expected, '{type(logs)}' received.",
                TypeError,
                self.c_name,
                currentframe(),
            )
        self._data[Keys.CLOG] = logs


# #[EOF]#######################################################################
