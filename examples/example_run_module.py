# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 23.11.2023

  Purpose:
"""

import time
from inspect import currentframe
from typing import Dict, List, Optional, Any
from threading import Thread, Event
from queue import Queue

from jsktoolbox.libs.base_th import ThBaseObject
from jsktoolbox.logstool.logs import LoggerClient, LoggerQueue
from jsktoolbox.configtool.main import Config as ConfigTool
from jsktoolbox.attribtool import ReadOnlyClass
from jsktoolbox.raisetool import Raise
from jsktoolbox.datetool import Timestamp

from libs.base.classes import BModule
from libs.interfaces.modules import IRunModule
from libs.base.classes import BModuleConfig
from libs.interfaces.conf import IModuleConfig
from libs.templates.modules import TemplateConfigItem
from libs.com.message import Message, Multipart, Channel


class _Keys(object, metaclass=ReadOnlyClass):
    """Private Keys definition class.

    For internal purpose only.
    """

    MODCONF = "__MODULE_CONF__"
    SLEEP_PERIOD = "sleep_period"
    MESSAGE_CHANNEL = "message_channel"


class _ModuleConf(IModuleConfig, BModuleConfig):
    """Module Config private class."""

    def _get(self, varname: str) -> Any:
        """Get variable from config."""
        return self._cfh.get(self._section, varname)

    @property
    def message_channel(self) -> Optional[List[str]]:
        """Return message channel list."""
        var = self._get(varname=_Keys.MESSAGE_CHANNEL)
        if var is not None and not isinstance(var, List):
            raise Raise.error(
                "Expected list type.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        return var

    @property
    def sleep_period(self) -> float:
        """Return sleep_period var."""
        var = self._get(varname=_Keys.SLEEP_PERIOD)
        if not isinstance(var, (int, float)):
            raise Raise.error(
                "Expected float type.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        return float(var)


class MExample(Thread, ThBaseObject, BModule, IRunModule):
    """Example module."""

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
        Thread.__init__(self, name=self._c_name)
        self._stop_event = Event()
        self.daemon = True
        self.sleep_period = 5.0

        # configuration section name
        self._section = self._c_name
        self._cfh = conf
        self._data[_Keys.MODCONF] = _ModuleConf(self._cfh, self._section)

        # logging level
        self._debug = debug
        self._verbose = verbose

        # logger client initialization
        self.logs = LoggerClient(queue=qlog, name=self._c_name)

        # communication queue
        self.qcom = qcom

    def _apply_config(self) -> bool:
        """Apply config from module_conf"""
        try:
            if self.module_conf.sleep_period:
                self.sleep_period = self.module_conf.sleep_period
        except Exception as ex:
            self.logs.message_critical = f"{ex}"
            return False
        return True

    def run(self) -> None:
        """Main loop."""
        self.logs.message_notice = "starting..."

        # initialization local variables
        channel = Channel(self.module_conf.message_channel)

        # initialization variables from config file
        if not self._apply_config():
            self.logs.message_error = "configuration error."
            return

        if self.debug:
            self.logs.message_debug = "configuration processing complete"
            self.logs.message_debug = "entering to the main loop"

        # starting module loop
        while not self.stopped:
            # TODO: not implemented
            # TODO: do something, build a message if necessary, put it in the qcom queue

            # sleep time
            self.sleep()

        # exiting from loop
        self.logs.message_notice = "exit"

    def sleep(self) -> None:
        """Sleep interval for main loop."""
        sbreak = Timestamp.now + self.sleep_period
        while not self.stopped and sbreak > Timestamp.now:
            time.sleep(0.2)

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
            TemplateConfigItem(desc="Example configuration for module.")
        )
        out.append(
            TemplateConfigItem(
                desc=f"'{_Keys.SLEEP_PERIOD}' [float], which determines the length of the break"
            )
        )
        out.append(
            TemplateConfigItem(
                desc="between subsequent executions of the program's main loop"
            )
        )
        out.append(
            TemplateConfigItem(
                desc=f"'{_Keys.MESSAGE_CHANNEL}' [List[str]], comma separated communication channels list,"
            )
        )
        out.append(
            TemplateConfigItem(
                desc="['nr(:default delay=0)'|'nr1:delay', 'nr2:delay']"
            )
        )
        out.append(
            TemplateConfigItem(
                desc="where 'delay' means the time between generating"
            )
        )
        out.append(
            TemplateConfigItem(
                desc="subsequent notifications for a given channel and can be given in"
            )
        )
        out.append(
            TemplateConfigItem(
                desc="seconds or a numerical value with the suffix 's|m|h|d|w'"
            )
        )
        out.append(
            TemplateConfigItem(
                varname=_Keys.SLEEP_PERIOD, value=3.25, desc="[second]"
            )
        )
        out.append(
            TemplateConfigItem(
                varname=_Keys.MESSAGE_CHANNEL,
                value=["1"],
            )
        )
        return out


# #[EOF]#######################################################################
