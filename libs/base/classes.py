# -*- coding: UTF-8 -*-
"""
Shared project base classes.

Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 2023-11-06

Purpose: Provide shared mixin-style helper classes used by the daemon and runtime modules.
"""

import os

from inspect import currentframe
from typing import Optional, List, Any, Union
from queue import Queue

from jsktoolbox.raisetool import Raise
from jsktoolbox.basetool.data import BData
from jsktoolbox.logstool.logs import LoggerClient
from jsktoolbox.configtool.main import Config as ConfigTool
from jsktoolbox.attribtool import ReadOnlyClass

from libs.keys import Keys
from libs.app import AppName


class BAppName(BData):
    """Mixin that exposes a typed application identity property.

    This class behaves as a reusable mixin. The current `B*` naming is kept for
    compatibility, but the naming should be refactored in the future to make the
    mixin role explicit.
    """

    @property
    def application(self) -> AppName:
        """Return the application identity object.

        ### Returns:
        AppName - Runtime application identity container.
        """
        return self._get_data(key=Keys.APP_NAME)  # type: ignore

    @application.setter
    def application(self, value: AppName) -> None:
        """Store the application identity object.

        ### Arguments:
        * value: AppName - Runtime application identity container.
        """
        self._set_data(key=Keys.APP_NAME, value=value, set_default_type=AppName)


class BConfigHandler(BData):
    """Mixin that exposes a typed configuration handler property."""

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


class BConfigSection(BData):
    """Mixin that exposes a typed configuration section property."""

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


class BModuleConfig(BConfigHandler, BConfigSection):
    """Mixin-style adapter that provides typed access to module configuration."""

    class Keys(object, metaclass=ReadOnlyClass):
        """Define shared configuration key names for module settings."""

        CHANNEL: str = "channel"
        MESSAGE_CHANNEL: str = "message_channel"
        MODULE_CONF: str = "__MODULE_CONF__"
        SLEEP_PERIOD: str = "sleep_period"

    def __init__(self, cfh: ConfigTool, section: Optional[str]) -> None:
        """Initialize the module configuration adapter.

        ### Arguments:
        * cfh: ConfigTool - Configuration handler used for value lookups.
        * section: Optional[str] - Configuration section bound to the module.
        """
        self._cfh = cfh
        self._section = section

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

    @property
    def channel(self) -> Optional[int]:
        """Return the communication channel configured for a module.

        ### Returns:
        Optional[int] - Communication channel number or `None`.

        ### Raises:
        * TypeError: If the configured value is not an integer.
        """
        var: Optional[int] = self._get(varname=BModuleConfig.Keys.CHANNEL)
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
        var = self._get(varname=BModuleConfig.Keys.MESSAGE_CHANNEL)
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
            varname=BModuleConfig.Keys.SLEEP_PERIOD
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


