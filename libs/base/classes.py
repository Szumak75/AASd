# -*- coding: UTF-8 -*-
"""
Shared project base classes.

Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 2023-11-06

Purpose: Provide shared mixin-style helper classes used by the daemon and runtime modules.
"""

import os

from inspect import currentframe
from typing import TYPE_CHECKING, Optional, List, Any, Union
from queue import Queue

from jsktoolbox.raisetool import Raise
from jsktoolbox.basetool import BData
from jsktoolbox.logstool import LoggerClient
from jsktoolbox.configtool import Config as ConfigTool
from jsktoolbox.attribtool import ReadOnlyClass

from libs import AppName, Keys

if TYPE_CHECKING:
    from libs import AppConfig


class AppNameMixin(BData):
    """Mixin that exposes a typed application identity property."""

    # #[PUBLIC PROPERTIES]#############################################################
    @property
    def application(self) -> AppName:
        """Return the application identity object.

        ### Returns:
        AppName - Runtime application identity container.
        """
        obj: Optional[AppName] = self._get_data(key=Keys.APP_NAME, default_value="")
        if obj is None:
            raise Raise.error(
                "Application identity not set.",
                ValueError,
                self._c_name,
                currentframe(),
            )
        return obj

    @application.setter
    def application(self, value: AppName) -> None:
        """Store the application identity object.

        ### Arguments:
        * value: AppName - Runtime application identity container.
        """
        self._set_data(key=Keys.APP_NAME, value=value, set_default_type=AppName)


class ConfigHandlerMixin(BData):
    """Mixin that exposes a typed configuration handler property."""

    # #[PROTECTED PROPERTIES]##########################################################
    @property
    def _cfh(self) -> Optional[ConfigTool]:
        """Return the bound configuration handler.

        ### Returns:
        Optional[ConfigTool] - Active configuration handler or `None`.
        """
        return self._get_data(key=Keys.CFH, default_value=None)

    @_cfh.setter
    def _cfh(self, config_handler: Optional[ConfigTool]) -> None:
        """Store the bound configuration handler.

        ### Arguments:
        * config_handler: Optional[ConfigTool] - Configuration handler instance.
        """
        self._set_data(
            key=Keys.CFH, value=config_handler, set_default_type=Optional[ConfigTool]
        )


class ConfigSectionMixin(BData):
    """Mixin that exposes a typed configuration section property."""

    # #[PROTECTED PROPERTIES]##########################################################
    @property
    def _section(self) -> Optional[str]:
        """Return the bound configuration section name.

        ### Returns:
        Optional[str] - Normalized section name or `None`.
        """
        return self._get_data(key=Keys.SECTION, default_value=None)

    @_section.setter
    def _section(self, section_name: Optional[str]) -> None:
        """Store the configuration section name.

        The setter normalizes string values to lowercase to match the current
        configuration access pattern.

        ### Arguments:
        * section_name: Optional[str] - Section name to bind.
        """
        sn: Optional[str] = None
        if section_name and isinstance(section_name, str):
            sn = section_name.lower()
        else:
            sn = section_name
        self._set_data(key=Keys.SECTION, value=sn, set_default_type=Optional[str])


