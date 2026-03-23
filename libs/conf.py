# -*- coding: UTF-8 -*-
"""
Application configuration service.

Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 2023-11-07

Purpose: Provide configuration loading, generation, and module discovery logic.
"""

import socket

from inspect import currentframe
from typing import Dict, Optional, List, Union, Tuple

from jsktoolbox.attribtool import ReadOnlyClass
from jsktoolbox.raisetool import Raise
from jsktoolbox.logstool import LoggerClient, LoggerQueue
from jsktoolbox.configtool import Config as ConfigTool
from jsktoolbox.stringtool import SimpleCrypto
from jsktoolbox.basetool import BData

from libs import AppName
from libs.base import (
    ConfigHandlerMixin,
    ConfigSectionMixin,
    ImporterMixin,
    LogsMixin,
    ModuleConfigMixin,
)

from libs.interfaces import IComModule, IRunModule
from libs.templates import TemplateConfigItem


class _Keys(object, metaclass=ReadOnlyClass):
    """Define internal storage keys and config variable names."""

    # #[CONSTANTS]####################################################################
    # internal vars
    APP_NAME: str = "__app_name__"
    CF: str = "__cf__"
    CONF_FILE: str = "__CONF_FILE__"
    CONF_UPDATE: str = "__config_update__"
    DEBUG: str = "__DEBUG__"
    MAIN: str = "__MAIN__"
    MODULE_CONF: str = "__MODULE_CONF__"
    MODULES: str = "__MODULES__"
    NAME: str = "__NAME__"
    PASSWORD: str = "__password__"
    PASSWORD_SECTION: str = "__pass_section__"
    PASSWORD_VARNAME: str = "__pass_var__"
    START_TIME: str = "__start_time__"
    VERBOSE: str = "__VERBOSE__"
    VERSION: str = "__VERSION__"

    # config keys
    MC_DEBUG: str = "debug"
    MC_MODULES: str = "modules"
    MC_SALT: str = "salt"
    MC_VERBOSE: str = "verbose"
    MC_PLUGINS_DIR: str = "plugins_dir"


class _ModuleConf(ModuleConfigMixin):
    """Provide typed access to the daemon main-section configuration."""

    # #[PUBLIC PROPERTIES]############################################################
    @property
    def debug(self) -> bool:
        """Return the global debug flag from the main section.

        ### Returns:
        bool - Debug flag value.
        """
        var: Optional[bool] = self._get(_Keys.MC_DEBUG)
        if var is None:
            return False
        return var

    @property
    def modules(self) -> List[str]:
        """Return the sorted list of enabled module names.

        ### Returns:
        List[str] - Sorted names of enabled runtime modules.

        ### Raises:
        * TypeError: If the configuration value is not a list of strings.
        """
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
    def plugins_dir(self) -> Optional[str]:
        """Return the plugins directory path from the main section.

        ### Returns:
        Optional[str] - Path to the plugins directory or `None`.
        """
        return self._get(_Keys.MC_PLUGINS_DIR)

    @property
    def salt(self) -> int:
        """Return the password encryption salt.

        ### Returns:
        int - Salt value read from the main configuration section.
        """
        return self._get(_Keys.MC_SALT)

    @property
    def verbose(self) -> bool:
        """Return the global verbose flag from the main section.

        ### Returns:
        bool - Verbose flag value.
        """
        var: Optional[bool] = self._get(_Keys.MC_VERBOSE)
        if var is None:
            return False
        return var


