# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 07.11.2023

  Purpose: configuration package
"""

from inspect import currentframe
from typing import Dict, Optional

from jsktoolbox.attribtool import NoDynamicAttributes
from jsktoolbox.raisetool import Raise
from jsktoolbox.logstool.logs import LoggerClient, LoggerQueue
from jsktoolbox.configtool.main import Config as ConfigTool
from .base.classes import BLogs


class _Keys(NoDynamicAttributes):
    """Private Keys definition class.

    For internal purpose only.
    """

    @classmethod
    @property
    def DEBUG(cls) -> str:
        """Return DEBUG Key."""
        return "__DEBUG__"

    @classmethod
    @property
    def FCONF(cls) -> str:
        """Return FCONF Key."""
        return "__FCONF__"

    @classmethod
    @property
    def MAIN(cls) -> str:
        """Return MAIN Key."""
        return "__MAIN__"

    @classmethod
    @property
    def NAME(cls) -> str:
        """Return NAME Key."""
        return "__NAME__"

    @classmethod
    @property
    def MODULES(cls) -> str:
        """Return MODULES Key."""
        return "__MODULES__"

    @classmethod
    @property
    def VERSION(cls) -> str:
        """Return VERSION Key."""
        return "__VERSION__"

    @classmethod
    @property
    def VERBOSE(cls) -> str:
        """Return VERBOSE Key."""
        return "__VERBOSE__"


class Config(BLogs):
    """Configuration containet class."""

    def __init__(self, queue: LoggerQueue, app_name: str) -> None:
        """Constructor."""
        # class logger client
        self.logs = LoggerClient(queue=queue, name=self.c_name)

        self.logs.message_info = "Config initialization..."
        # initialization data structure
        self._data[_Keys.MAIN] = {}
        self._data[_Keys.MODULES] = {}
        # configfile main section name
        self.__name = app_name

        # constructor complete
        self.logs.message_info = "... complete"

    def load(self) -> bool:
        """Try to load config file."""

    def save(self) -> bool:
        """Try to save config file."""

    def reload(self) -> bool:
        """Try to reload config file."""

    @property
    def __main(self) -> Dict:
        """Return MAIN dict."""
        return self._data[_Keys.MAIN]

    @property
    def __modules(self) -> Dict:
        """Return MODULES dict."""
        return self._data[_Keys.MODULES]

    @property
    def __name(self) -> str:
        """Return app_name string."""
        if _Keys.NAME not in self.__main:
            self.__main[_Keys.NAME] = None
        return self.__main[_Keys.NAME]

    @__name.setter
    def __name(self, value: str) -> None:
        """Set app_name string."""
        if not isinstance(value, str):
            raise Raise.error(
                f"String type expected, '{type(value)}' received.",
                TypeError,
                self.c_name,
                currentframe(),
            )
        self.__main[_Keys.NAME] = value

    @property
    def config_file(self) -> Optional[str]:
        """Return config_file path string."""
        if _Keys.FCONF not in self.__main:
            self.__main[_Keys.FCONF] = None
        return self.__main[_Keys.FCONF]

    @config_file.setter
    def config_file(self, value: str) -> None:
        """Set config_file path string."""
        if not isinstance(value, str):
            raise Raise.error(
                f"String type expected, '{type(value)}' received.",
                TypeError,
                self.c_name,
                currentframe(),
            )
        self.__main[_Keys.FCONF] = value

    @property
    def debug(self) -> bool:
        """Return debug flag."""
        if _Keys.DEBUG not in self.__main:
            self.__main[_Keys.DEBUG] = False
        return self.__main[_Keys.DEBUG]

    @debug.setter
    def debug(self, value: bool) -> None:
        """Set debug flag."""
        if not isinstance(value, bool):
            raise Raise.error(
                f"Boolean type expected, '{type(value)}' received.",
                TypeError,
                self.c_name,
                currentframe(),
            )
        self.__main[_Keys.DEBUG] = value

    @property
    def verbose(self) -> bool:
        """Return verbose flag."""
        if _Keys.VERBOSE not in self.__main:
            self.__main[_Keys.VERBOSE] = False
        return self.__main[_Keys.VERBOSE]

    @verbose.setter
    def verbose(self, value: bool) -> None:
        """Set verbose flag."""
        if not isinstance(value, bool):
            raise Raise.error(
                f"Boolean type expected, '{type(value)}' received.",
                TypeError,
                self.c_name,
                currentframe(),
            )
        self.__main[_Keys.VERBOSE] = value

    @property
    def version(self) -> Optional[str]:
        """Return version string."""
        if _Keys.VERSION not in self.__main:
            self.__main[_Keys.VERSION] = None
        return self.__main[_Keys.VERSION]

    @version.setter
    def version(self, value: str) -> None:
        """Set version string."""
        if not isinstance(value, str):
            raise Raise.error(
                f"String type expected, '{type(value)}' received.",
                TypeError,
                self.c_name,
                currentframe(),
            )
        self.__main[_Keys.VERSION] = value


# #[EOF]#######################################################################
