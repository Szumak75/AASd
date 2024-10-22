# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 06.11.2023

  Purpose: base classes for project.
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


class BConfigHandler(BData):
    """Base class for Config handler."""

    @property
    def _cfh(self) -> Optional[ConfigTool]:
        """Return config handler object."""
        return self._get_data(key=Keys.CFH, default_value=None)

    @_cfh.setter
    def _cfh(self, config_handler: Optional[ConfigTool]) -> None:
        """Set config handler."""
        self._set_data(
            key=Keys.CFH, value=config_handler, set_default_type=Optional[ConfigTool]
        )


class BConfigSection(BData):
    """Base class for Config handler."""

    @property
    def _section(self) -> Optional[str]:
        """Return section name."""
        return self._get_data(key=Keys.SECTION, default_value=None)

    @_section.setter
    def _section(self, section_name: Optional[str]) -> None:
        """Set section name."""
        sn: Optional[str] = None
        if section_name and isinstance(section_name, str):
            sn = section_name.lower()
        else:
            sn = section_name
        self._set_data(key=Keys.SECTION, value=sn, set_default_type=Optional[str])


class BModuleConfig(BConfigHandler, BConfigSection):
    """Base class for module config classes."""

    class Keys(object, metaclass=ReadOnlyClass):
        """Keys definition container class."""

        CHANNEL: str = "channel"
        MESSAGE_CHANNEL: str = "message_channel"
        MODULE_CONF: str = "__MODULE_CONF__"
        SLEEP_PERIOD: str = "sleep_period"

    def __init__(self, cfh: ConfigTool, section: Optional[str]) -> None:
        """Constructor."""
        self._cfh = cfh
        self._section = section

    def _get(self, varname: str) -> Any:
        """Get variable from config."""
        if self._cfh and self._section:
            return self._cfh.get(self._section, varname)
        return None

    @property
    def channel(self) -> Optional[int]:
        """Return channel var for communication modules."""
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
        """Return message channel list for running modules."""
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
        """Return sleep_period var."""
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
    """Base class for modules importer.

    Requirements:

    The module filename is the name of the class to be imported and must begin
    with the letter 'm'.
    The class name begins with the letter 'M', the second letter must be capitalized,
    all other characters must be lowercase.
    This is an important condition for the method that determines the name of
    the class to be imported.
    """

    def import_name_list(self, package: str) -> List:
        """Get modules list."""
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
        """Try to import module.

        Returns: imported module or None.
        """
        modulename: str = f"{package}.{name}"
        name = f"{name[:2].upper()}{name[2:]}"
        try:
            module = __import__(modulename, globals(), locals(), [name])
        except ImportError:
            return None
        return getattr(module, name)


class BLogs(BData):
    """Base class for LoggerClient property."""

    @property
    def logs(self) -> LoggerClient:
        """Return LoggerClient object or None."""
        if self._get_data(key=Keys.CLOG, default_value=None) is None:
            self._set_data(
                key=Keys.CLOG, value=LoggerClient(), set_default_type=LoggerClient
            )
        return self._get_data(key=Keys.CLOG)  # type: ignore

    @logs.setter
    def logs(self, logs: LoggerClient) -> None:
        """Set LoggerClient."""
        self._set_data(key=Keys.CLOG, value=logs, set_default_type=LoggerClient)


class BCom(BData):
    """Base class for communication queue."""

    @property
    def qcom(self) -> Optional[Queue]:
        """Return Queue object or None."""
        return self._get_data(key=Keys.QCOM, default_value=None)

    @qcom.setter
    def qcom(self, queue: Queue) -> None:
        """Set communication queue."""
        self._set_data(key=Keys.QCOM, value=queue, set_default_type=Queue)


class BConfig(BData):
    """Base class for Config property."""

    from libs.conf import Config

    @property
    def conf(self) -> Optional[Config]:
        """Return Config class object."""
        return self._get_data(key=Keys.CONF, default_value=None)

    @conf.setter
    def conf(self, conf: Config) -> None:
        """Set Config class object."""
        from libs.conf import Config

        self._set_data(key=Keys.CONF, value=conf, set_default_type=Config)


class BProjectClass(BLogs, BConfig):
    """Base Project class.

    Properties:
    - _c_name: str
    - _f_name: str
    - conf: Optional[Config]
    - logs: Optional[LoggerClient]
    """


class BModule(BConfigHandler, BConfigSection, BLogs, BCom):
    """Base class for module classes.

    Properties:
    - _c_name: str
    - _f_name: str
    - _cfh: ConfigTool
    - _section: str
    - logs: LoggerClient
    - qcom: Queue
    """

    class Keys(object, metaclass=ReadOnlyClass):
        """Keys definition container class."""

        DEBUG: str = "debug"
        VERBOSE: str = "verbose"

    @property
    def _debug(self) -> bool:
        """Return debug flag."""
        if self._get_data(key=Keys.DEBUG, default_value=None) is None:
            self._set_data(key=Keys.DEBUG, value=False, set_default_type=bool)
        if (
            self._cfh
            and self._section
            and self._cfh.get(self._section, BModule.Keys.DEBUG) is not None
        ):
            return self._cfh.get(self._section, BModule.Keys.DEBUG) or self._get_data(key=Keys.DEBUG)  # type: ignore
        return self._get_data(key=Keys.DEBUG)  # type: ignore

    @_debug.setter
    def _debug(self, debug: bool) -> None:
        """Set debug flag."""
        self._set_data(key=Keys.DEBUG, value=debug, set_default_type=bool)

    @property
    def _module_conf(self) -> Optional[BModuleConfig]:
        """Return module configuration."""
        return self._get_data(
            key=BModuleConfig.Keys.MODULE_CONF, default_value=None
        )  # type: ignore

    @_module_conf.setter
    def _module_conf(self, value: BModuleConfig) -> None:
        """Set module configuration."""
        self._set_data(
            key=BModuleConfig.Keys.MODULE_CONF,
            value=value,
            set_default_type=BModuleConfig,
        )

    @property
    def _verbose(self) -> bool:
        """Return verbose flag."""
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
        """Set verbose flag."""
        self._set_data(key=Keys.VERBOSE, value=verbose, set_default_type=bool)


class BDebug(BData):
    """Base class for debug flags."""

    @property
    def _debug(self) -> bool:
        """Return debug flag."""
        return self._get_data(key=Keys.DEBUG, default_value=False)  # type: ignore

    @_debug.setter
    def _debug(self, debug: bool) -> None:
        """Set debug flag."""
        self._set_data(key=Keys.DEBUG, value=debug, set_default_type=bool)


class BVerbose(BData):
    """Base class for verbose flags."""

    @property
    def _verbose(self) -> bool:
        """Return verbose flag."""
        return self._get_data(key=Keys.VERBOSE, default_value=False)  # type: ignore

    @_verbose.setter
    def _verbose(self, verbose: bool) -> None:
        """Set verbose flag."""
        self._set_data(key=Keys.VERBOSE, value=verbose, set_default_type=bool)


class BThProcessor(BCom, BVerbose, BLogs):
    """Base class for ThProcessor."""


# #[EOF]#######################################################################
