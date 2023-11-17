# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 06.11.2023

  Purpose:
"""

import os

from inspect import currentframe
from typing import Optional, List
from queue import Queue, SimpleQueue

from jsktoolbox.attribtool import NoDynamicAttributes
from jsktoolbox.raisetool import Raise
from jsktoolbox.libs.base_data import BData
from jsktoolbox.logstool.logs import LoggerClient
from jsktoolbox.configtool.main import Config as ConfigTool

from libs.keys import Keys


class BClasses(BData, NoDynamicAttributes):
    """Base class for project."""


class BConfigHandler(BClasses):
    """Base class for Config handler."""

    @property
    def _cfh(self) -> Optional[ConfigTool]:
        """Return config handler object."""
        if Keys.CFH not in self._data:
            self._data[Keys.CFH] = None
        return self._data[Keys.CFH]

    @_cfh.setter
    def _cfh(self, config_handler: ConfigTool) -> None:
        """Set config handler."""
        if not isinstance(config_handler, ConfigTool):
            raise Raise.error(
                f"ConfigTool type expected, '{type(config_handler)}' received.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        self._data[Keys.CFH] = config_handler


class BConfigSection(BClasses):
    """Base class for Config handler."""

    @property
    def _section(self) -> Optional[str]:
        """Return section name."""
        if Keys.SECTION not in self._data:
            self._data[Keys.SECTION] = None
        return self._data[Keys.SECTION]

    @_section.setter
    def _section(self, section_name: str) -> None:
        """Set section name."""
        self._data[Keys.SECTION] = str(section_name).lower()


class BModuleConfig(BConfigHandler, BConfigSection):
    """Base class for module config classes."""

    def __init__(self, cfh: ConfigTool, section: str) -> None:
        """Constructor."""
        self._cfh = cfh
        self._section = section


class BImporter(BClasses):
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
                f"package name as string expected, '{type(package)}' received.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        dirname = os.path.join("./", *package.split("."))
        with os.scandir(dirname) as itr:
            for entry in itr:
                if (
                    entry.name.startswith("m")
                    and entry.name.endswith("y")
                    and entry.name.find(".py") > 0
                ):
                    out.append(entry.name[:-3])
        return out

    def import_module(self, package: str, name: str) -> Optional[object]:
        """Try to import module.

        Returns: imported module or None.
        """
        modulename = f"{package}.{name}"
        name = f"{name[:2].upper()}{name[2:]}"
        try:
            module = __import__(modulename, globals(), locals(), [name])
        except ImportError:
            return None
        return getattr(module, name)


class BLogs(BClasses):
    """Base class for LoggerClient property."""

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
                self._c_name,
                currentframe(),
            )
        self._data[Keys.CLOG] = logs


class BCom(BClasses):
    """Base class for communication queue."""

    @property
    def qcom(self) -> Optional[Queue]:
        """Return Queue object or None."""
        if Keys.QCOM not in self._data:
            self._data[Keys.QCOM] = None
        return self._data[Keys.QCOM]

    @qcom.setter
    def qcom(self, queue: Queue) -> None:
        """Set communication queue."""
        if not isinstance(queue, Queue):
            raise Raise.error(
                f"Queue type expected, '{type(logs)}' received.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        self._data[Keys.QCOM] = queue


class BConfig(BClasses):
    """Base class for Config property."""

    from libs.conf import Config

    @property
    def conf(self) -> Optional[Config]:
        """Return Config class object."""
        if Keys.CONF not in self._data:
            self._data[Keys.CONF] = None
        return self._data[Keys.CONF]

    @conf.setter
    def conf(self, conf_obj: Config) -> None:
        """Set Config class object."""
        from libs.conf import Config

        if not isinstance(conf_obj, Config):
            raise Raise.error(
                f"Config class object expected, '{type(conf_obj)}' received.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        self._data[Keys.CONF] = conf_obj


class BProjectClass(BLogs, BConfig):
    """Base Project class.

    Propertys:
    - c_name: str
    - f_name: str
    - conf: Optional[Config]
    - logs: Optional[LoggerClient]
    """


class BModule(BConfigHandler, BConfigSection, BLogs, BCom):
    """Base class for module classes.

    Propertys:
    - c_name: str
    - f_name: str
    - _cfh: ConfigTool
    - _section: str
    - logs: LoggerClient
    - qcom: Queue
    """

    @property
    def _debug(self) -> bool:
        """Return debug flag."""
        if Keys.DEBUG not in self._data:
            self._data[Keys.DEBUG] = False
        if self._cfh and self._cfh.get(self._section, "debug") is not None:
            return (
                self._cfh.get(self._section, "debug")
                or self._data[Keys.DEBUG]
            )
        return self._data[Keys.DEBUG]

    @_debug.setter
    def _debug(self, debug: bool) -> None:
        """Set debug flag."""
        self._data[Keys.DEBUG] = debug

    @property
    def _verbose(self) -> bool:
        """Return verbose flag."""
        if Keys.VERBOSE not in self._data:
            self._data[Keys.VERBOSE] = False
        if self._cfh and self._cfh.get(self._section, "verbose") is not None:
            return (
                self._cfh.get(self._section, "verbose")
                or self._data[Keys.VERBOSE]
            )
        return self._data[Keys.VERBOSE]

    @_verbose.setter
    def _verbose(self, verbose: bool) -> None:
        """Set verbose flag."""
        self._data[Keys.VERBOSE] = verbose


class BThProcessor(BCom, BLogs):
    """Base class for ThProcessor."""

    @property
    def _debug(self) -> bool:
        """Return debug flag."""
        if Keys.DEBUG not in self._data:
            self._data[Keys.DEBUG] = False
        return self._data[Keys.DEBUG]

    @_debug.setter
    def _debug(self, debug: bool) -> None:
        """Set debug flag."""
        self._data[Keys.DEBUG] = debug

    @property
    def _verbose(self) -> bool:
        """Return verbose flag."""
        if Keys.VERBOSE not in self._data:
            self._data[Keys.VERBOSE] = False
        return self._data[Keys.VERBOSE]

    @_verbose.setter
    def _verbose(self, verbose: bool) -> None:
        """Set verbose flag."""
        self._data[Keys.VERBOSE] = verbose


# #[EOF]#######################################################################
