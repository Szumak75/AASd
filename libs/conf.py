# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 07.11.2023

  Purpose: configuration package
"""

from inspect import currentframe
from typing import Dict, Optional, List, Any

from jsktoolbox.attribtool import ReadOnlyClass
from jsktoolbox.raisetool import Raise
from jsktoolbox.logstool.logs import LoggerClient, LoggerQueue
from jsktoolbox.configtool.main import Config as ConfigTool
from jsktoolbox.stringtool.crypto import SimpleCrypto
from .base.classes import BLogs, BModuleConfig
from .interfaces.conf import IModuleConfig


class _Keys(object, metaclass=ReadOnlyClass):
    """Private Keys definition class.

    For internal purpose only.
    """

    CF = "__cf__"
    DEBUG = "__DEBUG__"
    FCONF = "__FCONF__"
    MAIN = "__MAIN__"
    NAME = "__NAME__"
    MODULES = "__MODULES__"
    MODCONF = "__MODULE_CONF__"
    VERSION = "__VERSION__"
    VERBOSE = "__VERBOSE__"
    MC_DEBUG = "debug"
    MC_MODULES = "modules"
    MC_SALT = "salt"


class _ModuleConf(IModuleConfig, BModuleConfig):
    """Module Config private class."""

    def _get(self, varname: str) -> Any:
        """Get variable from config."""
        return self._cfh.get(self._section, varname)

    @property
    def debug(self) -> bool:
        """Return debug var."""
        return self._get(_Keys.MC_DEBUG)

    @property
    def modules(self) -> List[str]:
        """Return modules list."""
        return self._get(_Keys.MC_MODULES)

    @property
    def salt(self) -> int:
        """Return salt var."""
        return self._get(_Keys.MC_SALT)


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
        self._data[_Keys.MODCONF] = None
        # configfile main section name
        self.__name = app_name
        # config file handler
        self._data[_Keys.CF] = None

        # constructor complete
        self.logs.message_info = "... complete"

    def load(self) -> bool:
        """Try to load config file."""
        if self.cf is None:
            self.cf = ConfigTool(self.config_file, self.__name)
            self._data[_Keys.MODCONF] = _ModuleConf(self.cf, self.__name)
            if not self.cf.file_exists:
                self.logs.message_warning = (
                    f"Config file '{self.config_file}' not exist."
                )
                self.logs.message_warning = "Try to create default one."
                if not self.__create_config_file():
                    return False
        try:
            if self.debug:
                self.logs.message_debug = (
                    f"Try to load config file: '{self.config_file}'..."
                )
            out = self.cf.load()
            if out:
                if self.debug:
                    self.logs.message_debug = (
                        "Config file loaded successful."
                    )
            return out
        except Exception as ex:
            self.logs.message_critical = (
                f"Cannot load config file: '{self.config_file}'."
            )
            if self.debug:
                self.logs.message_debug = f"{ex}"

    def save(self) -> bool:
        """Try to save config file."""

    def reload(self) -> bool:
        """Try to reload config file."""
        self.cf = None
        return self.load()

    def __create_config_file(self) -> bool:
        """Try to create config file."""
        # main section
        self.cf.set(self.__name, desc=f"{self.__name} configuration file")
        self.cf.set(self.__name, desc="[ communication modules ]:")
        self.cf.set(self.__name, desc="[ running modules ]:")
        self.cf.set(
            self.__name,
            varname=_Keys.MC_MODULES,
            value=[],
            desc="list of modules to activate",
        )
        self.cf.set(self.__name, varname=_Keys.MC_DEBUG, value=False)
        self.cf.set(
            self.__name,
            varname=_Keys.MC_SALT,
            value=SimpleCrypto.salt_generator(6),
            desc="salt for passwords encode/decode",
        )

        # modules section
        # TODO: write modules and config generator

        try:
            return self.cf.save()
        except Exception as ex:
            self.logs.message_critical = (
                f"Cannot create config file: '{self.config_file}'."
            )
            if self.debug:
                self.logs.message_debug = f"{ex}"
            return False

    @property
    def cf(self) -> Optional[ConfigTool]:
        """Return config file handler."""
        if _Keys.CF not in self._data:
            self._data[_Keys.CF] = None
        return self._data[_Keys.CF]

    @cf.setter
    def cf(self, cf: ConfigTool) -> None:
        """Set config file handler."""
        if not isinstance(cf, ConfigTool):
            raise Raise.error(
                f"ConfigTool type expected, '{type(cf)}' received.",
                TypeError,
                self.c_name,
                currentframe(),
            )
        self._data[_Keys.CF] = cf

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
        if self.cf:
            if self.cf.get(self.__name, "debug"):
                return True
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
    def module_conf(self) -> Optional[_ModuleConf]:
        """Return module conf object."""
        return self._data[_Keys.MODCONF]

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