class BImporter(BData):
    """Mixin that discovers and imports runtime modules using the current naming convention.

    The loader expects module file names to start with `m` and derives the class
    name from the file name using the current project convention.
    """

    def import_name_list(self, package: str) -> List:
        """Return importable module file names from the selected package.

        ### Arguments:
        * package: str - Dotted package path relative to the repository root.

        ### Returns:
        List - Sorted list of module names without the `.py` suffix.

        ### Raises:
        * TypeError: If `package` is not a string.
        """
        out = []
        if not isinstance(package, str):
            raise Raise.error(
                f"Expected package name as string type, received: '{type(package)}'.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        dirname: str = os.path.join("./", *package.split("."))
        with os.scandir(dirname) as itr:
            for entry in itr:
                if (
                    entry.name.startswith("m")
                    and entry.name.endswith("y")
                    and entry.name.find(".py") > 0
                ):
                    out.append(entry.name[:-3])
        return sorted(out)

    def import_module(self, package: str, name: str) -> Optional[object]:
        """Import a runtime module class from the selected package.

        ### Arguments:
        * package: str - Dotted package path relative to the repository root.
        * name: str - Module file name without the `.py` suffix.

        ### Returns:
        Optional[object] - Imported class object or `None` when import fails.
        """
        modulename: str = f"{package}.{name}"
        name = f"{name[:2].upper()}{name[2:]}"
        try:
            module = __import__(modulename, globals(), locals(), [name])
        except ImportError:
            return None
        return getattr(module, name)


class BLogs(BData):
    """Mixin that exposes a typed logger client property."""

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
        return self._get_data(key=Keys.CLOG)  # type: ignore

    @logs.setter
    def logs(self, logs: LoggerClient) -> None:
        """Store the logger client for the current object.

        ### Arguments:
        * logs: LoggerClient - Logger client instance.
        """
        self._set_data(key=Keys.CLOG, value=logs, set_default_type=LoggerClient)


class BCom(BData):
    """Mixin that exposes a typed communication queue property."""

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


class BConfig(BData):
    """Mixin that exposes a typed application configuration property."""

    from libs.conf import AppConfig

    @property
    def conf(self) -> Optional[AppConfig]:
        """Return the bound application configuration object.

        ### Returns:
        Optional[AppConfig] - Application configuration object or `None`.
        """
        return self._get_data(key=Keys.CONF, default_value=None)

    @conf.setter
    def conf(self, conf: AppConfig) -> None:
        """Store the application configuration object.

        ### Arguments:
        * conf: AppConfig - Application configuration object.
        """
        from libs.conf import AppConfig

        self._set_data(key=Keys.CONF, value=conf, set_default_type=AppConfig)


class BProjectClass(BLogs, BConfig, BAppName):
    """Compose mixins used by the daemon core.

    The current name suggests a concrete base type, but this class mostly groups
    mixin behavior and should be revisited during future naming cleanup.
    """


class BModule(BConfigHandler, BConfigSection, BLogs, BCom, BAppName):
    """Compose mixins used by communication and task modules."""

    class Keys(object, metaclass=ReadOnlyClass):
        """Define internal key names used by module runtime state."""

        DEBUG: str = "debug"
        VERBOSE: str = "verbose"

    @property
    def _bm_debug(self) -> bool:
        """Return the module debug flag.

        ### Returns:
        bool - Effective debug flag derived from runtime state and configuration.
        """
        if self._get_data(key=Keys.DEBUG, default_value=None) is None:
            self._set_data(key=Keys.DEBUG, value=False, set_default_type=bool)
        if (
            self._cfh
            and self._section
            and self._cfh.get(self._section, BModule.Keys.DEBUG) is not None
        ):
            return self._cfh.get(self._section, BModule.Keys.DEBUG) or self._get_data(key=Keys.DEBUG)  # type: ignore
        return self._get_data(key=Keys.DEBUG)  # type: ignore

    @_bm_debug.setter
    def _bm_debug(self, debug: bool) -> None:
        """Store the module debug flag.

        ### Arguments:
        * debug: bool - Debug flag value.
        """
        self._set_data(key=Keys.DEBUG, value=debug, set_default_type=bool)

    @property
    def _module_conf(self) -> Optional[BModuleConfig]:
        """Return the typed module configuration adapter.

        ### Returns:
        Optional[BModuleConfig] - Module configuration adapter or `None`.
        """
        return self._get_data(
            key=BModuleConfig.Keys.MODULE_CONF, default_value=None
        )  # type: ignore

    @_module_conf.setter
    def _module_conf(self, value: BModuleConfig) -> None:
        """Store the typed module configuration adapter.

        ### Arguments:
        * value: BModuleConfig - Module configuration adapter.
        """
        self._set_data(
            key=BModuleConfig.Keys.MODULE_CONF,
            value=value,
            set_default_type=BModuleConfig,
        )

    @property
    def _verbose(self) -> bool:
        """Return the module verbose flag.

        ### Returns:
        bool - Effective verbose flag derived from runtime state and configuration.
        """
        if self._get_data(key=Keys.VERBOSE, default_value=None) is None:
            self._set_data(key=Keys.VERBOSE, value=False, set_default_type=bool)
        if (
            self._cfh
            and self._section
            and self._cfh.get(self._section, BModule.Keys.VERBOSE) is not None
        ):
            return self._cfh.get(self._section, BModule.Keys.VERBOSE) or self._get_data(key=Keys.VERBOSE)  # type: ignore
        return self._get_data(key=Keys.VERBOSE)  # type: ignore

    @_verbose.setter
    def _verbose(self, verbose: bool) -> None:
        """Store the module verbose flag.

        ### Arguments:
        * verbose: bool - Verbose flag value.
        """
        self._set_data(key=Keys.VERBOSE, value=verbose, set_default_type=bool)


class BDebug(BData):
    """Mixin that exposes a simple debug flag property."""

    @property
    def _debug(self) -> bool:
        """Return the current debug flag.

        ### Returns:
        bool - Debug flag value.
        """
        return self._get_data(key=Keys.DEBUG, default_value=False)  # type: ignore

    @_debug.setter
    def _debug(self, debug: bool) -> None:
        """Store the current debug flag.

        ### Arguments:
        * debug: bool - Debug flag value.
        """
        self._set_data(key=Keys.DEBUG, value=debug, set_default_type=bool)


class BVerbose(BData):
    """Mixin that exposes a simple verbose flag property."""

    @property
    def _verbose(self) -> bool:
        """Return the current verbose flag.

        ### Returns:
        bool - Verbose flag value.
        """
        return self._get_data(key=Keys.VERBOSE, default_value=False)  # type: ignore

    @_verbose.setter
    def _verbose(self, verbose: bool) -> None:
        """Store the current verbose flag.

        ### Arguments:
        * verbose: bool - Verbose flag value.
        """
        self._set_data(key=Keys.VERBOSE, value=verbose, set_default_type=bool)


class BThProcessor(BCom, BVerbose, BLogs):
    """Compose mixins used by threaded communication processors."""


# #[EOF]#######################################################################