class AppConfig(LogsMixin, ConfigHandlerMixin, ConfigSectionMixin, ImporterMixin):
    """Manage daemon configuration, module discovery, and config generation."""

    # #[CONSTRUCTOR]##################################################################
    def __init__(self, qlog: LoggerQueue, app_name: str) -> None:
        """Initialize the application configuration service.

        ### Arguments:
        * qlog: LoggerQueue - Shared logging queue used by the configuration service.
        * app_name: str - Name of the main application section in the config file.
        """
        from jsktoolbox.datetool import Timestamp

        self.logs = LoggerClient(queue=qlog, name=self._c_name)
        self.logs.message_info = "Config initialization..."
        self._set_data(key=_Keys.MAIN, value=BData(), set_default_type=BData)
        self._set_data(key=_Keys.MODULES, value={}, set_default_type=Dict)
        self.__main._set_data(
            key=_Keys.START_TIME, value=Timestamp.now(), set_default_type=int
        )
        self._set_data(
            key=_Keys.MODULE_CONF, value=None, set_default_type=Optional[_ModuleConf]
        )
        self.app_name = app_name
        self._set_data(key=_Keys.CF, value=None)
        self.logs.message_info = "... complete"

    # #[PUBLIC PROPERTIES]############################################################
    @property
    def app_name(self) -> Optional[str]:
        """Return the application section name.

        ### Returns:
        Optional[str] - Main section name or `None`.
        """
        return self.__main._get_data(key=_Keys.APP_NAME, default_value=None)

    @app_name.setter
    def app_name(self, value: str) -> None:
        """Store the application section name.

        ### Arguments:
        * value: str - Main section name written to internal state.
        """
        self.__main._set_data(key=_Keys.APP_NAME, value=value, set_default_type=str)
        self._section = value

    @property
    def cf(self) -> Optional[ConfigTool]:
        """Return the bound configuration handler.

        ### Returns:
        Optional[ConfigTool] - Configuration handler or `None`.
        """
        return self._cfh

    @property
    def config_file(self) -> Optional[str]:
        """Return the configuration file path.

        ### Returns:
        Optional[str] - Absolute or relative path to the configuration file.
        """
        return self.__main._get_data(key=_Keys.CONF_FILE, default_value=None)

    @config_file.setter
    def config_file(self, value: str) -> None:
        """Store the configuration file path.

        ### Arguments:
        * value: str - Configuration file path.
        """
        self.__main._set_data(key=_Keys.CONF_FILE, value=value, set_default_type=str)

    @property
    def debug(self) -> bool:
        """Return the effective global debug flag.

        ### Returns:
        bool - Debug flag value.
        """
        debug: Optional[bool] = self.__main._get_data(
            key=_Keys.DEBUG, default_value=None
        )
        if debug is None:
            self.__main._set_data(key=_Keys.DEBUG, value=False, set_default_type=bool)
            debug = False
        if self._cfh and self._section and self._cfh.get(self._section, _Keys.MC_DEBUG):
            return True
        return debug

    @debug.setter
    def debug(self, value: bool) -> None:
        """Store the global debug flag.

        ### Arguments:
        * value: bool - Debug flag value.
        """
        self.__main._set_data(key=_Keys.DEBUG, value=value, set_default_type=bool)

    @property
    def fqdn(self) -> str:
        """Return the current host FQDN.

        ### Returns:
        str - Fully qualified domain name.
        """
        return socket.getfqdn()

    @property
    def get_com_modules(self) -> List[IComModule]:
        """Return the enabled communication module classes.

        ### Returns:
        List[IComModule] - Imported communication module classes.
        """
        return self.__get_modules_list("modules.com")  # type: ignore

    @property
    def get_run_modules(self) -> List[IRunModule]:
        """Return the enabled task module classes.

        ### Returns:
        List[IRunModule] - Imported task module classes.
        """
        return self.__get_modules_list("modules.run")  # type: ignore

    @property
    def module_conf(self) -> Optional[_ModuleConf]:
        """Return the typed main-section configuration adapter.

        ### Returns:
        Optional[_ModuleConf] - Typed configuration adapter or `None`.
        """
        return self._get_data(key=_Keys.MODULE_CONF, default_value=None)

    @property
    def password(self) -> bool:
        """Return the one-shot password update flag.

        ### Returns:
        bool - Password update mode flag.
        """
        obj: Optional[bool] = self.__main._get_data(
            key=_Keys.PASSWORD, default_value=None
        )
        if obj is None:
            self.__main._set_data(
                key=_Keys.PASSWORD, value=False, set_default_type=bool
            )
            return False
        return obj

    @password.setter
    def password(self, value: bool) -> None:
        """Store the one-shot password update flag.

        ### Arguments:
        * value: bool - Password update mode flag.
        """
        self.__main._set_data(key=_Keys.PASSWORD, value=value, set_default_type=bool)

    @property
    def plugins_dir(self) -> Optional[str]:
        """Return the plugins directory path from the main section.

        ### Returns:
        Optional[str] - Path to the plugins directory or `None`.
        """
        return self.__main._get_data(key=_Keys.MC_PLUGINS_DIR, default_value=None)

    @plugins_dir.setter
    def plugins_dir(self, value: str) -> None:
        """Store the plugins directory path in the main section.

        ### Arguments:
        * value: str - Path to the plugins directory.
        """
        self.__main._set_data(
            key=_Keys.MC_PLUGINS_DIR, value=value, set_default_type=str
        )

    @property
    def update(self) -> bool:
        """Return the configuration update flag.

        ### Returns:
        bool - Update mode flag.
        """
        obj: Optional[bool] = self.__main._get_data(
            key=_Keys.CONF_UPDATE, default_value=None
        )
        if obj is None:
            self.__main._set_data(
                key=_Keys.CONF_UPDATE, value=False, set_default_type=bool
            )
            return False
        return obj

    @update.setter
    def update(self, value: bool) -> None:
        """Store the configuration update flag.

        ### Arguments:
        * value: bool - Update mode flag.
        """
        self.__main._set_data(key=_Keys.CONF_UPDATE, value=value, set_default_type=bool)

    @property
    def verbose(self) -> bool:
        """Return the effective global verbose flag.

        ### Returns:
        bool - Verbose flag value.
        """
        verbose: Optional[bool] = self.__main._get_data(
            key=_Keys.VERBOSE, default_value=None
        )
        if verbose is None:
            self.__main._set_data(key=_Keys.VERBOSE, value=False, set_default_type=bool)
            verbose = False
        if (
            self._cfh
            and self._section
            and self._cfh.get(self._section, _Keys.MC_VERBOSE)
        ):
            return True
        return verbose

    @verbose.setter
    def verbose(self, value: bool) -> None:
        """Store the global verbose flag.

        ### Arguments:
        * value: bool - Verbose flag value.
        """
        self.__main._set_data(key=_Keys.VERBOSE, value=value, set_default_type=bool)

    @property
    def version(self) -> Optional[str]:
        """Return the current application version string.

        ### Returns:
        Optional[str] - Application version string or `None`.
        """
        return self.__main._get_data(key=_Keys.VERSION, default_value=None)

    @version.setter
    def version(self, value: str) -> None:
        """Store the current application version string.

        ### Arguments:
        * value: str - Application version string.
        """
        self.__main._set_data(key=_Keys.VERSION, value=value, set_default_type=str)

    # #[PROTECTED PROPERTIES]#########################################################
    @property
    def _password_section(self) -> Optional[str]:
        """Return the section name targeted by password update mode.

        ### Returns:
        Optional[str] - Target section name or `None`.
        """
        return self.__main._get_data(key=_Keys.PASSWORD_SECTION, default_value=None)

    @_password_section.setter
    def _password_section(self, value: str) -> None:
        """Store the section name targeted by password update mode.

        ### Arguments:
        * value: str - Target section name.
        """
        self.__main._set_data(
            key=_Keys.PASSWORD_SECTION, value=value, set_default_type=str
        )

    @property
    def _password_varname(self) -> Optional[str]:
        """Return the variable name targeted by password update mode.

        ### Returns:
        Optional[str] - Target variable name or `None`.
        """
        return self.__main._get_data(key=_Keys.PASSWORD_VARNAME, default_value=None)

    @_password_varname.setter
    def _password_varname(self, value: str) -> None:
        """Store the variable name targeted by password update mode.

        ### Arguments:
        * value: str - Target variable name.
        """
        self.__main._set_data(
            key=_Keys.PASSWORD_VARNAME, value=value, set_default_type=str
        )

    # #[PRIVATE PROPERTIES]###########################################################
    @property
    def __main(self) -> BData:
        """Return the internal main-state container.

        ### Returns:
        BData - Internal state container for global configuration data.
        """
        obj: Optional[BData] = self._get_data(key=_Keys.MAIN)
        if obj is None:
            raise Raise.error(
                "Main state container is not initialized.",
                RuntimeError,
                self._c_name,
                currentframe(),
            )
        return obj

    @property
    def __modules(self) -> Dict:
        """Return the internal module-state container.

        ### Returns:
        Dict - Internal module state dictionary.
        """
        obj: Optional[Dict] = self._get_data(key=_Keys.MODULES)
        if obj is None:
            raise Raise.error(
                "Module state container is not initialized.",
                RuntimeError,
                self._c_name,
                currentframe(),
            )
        return obj

    # #[PUBLIC METHODS]###############################################################
    def load(self) -> bool:
        """Load the configuration file and refresh discovered module settings.

        ### Returns:
        bool - `True` when the configuration was loaded successfully.
        """
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
            self._set_data(
                key=_Keys.MODULE_CONF, value=_ModuleConf(config, self._section)
            )
            if not config.file_exists:
                self.logs.message_warning = (
                    f"config file '{self.config_file}' does not exist"
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
            if out:
                if self.debug:
                    self.logs.message_debug = "config file loaded successful"
                if self.module_conf and self.module_conf.modules:
                    self.logs.message_info = (
                        f"list of modules to enable: {self.module_conf.modules}"
                    )
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

    def reload(self) -> bool:
        """Reload the configuration file from disk.

        ### Returns:
        bool - `True` when the configuration was reloaded successfully.
        """
        self._cfh = None
        return self.load()

    def save(self) -> bool:
        """Persist the current configuration handler to disk.

        ### Returns:
        bool - `True` when the configuration was saved successfully.
        """
        if self._cfh:
            if self._cfh.save():
                if self.debug:
                    self.logs.message_debug = "config file saved successful"
                return True
            self.logs.message_warning = f"cannot save config file: '{self.config_file}'"
        return False

    # #[PRIVATE METHODS]##############################################################
    def __check_module_config_updates(self) -> bool:
        """Ensure that discovered modules have all required config entries.

        ### Returns:
        bool - `True` when the configuration file requires an update.
        """
        test = False
        if self._cfh is None:
            return False
        (com_mods, run_mods, config) = self.__get_modules_config()
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
                continue
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
                        self.logs.message_debug = (
                            f"add default new variable '{tci.varname}' "
                            f"to section: [{name}]"
                        )
        return test

    def __create_config_file(self) -> bool:
        """Create a default configuration file using discovered module templates.

        ### Returns:
        bool - `True` when the configuration file was created successfully.
        """
        if self._cfh is None or self._section is None:
            return False
        self._cfh.set(self._section, desc=f"{self._section} configuration file")
        self._cfh.set(self._section, varname=_Keys.MC_DEBUG, value=False)
        self._cfh.set(self._section, varname=_Keys.MC_VERBOSE, value=False)
        self._cfh.set(
            self._section,
            varname=_Keys.MC_SALT,
            value=SimpleCrypto.salt_generator(6),
            desc="[int] salt for passwords encode/decode",
        )
        # default plugins dir is located in the same directory as the project main script
        self._cfh.set(
            self._section,
            varname=_Keys.MC_PLUGINS_DIR,
            value=self.plugins_dir or "./plugins",
            desc="path to the plugins directory",
        )

        # collect config templates from modules
        (com_mods, run_mods, config) = self.__get_modules_config()
        self._cfh.set(self._section, desc="[ communication modules ]:")
        for item in com_mods:
            self._cfh.set(self._section, desc=f"{item}")
        self._cfh.set(self._section, desc="##")
        self._cfh.set(self._section, desc="[ running modules ]:")
        for item in run_mods:
            self._cfh.set(self._section, desc=f"{item}")
        self._cfh.set(self._section, desc="##")
        self._cfh.set(
            self._section,
            varname=_Keys.MC_MODULES,
            value=[],
            desc="list of modules to activate",
        )
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

    def __get_modules_config(self) -> Tuple[List[str], List[str], Dict]:
        """Collect configuration templates for discovered communication and task modules.

        ### Returns:
        Tuple[List[str], List[str], Dict] - Communication module names, task
        module names, and their configuration template definitions.
        """
        com_mods = sorted(self.import_name_list("modules.com"))
        run_mods = sorted(self.import_name_list("modules.run"))
        config = dict()
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

    def __get_modules_list(self, package: str) -> List[Union[IRunModule, IComModule]]:
        """Return enabled modules available in the selected package.

        ### Arguments:
        * package: str - Dotted package path, for example `modules.com`.

        ### Returns:
        List[Union[IRunModule, IComModule]] - Imported module classes enabled in config.
        """
        out = []
        if self.module_conf and self.module_conf.modules:
            name_list = self.import_name_list(package)
            if self.debug:
                self.logs.message_debug = f"found module list: {name_list}"
            tmp = dict(zip(self.module_conf.modules, self.module_conf.modules))
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


# #[EOF]#######################################################################
