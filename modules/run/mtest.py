# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 07.11.2023

  Purpose: Test
"""

import time
from typing import Dict, List, Optional, Any
from threading import Thread, Event
from queue import Queue

from jsktoolbox.libs.base_th import ThBaseObject
from jsktoolbox.logstool.logs import LoggerClient, LoggerQueue
from jsktoolbox.configtool.main import Config as ConfigTool
from jsktoolbox.attribtool import ReadOnlyClass

from libs.base.classes import BModule
from libs.interfaces.modules import IRunModule
from libs.base.classes import BModuleConfig
from libs.interfaces.conf import IModuleConfig
from libs.templates.modules import TemplateConfigItem


class _Keys(object, metaclass=ReadOnlyClass):
    """Private Keys definition class.

    For internal purpose only.
    """

    MODCONF = "__MODULE_CONF__"
    SLEEP_PERIOD = "sleep_period"


class _ModuleConf(IModuleConfig, BModuleConfig):
    """Module Config private class."""

    def _get(self, varname: str) -> Any:
        """Get variable from config."""
        return self._cfh.get(self._section, varname)

    @property
    def sleep_period(self) -> float:
        """Return sleep_period var."""
        return self._get(varname=_Keys.SLEEP_PERIOD)


class MTest(Thread, ThBaseObject, BModule, IRunModule):
    """Test module."""

    def __init__(
        self,
        conf: ConfigTool,
        qlog: LoggerQueue,
        qcom: Queue,
        verbose: bool = False,
        debug: bool = False,
    ) -> None:
        """Constructor."""
        # Thread initialization
        Thread.__init__(self, name=self.c_name)
        self._stop_event = Event()
        self.daemon = True
        self.sleep_period = 5.0

        # configuration section name
        self._section = self.c_name
        self._cfh = conf
        self._data[_Keys.MODCONF] = _ModuleConf(self._cfh, self._section)

        # logging level
        self._debug = debug
        self._verbose = verbose

        # logger client initialization
        self.logs = LoggerClient(queue=qlog, name=self.c_name)

    def _apply_config(self) -> None:
        """Apply config from module_conf"""
        if self.module_conf.sleep_period:
            self.sleep_period = self.module_conf.sleep_period

    def run(self) -> None:
        """Main loop."""
        # initialization local variables
        count = 0
        # initialization variables from config file
        self._apply_config()
        # starting module loop
        while not self.stopped:
            # someting
            count += 1
            self.logs.message_info = f"ping {count:>04d}"
            time.sleep(self.sleep_period)
        # exiting from loop
        if self._debug:
            self.logs.message_debug = "exiting from loop."

    def stop(self) -> None:
        """Set stop event."""
        if self._debug:
            self.logs.message_debug = "stop signal received."
        self._stop_event.set()

    @property
    def debug(self) -> bool:
        """Return debug flag."""
        return self._debug

    @property
    def verbose(self) -> bool:
        """Return verbose flag."""
        return self._verbose

    @property
    def stopped(self) -> bool:
        """Return stop flag."""
        return self._stop_event.is_set()

    @property
    def module_conf(self) -> Optional[_ModuleConf]:
        """Return module conf object."""
        return self._data[_Keys.MODCONF]

    @classmethod
    def template_module_name(cls) -> str:
        """Return module name for configuration builder."""
        return cls.__name__.lower()

    @classmethod
    def template_module_variables(cls) -> List:
        """Return configuration variables template."""
        out = []
        # item format:
        # TemplateConfigItem()
        out.append(
            TemplateConfigItem(desc="Example configuration for test module.")
        )
        out.append(
            TemplateConfigItem(
                desc="This module is for testing purposes only."
            )
        )
        out.append(
            TemplateConfigItem(
                desc="It works by periodically sending messages to the logger."
            )
        )
        out.append(
            TemplateConfigItem(desc="the module defines only one variable:")
        )
        out.append(
            TemplateConfigItem(
                desc="'sleep_period' [float], which determines the length of the break"
            )
        )
        out.append(
            TemplateConfigItem(
                desc="between subsequent executions of the program's main loop"
            )
        )
        out.append(
            TemplateConfigItem(
                varname=_Keys.SLEEP_PERIOD, value=3.25, desc="[second]"
            )
        )
        return out


# #[EOF]#######################################################################
