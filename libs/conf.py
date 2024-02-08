# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 07.11.2023

  Purpose: configuration package
"""

import socket

from inspect import currentframe
from typing import Dict, Optional, List, Any, Union, Tuple

from jsktoolbox.attribtool import ReadOnlyClass
from jsktoolbox.raisetool import Raise
from jsktoolbox.logstool.logs import LoggerClient, LoggerQueue
from jsktoolbox.configtool.main import Config as ConfigTool
from jsktoolbox.stringtool.crypto import SimpleCrypto
from libs.base.classes import (
    BLogs,
    BConfigSection,
    BConfigHandler,
    BModuleConfig,
    BImporter,
)

from libs.interfaces.modules import IComModule, IRunModule
from libs.templates.modules import TemplateConfigItem


class _Keys(object, metaclass=ReadOnlyClass):
    """Private Keys definition class.

    For internal purpose only.
    """

    # internal vars
    APP_NAME: str = "__app_name__"
    CF: str = "__cf__"
    CONF_FILE: str = "__CONF_FILE__"
    CONF_UPDATE: str = "__config_update__"
    DEBUG: str = "__DEBUG__"
    MAIN: str = "__MAIN__"
    MODCONF: str = "__MODULE_CONF__"
    MODULES: str = "__MODULES__"
    NAME: str = "__NAME__"
    PASSWORD: str = "__password__"
    PASS_SECTION: str = "__pass_section__"
    PASS_VAR: str = "__pass_var__"
    START_TIME: str = "__start_time__"
    VERBOSE: str = "__VERBOSE__"
    VERSION: str = "__VERSION__"

    # config keys
    MC_DEBUG: str = "debug"
    MC_MODULES: str = "modules"
    MC_SALT: str = "salt"
    MC_VERBOSE: str = "verbose"


class _ModuleConf(BModuleConfig):
    """Module Config private class."""

    @property
    def debug(self) -> bool:
        """Return debug var."""
        var: Optional[bool] = self._get(_Keys.MC_DEBUG)
        if var is None:
            return False
        return var

    @property
    def verbose(self) -> bool:
        """Return verbose var."""
        var: Optional[bool] = self._get(_Keys.MC_VERBOSE)
        if var is None:
            return False
        return var

    @property
    def modules(self) -> List[str]:
        """Return modules list."""
        tmp: Optional[List[str]] = self._get(_Keys.MC_MODULES)
        if tmp is None:
            return []
        if not isinstance(tmp, List):
            raise Raise.error(
                "Expected type 'List' in variable 'modules'.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        if tmp:
            for item in tmp:
                if not isinstance(item, str):
                    raise Raise.error(
                        "Names were expected as strings in the module list.",
                        TypeError,
                        self._c_name,
                        currentframe(),
                    )
        return sorted(tmp)

    @property
    def salt(self) -> int:
        """Return salt var."""
        return self._get(_Keys.MC_SALT)


class Config(BLogs, BConfigHandler, BConfigSection, BImporter):
    """Configuration container class."""

    def __init__(self, qlog: LoggerQueue, app_name: str) -> None:
        """Constructor."""
        from jsktoolbox.datetool import Timestamp

        # class logger client
        self.logs = LoggerClient(queue=qlog, name=self._c_name)

        self.logs.message_info = "Config initialization..."
        # initialization data structure
        self._data[_Keys.MAIN] = dict()
        self._data[_Keys.MODULES] = dict()
        # starting timestamp
        self._data[_Keys.MAIN][_Keys.START_TIME] = Timestamp.now
        # self.module_conf
        self._data[_Keys.MODCONF] = None
        # config file main section name
        self.app_name = app_name
        # config file handler
        self._data[_Keys.CF] = None

        # constructor complete
        self.logs.message_info = "... complete"

    def load(self) -> bool:
        """Try to load config file."""
        if self.config_file is None or self._section is None:
            self.logs.message_critical = (
                f"UNRECOVERABLE ERROR: {self._c_name}.{self._f_name}"
            )
            self.logs.message_error = (
                f"config file: {self.config_file}, section:{self._section}"
            )
            return False
        if self._cfh is None:
            config = ConfigTool(self.config_file, self._section)
            self._cfh = config
            self._data[_Keys.MODCONF] = _ModuleConf(config, self._section)
            if not config.file_exists:
                self.logs.message_warning = (
                    f"config file '{self.config_file}' not exist"
                )
                self.logs.message_warning = "try to create default one"
                if not self.__create_config_file():
                    return False
        try:
            if self.debug:
                self.logs.message_debug = (
                    f"try to load config file: '{self.config_file}'..."
                )
            out: bool = self._cfh.load()
            # TODO: process config file
            if out:
                if self.debug:
                    self.logs.message_debug = "config file loaded successful"
                if self.module_conf and self.module_conf.modules:
                    self.logs.message_info = (
                        f"list of modules to enable: {self.module_conf.modules}"
                    )

            # check module updates
            if self.__check_module_config_updates():
                if self.debug:
                    self.logs.message_debug = "found new module configuration"
                if not self._cfh.save():
                    self.logs.message_critical = "cannot update config file."
            return out
        except Exception as ex:
            self.logs.message_critical = (
                f"cannot load config file: '{self.config_file}'"
            )
            if self.debug:
                self.logs.message_debug = f"{ex}"
            return False

    def save(self) -> bool:
        """Try to save config file."""
        if self._cfh:
            if self._cfh.save():
                if self.debug:
                    self.logs.message_debug = "config file saved successful"
                return True
            else:
                self.logs.message_warning = (
                    f"cannot save config file: '{self.config_file}'"
                )
        return False

    def reload(self) -> bool:
        """Try to reload config file."""
        self._cfh = None
        return self.load()

    def __check_module_config_updates(self) -> bool:
        """Check module configs."""
        test = False
        if self._cfh is None:
            return False
        (com_mods, run_mods, config) = self.__get_modules_config()
        # check modules
        for name in com_mods + run_mods:
            if not self._cfh.has_section(name):
                test = True
                for item in config[name]:
                    tci: TemplateConfigItem = item
                    self._cfh.set(
                        name,
                        varname=tci.varname,
                        value=tci.value,
                        desc=tci.desc,
                    )
                if self.debug:
                    self.logs.message_debug = (
                        f"add default configuration for section: [{name}]"
                    )
            else:
                for item in config[name]:
                    tci: TemplateConfigItem = item
                    if tci.varname and not self._cfh.has_varname(name, tci.varname):
                        test = True
                        self._cfh.set(
                            name,
                            varname=tci.varname,
                            value=tci.value,
                            desc=tci.desc,
                        )
                        if self.debug:
                            self.logs.message_debug = f"add default new variable '{tci.varname}' to section: [{name}]"

        return test

    def __get_modules_config(self) -> Tuple[List[str], List[str], Dict]:
        """Get modules configuration template."""
        # init local variables
        com_mods = list()
        run_mods = list()
        config = dict()

        # get modules name list
        com_mods = sorted(self.import_name_list("modules.com"))
        run_mods = sorted(self.import_name_list("modules.run"))

        # get config template
        for item in com_mods:
            config[item] = []
            com_mod: IComModule = self.import_module("modules.com", item)  # type: ignore
            if com_mod:
                for mod_item in com_mod.template_module_variables():
                    config[item].append(mod_item)
            else:
                self.logs.message_error = f"Cannot load module: modules.com.{item}"

        for item in run_mods:
            config[item] = []
            run_mod: IRunModule = self.import_module("modules.run", item)  # type: ignore
            if run_mod:
                for mod_item in run_mod.template_module_variables():
                    config[item].append(mod_item)
            else:
                self.logs.message_error = f"Cannot load module: modules.run.{item}"
        return com_mods, run_mods, config

    def __create_config_file(self) -> bool:
        """Try to create config file."""
        if self._cfh is None or self._section is None:
            return False
        # main section
        (com_mods, run_mods, config) = self.__get_modules_config()
        # set header file
        self._cfh.set(self._section, desc=f"{self._section} configuration file")
        # generate description for communication modules
        self._cfh.set(self._section, desc="[ communication modules ]:")
        for item in com_mods:
            self._cfh.set(self._section, desc=f"{item}")
        self._cfh.set(self._section, desc="##")
        # generate description for running modules
        self._cfh.set(self._section, desc="[ running modules ]:")
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
        # add verbose variable
        self._cfh.set(self._section, varname=_Keys.MC_VERBOSE, value=False)
        # add salt variable
        self._cfh.set(
            self._section,
            varname=_Keys.MC_SALT,
            value=SimpleCrypto.salt_generator(6),
            desc="[int] salt for passwords encode/decode",
        )

        # modules section
        # communication modules
        if self.debug:
            self.logs.message_debug = f"Found communication modules list: {com_mods}"
        if com_mods:
            for name in com_mods:
                if name not in config:
                    self.logs.message_critical = (
                        f"cannot found config template for module: '{name}'"
                    )
                    continue
                for item in config[name]:
                    tci: TemplateConfigItem = item
                    self._cfh.set(
                        name,
                        varname=tci.varname,
                        value=tci.value,
                        desc=tci.desc,
                    )

        # running modules
        if self.debug:
            self.logs.message_debug = f"Found running modules list: {run_mods}"
        if run_mods:
            for name in run_mods:
                if name not in config:
                    self.logs.message_critical = (
                        f"cannot found config template for module: '{name}'"
                    )
                    continue
                for item in config[name]:
                    tci: TemplateConfigItem = item
                    self._cfh.set(
                        name,
                        varname=tci.varname,
                        value=tci.value,
                        desc=tci.desc,
                    )

        try:
            return self.save()
        except Exception as ex:
            self.logs.message_critical = (
                f"cannot create config file: '{self.config_file}'"
            )
            if self.debug:
                self.logs.message_debug = f"{ex}"
            return False

    @property
    def app_name(self) -> Optional[str]:
        """Returns app name."""
        if _Keys.APP_NAME not in self.__main:
            self.__main[_Keys.APP_NAME] = None
        return self.__main[_Keys.APP_NAME]

    @app_name.setter
    def app_name(self, value: str) -> None:
        """Sets app name string."""
        if not isinstance(value, str):
            raise Raise.error(
                f"Expected string type",
                TypeError,
                self._c_name,
                currentframe(),
            )
        self.__main[_Keys.APP_NAME] = value
        self._section = value

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
        if _Keys.CONF_FILE not in self.__main:
            self.__main[_Keys.CONF_FILE] = None
        return self.__main[_Keys.CONF_FILE]

    @config_file.setter
    def config_file(self, value: str) -> None:
        """Set config_file path string."""
        if not isinstance(value, str):
            raise Raise.error(
                f"Expected String type, received: '{type(value)}'.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        self.__main[_Keys.CONF_FILE] = value

    @property
    def debug(self) -> bool:
        """Return debug flag."""
        if _Keys.DEBUG not in self.__main:
            self.__main[_Keys.DEBUG] = False
        if self._cfh and self._section:
            if self._cfh.get(self._section, _Keys.MC_DEBUG):
                return True
        return self.__main[_Keys.DEBUG]

    @debug.setter
    def debug(self, value: bool) -> None:
        """Set debug flag."""
        if not isinstance(value, bool):
            raise Raise.error(
                f"Expected Boolean type, received: '{type(value)}'.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        self.__main[_Keys.DEBUG] = value

    def __get_modules_list(self, package: str) -> List:
        """Get configured modules list."""
        out = []
        if self.module_conf and self.module_conf.modules:
            # try search importable modules and compare it to config variable list
            name_list = self.import_name_list(package)
            if self.debug:
                self.logs.message_debug = f"found module list: {name_list}"
            # make dictionary
            tmp = dict(zip(self.module_conf.modules, self.module_conf.modules))
            # find name in tmp dict
            for name in name_list:
                if name in tmp:
                    imod = self.import_module(package, name)
                    if imod:
                        out.append(imod)
                    else:
                        self.logs.message_error = (
                            f"cannot import module: '{package}.{name}'"
                        )

        return out

    @property
    def fqdn(self) -> str:
        """Get fully qualified domain name from name."""
        return socket.getfqdn()

    @property
    def get_com_modules(self) -> List[IComModule]:
        """Get configured communication modules list."""
        import_from = "modules.com"
        return self.__get_modules_list(import_from)

    @property
    def get_run_modules(self) -> List[IRunModule]:
        """Get configured running modules list."""
        import_from = "modules.run"
        return self.__get_modules_list(import_from)

    @property
    def module_conf(self) -> Optional[_ModuleConf]:
        """Return module conf object."""
        return self._data[_Keys.MODCONF]

    @property
    def password(self) -> bool:
        """Return password flag."""
        if _Keys.PASSWORD not in self.__main:
            self.__main[_Keys.PASSWORD] = False
        return self.__main[_Keys.PASSWORD]

    @password.setter
    def password(self, value: bool) -> None:
        """Set password flag."""
        if not isinstance(value, bool):
            raise Raise.error(
                f"Expected boolean type, received '{type(value)}'.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        self.__main[_Keys.PASSWORD] = value

    @property
    def _password_section(self) -> Optional[str]:
        """Return password section string."""
        if _Keys.PASS_SECTION not in self.__main:
            return None
        return self.__main[_Keys.PASS_SECTION]

    @_password_section.setter
    def _password_section(self, value: str) -> None:
        """Set password section string."""
        if not isinstance(value, str):
            raise Raise.error(
                f"Expected string type, received '{type(value)}'.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        self.__main[_Keys.PASS_SECTION] = value

    @property
    def _password_varname(self) -> Optional[str]:
        """Return password varname string."""
        if _Keys.PASS_VAR not in self.__main:
            return None
        return self.__main[_Keys.PASS_VAR]

    @_password_varname.setter
    def _password_varname(self, value: str) -> None:
        """Set password varname string."""
        if not isinstance(value, str):
            raise Raise.error(
                f"Expected string type, received '{type(value)}'.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        self.__main[_Keys.PASS_VAR] = value

    @property
    def update(self) -> bool:
        """Return update flag."""
        if _Keys.CONF_UPDATE not in self.__main:
            self.__main[_Keys.CONF_UPDATE] = False
        return self.__main[_Keys.CONF_UPDATE]

    @update.setter
    def update(self, value: bool) -> None:
        """Set update flag."""
        if not isinstance(value, bool):
            raise Raise.error(
                f"Expected Boolean type, received: '{type(value)}'.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        self.__main[_Keys.CONF_UPDATE] = value

    @property
    def verbose(self) -> bool:
        """Return verbose flag."""
        if _Keys.VERBOSE not in self.__main:
            self.__main[_Keys.VERBOSE] = False
        if self._cfh and self._section:
            if self._cfh.get(self._section, _Keys.MC_VERBOSE):
                return True
        return self.__main[_Keys.VERBOSE]

    @verbose.setter
    def verbose(self, value: bool) -> None:
        """Set verbose flag."""
        if not isinstance(value, bool):
            raise Raise.error(
                f"Expected Boolean type, received: '{type(value)}'.",
                TypeError,
                self._c_name,
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
                f"Expected String type, received: '{type(value)}'.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        self.__main[_Keys.VERSION] = value


# #[EOF]#######################################################################