class ModuleConfigMixin(ConfigHandlerMixin, ConfigSectionMixin):
    """Mixin-style adapter that provides typed access to module configuration."""

    # #[CONSTANTS]#####################################################################
    class Keys(object, metaclass=ReadOnlyClass):
        """Define shared configuration key names for module settings."""

        CHANNEL: str = "channel"
        MESSAGE_CHANNEL: str = "message_channel"
        MODULE_CONF: str = "__MODULE_CONF__"
        SLEEP_PERIOD: str = "sleep_period"

    # #[CONSTRUCTOR]##################################################################
    def __init__(self, cfh: ConfigTool, section: Optional[str]) -> None:
        """Initialize the module configuration adapter.

        ### Arguments:
        * cfh: ConfigTool - Configuration handler used for value lookups.
        * section: Optional[str] - Configuration section bound to the module.
        """
        self._cfh = cfh
        self._section = section

    # #[PUBLIC PROPERTIES]#############################################################
    @property
    def channel(self) -> Optional[int]:
        """Return the communication channel configured for a module.

        ### Returns:
        Optional[int] - Communication channel number or `None`.

        ### Raises:
        * TypeError: If the configured value is not an integer.
        """
        var: Optional[int] = self._get(varname=ModuleConfigMixin.Keys.CHANNEL)
        if var is not None and not isinstance(var, int):
            raise Raise.error(
                "Expected int type.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        return var

    @property
    def message_channel(self) -> Optional[List[str]]:
        """Return the message channel configuration for a task module.

        ### Returns:
        Optional[List[str]] - Channel schedule definitions or `None`.

        ### Raises:
        * TypeError: If the configured value is not a list.
        """
        var = self._get(varname=ModuleConfigMixin.Keys.MESSAGE_CHANNEL)
        if var is not None and not isinstance(var, List):
            raise Raise.error(
                "Expected list type.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        return var

    @property
    def sleep_period(self) -> Optional[float]:
        """Return the module sleep interval.

        ### Returns:
        Optional[float] - Sleep interval in seconds or `None`.

        ### Raises:
        * TypeError: If the configured value is neither `int` nor `float`.
        """
        var: Optional[Union[int, float]] = self._get(
            varname=ModuleConfigMixin.Keys.SLEEP_PERIOD
        )
        if var is None:
            return None
        if not isinstance(var, (int, float)):
            raise Raise.error(
                "Expected float or int type.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        return float(var)

    # #[PRIVATE METHODS]###############################################################
    def _get(self, varname: str) -> Any:
        """Return a raw configuration value from the current section.

        ### Arguments:
        * varname: str - Variable name to read from the configuration section.

        ### Returns:
        Any - Raw configuration value or `None`.
        """
        if self._cfh and self._section:
            return self._cfh.get(self._section, varname)
        return None


class LogsMixin(BData):
    """Mixin that exposes a typed logger client property."""

    # #[PUBLIC PROPERTIES]#############################################################
    @property
    def logs(self) -> LoggerClient:
        """Return the logger client for the current object.

        ### Returns:
        LoggerClient - Logger client instance.
        """
        if self._get_data(key=Keys.CLOG, default_value=None) is None:
            self._set_data(
                key=Keys.CLOG, value=LoggerClient(), set_default_type=LoggerClient
            )
        out: Optional[LoggerClient] = self._get_data(key=Keys.CLOG, default_value=None)
        if out is None:
            raise Raise.error(
                "Logger client not set.",
                ValueError,
                self._c_name,
                currentframe(),
            )
        return out

    @logs.setter
    def logs(self, logs: LoggerClient) -> None:
        """Store the logger client for the current object.

        ### Arguments:
        * logs: LoggerClient - Logger client instance.
        """
        self._set_data(key=Keys.CLOG, value=logs, set_default_type=LoggerClient)


class ComMixin(BData):
    """Mixin that exposes a typed communication queue property."""

    # #[PUBLIC PROPERTIES]#############################################################
    @property
    def qcom(self) -> Optional[Queue]:
        """Return the shared communication queue.

        ### Returns:
        Optional[Queue] - Communication queue or `None`.
        """
        return self._get_data(key=Keys.QCOM, default_value=None)

    @qcom.setter
    def qcom(self, queue: Queue) -> None:
        """Store the shared communication queue.

        ### Arguments:
        * queue: Queue - Communication queue instance.
        """
        self._set_data(key=Keys.QCOM, value=queue, set_default_type=Queue)


class ConfigMixin(BData):
    """Mixin that exposes a typed application configuration property."""

    # #[PUBLIC PROPERTIES]#############################################################
    @property
    def conf(self) -> Optional["AppConfig"]:
        """Return the bound application configuration object.

        ### Returns:
        Optional[AppConfig] - Application configuration object or `None`.
        """
        return self._get_data(key=Keys.CONF, default_value=None)

    @conf.setter
    def conf(self, conf: "AppConfig") -> None:
        """Store the application configuration object.

        ### Arguments:
        * conf: AppConfig - Application configuration object.
        """
        from libs import AppConfig

        self._set_data(key=Keys.CONF, value=conf, set_default_type=AppConfig)


class ProjectClassMixin(LogsMixin, ConfigMixin, AppNameMixin):
    """Compose mixins used by the daemon core."""


class ModuleMixin(
    ConfigHandlerMixin, ConfigSectionMixin, LogsMixin, ComMixin, AppNameMixin
):
    """Compose mixins used by communication and task modules."""

    # #[CONSTANTS]#####################################################################
    class Keys(object, metaclass=ReadOnlyClass):
        """Define internal key names used by module runtime state."""

        DEBUG: str = "debug"
        VERBOSE: str = "verbose"

    # #[PROTECTED PROPERTIES]##########################################################
    @property
    def _bm_debug(self) -> bool:
        """Return the module debug flag.

        ### Returns:
        bool - Effective debug flag derived from runtime state and configuration.
        """

        cfh_debug: Optional[bool] = (
            self._cfh.get(self._section, ModuleMixin.Keys.DEBUG)
            if self._cfh and self._section
            else None
        )
        debug: Optional[bool] = self._get_data(key=Keys.DEBUG, default_value=None)

        if debug is None:
            self._set_data(key=Keys.DEBUG, value=False, set_default_type=bool)
            debug = False
        if cfh_debug is not None:
            return cfh_debug or debug
        return debug

    @_bm_debug.setter
    def _bm_debug(self, debug: bool) -> None:
        """Store the module debug flag.

        ### Arguments:
        * debug: bool - Debug flag value.
        """
        self._set_data(key=Keys.DEBUG, value=debug, set_default_type=bool)

    @property
    def _module_conf(self) -> Optional[ModuleConfigMixin]:
        """Return the typed module configuration adapter.

        ### Returns:
        Optional[ModuleConfigMixin] - Module configuration adapter or `None`.
        """
        out: Optional[ModuleConfigMixin] = self._get_data(
            key=ModuleConfigMixin.Keys.MODULE_CONF, default_value=None
        )
        return out

    @_module_conf.setter
    def _module_conf(self, value: ModuleConfigMixin) -> None:
        """Store the typed module configuration adapter.

        ### Arguments:
        * value: ModuleConfigMixin - Module configuration adapter.
        """
        self._set_data(
            key=ModuleConfigMixin.Keys.MODULE_CONF,
            value=value,
            set_default_type=ModuleConfigMixin,
        )

    @property
    def _verbose(self) -> bool:
        """Return the module verbose flag.

        ### Returns:
        bool - Effective verbose flag derived from runtime state and configuration.
        """
        cfh_verbose: Optional[bool] = (
            self._cfh.get(self._section, ModuleMixin.Keys.VERBOSE)
            if self._cfh and self._section
            else None
        )
        verbose: Optional[bool] = self._get_data(key=Keys.VERBOSE, default_value=None)

        if verbose is None:
            self._set_data(key=Keys.VERBOSE, value=False, set_default_type=bool)
            verbose = False
        if cfh_verbose is not None:
            return cfh_verbose or verbose
        return verbose

    @_verbose.setter
    def _verbose(self, verbose: bool) -> None:
        """Store the module verbose flag.

        ### Arguments:
        * verbose: bool - Verbose flag value.
        """
        self._set_data(key=Keys.VERBOSE, value=verbose, set_default_type=bool)


class DebugMixin(BData):
    """Mixin that exposes a simple debug flag property."""

    # #[PROTECTED PROPERTIES]##########################################################
    @property
    def _debug(self) -> bool:
        """Return the current debug flag.

        ### Returns:
        bool - Debug flag value.
        """
        out: Optional[bool] = self._get_data(key=Keys.DEBUG, default_value=None)
        if out is None:
            self._set_data(key=Keys.DEBUG, value=False, set_default_type=bool)
            out = False
        return out

    @_debug.setter
    def _debug(self, debug: bool) -> None:
        """Store the current debug flag.

        ### Arguments:
        * debug: bool - Debug flag value.
        """
        self._set_data(key=Keys.DEBUG, value=debug, set_default_type=bool)


class VerboseMixin(BData):
    """Mixin that exposes a simple verbose flag property."""

    # #[PROTECTED PROPERTIES]##########################################################
    @property
    def _verbose(self) -> bool:
        """Return the current verbose flag.

        ### Returns:
        bool - Verbose flag value.
        """
        out: Optional[bool] = self._get_data(key=Keys.VERBOSE, default_value=None)
        if out is None:
            self._set_data(key=Keys.VERBOSE, value=False, set_default_type=bool)
            out = False
        return out

    @_verbose.setter
    def _verbose(self, verbose: bool) -> None:
        """Store the current verbose flag.

        ### Arguments:
        * verbose: bool - Verbose flag value.
        """
        self._set_data(key=Keys.VERBOSE, value=verbose, set_default_type=bool)


class ThProcessorMixin(ComMixin, VerboseMixin, LogsMixin):
    """Compose mixins used by threaded communication processors."""


# #[EOF]#######################################################################
