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
from .base.classes import (
    BLogs,
    BConfigSection,
    BConfigHandler,
    BModuleConfig,
    BImporter,
)
from .interfaces.conf import IModuleConfig
from .interfaces.modules import IComModule, IRunModule
from .templates.modules import TemplateConfigItem


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


class Config(BLogs, BConfigHandler, BConfigSection, BImporter):
    """Configuration containet class."""

    def __init__(self, qlog: LoggerQueue, app_name: str) -> None:
        """Constructor."""
        # class logger client
        self.logs = LoggerClient(queue=qlog, name=self.c_name)

        self.logs.message_info = "Config initialization..."
        # initialization data structure
        self._data[_Keys.MAIN] = dict()
        self._data[_Keys.MODULES] = dict()
        # self.module_conf
        self._data[_Keys.MODCONF] = None
        # configfile main section name
        self._section = app_name
        # config file handler
        self._data[_Keys.CF] = None

        # constructor complete
        self.logs.message_info = "... complete"

    def load(self) -> bool:
        """Try to load config file."""
        if self._cfh is None:
            self._cfh = ConfigTool(self.config_file, self._section)
            self._data[_Keys.MODCONF] = _ModuleConf(self._cfh, self._section)
            if not self._cfh.file_exists:
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
            out = self._cfh.load()
            # TODO: process config file
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
        if self._cfh:
            if self._cfh.save():
                if self.debug:
                    self.logs.message_debug = "Config file saved successful."
                return True
            else:
                self.logs.message_critical = (
                    f"Cannot save config file: '{self.config_file}'."
                )
        return False

    def reload(self) -> bool:
        """Try to reload config file."""
        self._cfh = None
        return self.load()

    def __create_config_file(self) -> bool:
        """Try to create config file."""
        # main section
        com_mods = list()
        run_mods = list()
        # set header file
        self._cfh.set(
            self._section, desc=f"{self._section} configuration file"
        )
        # generate description for communication modules
        self._cfh.set(self._section, desc="[ communication modules ]:")
        com_mods = self.import_name_list("modules.com")
        for item in com_mods:
            self._cfh.set(self._section, desc=f"{item}")
        self._cfh.set(self._section, desc="##")
        # generate description for running modules
        self._cfh.set(self._section, desc="[ running modules ]:")
        run_mods = self.import_name_list("modules.run")
        for item in run_mods:
            self._cfh.set(self._section, desc=f"{item}")
        self._cfh.set(self._section, desc="##")
        # add configuration variable for list of modules
        self._cfh.set(
            self._section,
            varname=_Keys.MC_MODULES,
            value=[],
            desc="list of modules to activate",
        )
        # add debug variable
        self._cfh.set(self._section, varname=_Keys.MC_DEBUG, value=False)
        # add salt variable
        self._cfh.set(
            self._section,
            varname=_Keys.MC_SALT,
            value=SimpleCrypto.salt_generator(6),
            desc="salt for passwords encode/decode",
        )

        # modules section
        # comunication modules
        if self.debug:
            self.logs.message_debug = (
                f"Found communication modules list: {com_mods}"
            )
        if com_mods:
            for name in com_mods:
                mod: IComModule = self.import_module("modules.com", name)
                if mod:
                    for item in mod.template_module_variables():
                        tci: TemplateConfigItem = item
                        self._cfh.set(
                            name,
                            varname=tci.varname,
                            value=tci.value,
                            desc=tci.desc,
                        )
                else:
                    self.logs.message_error = (
                        f"Cannot load module: modules.com.'{name}'"
                    )
        # running modules
        if self.debug:
            self.logs.message_debug = (
                f"Found running modules list: {run_mods}"
            )
            if run_mods:
                for name in run_mods:
                    mod: IComModule = self.import_module("modules.run", name)
                    if mod:
                        for item in mod.template_module_variables():
                            tci: TemplateConfigItem = item
                            self._cfh.set(
                                name,
                                varname=tci.varname,
                                value=tci.value,
                                desc=tci.desc,
                            )
                    else:
                        self.logs.message_error = (
                            f"Cannot load module: modules.run.'{name}'"
                        )

        try:
            return self.save()
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
        return self._cfh

    @property
    def __main(self) -> Dict:
        """Return MAIN dict."""
        return self._data[_Keys.MAIN]

    @property
    def __modules(self) -> Dict:
        """Return MODULES dict."""
        return self._data[_Keys.MODULES]

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
        if self._cfh:
            if self._cfh.get(self._section, "debug"):
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
