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

from libs.base.classes import BModule
from libs.interfaces.modules import IRunModule
from libs.base.classes import BModuleConfig
from libs.interfaces.conf import IModuleConfig
from libs.templates.modules import TemplateConfigItem


class _ModuleConf(IModuleConfig, BModuleConfig):
    """Module Config private class."""

    def _get(self, varname: str) -> Any:
        """Get variable from config."""
        return self._cfh.get(self._section, varname)


class MRTest(Thread, ThBaseObject, BModule, IRunModule):
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

        # logging level
        self._debug = debug
        self._verbose = verbose

        # logger client initialization
        self.logs = LoggerClient(queue=qlog, name=self.c_name)

    def run(self) -> None:
        """Main loop."""

        while not self.stopped:
            # someting
            self.logs.message_info = "pik"
            time.sleep(self.sleep_period)

    def stop(self) -> None:
        """Set stop event."""
        self._stop_event.set()

    @property
    def stopped(self) -> bool:
        """Return stop flag."""
        return self._stop_event.is_set()

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
        out.append(TemplateConfigItem(desc="Example configuration for test module."))
        out.append(TemplateConfigItem(desc="This module is for testing purposes only."))
        out.append(
            TemplateConfigItem(
                desc="It works by periodically sending messages to the logger."
            )
        )
        out.append(TemplateConfigItem(desc="the module defines only one configuration"))
        out.append(
            TemplateConfigItem(
                desc="variable: 'sleep_period' [float], which determines the length of "
            )
        )
        out.append(
            TemplateConfigItem(
                desc="the break between subsequent executions of the program's main loop"
            )
        )
        out.append(TemplateConfigItem(varname="sleep_period", value=3.25))
        return out


# #[EOF]#######################################################################
