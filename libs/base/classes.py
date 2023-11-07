# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 06.11.2023

  Purpose:
"""

from inspect import currentframe
from typing import Optional
from queue import Queue, SimpleQueue

from jsktoolbox.attribtool import NoDynamicAttributes
from jsktoolbox.raisetool import Raise
from jsktoolbox.libs.base_data import BData
from jsktoolbox.logstool.logs import LoggerClient
from jsktoolbox.configtool.main import Config as ConfigTool

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
                self.c_name,
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
        self._data[Keys.SECTION] = section_name


class BModuleConfig(BConfigHandler, BConfigSection):
    """Base class for module config classes."""

    def __init__(self, cfh: ConfigTool, section: str) -> None:
        """Constructor."""
        self._cfh = cfh
        self._section = section


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
                self.c_name,
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
                self.c_name,
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
                self.c_name,
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


# #[EOF]#######################################################################
