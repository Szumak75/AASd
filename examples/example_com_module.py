# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 23.11.2023

  Purpose:
"""

import time

from inspect import currentframe
from typing import Dict, List, Optional, Union, Any
from threading import Thread, Event
from queue import Queue, Empty, Full
from email.message import EmailMessage
from email.utils import make_msgid

from jsktoolbox.libs.base_th import ThBaseObject
from jsktoolbox.logstool.logs import LoggerClient, LoggerQueue
from jsktoolbox.configtool.main import Config as ConfigTool
from jsktoolbox.attribtool import ReadOnlyClass
from jsktoolbox.raisetool import Raise
from jsktoolbox.datetool import Timestamp

from libs.base.classes import BModule
from libs.interfaces.modules import IComModule
from libs.base.classes import BModuleConfig
from libs.templates.modules import TemplateConfigItem
from libs.com.message import Message, Multipart
from libs.tools.datetool import MDateTime


class _Keys(object, metaclass=ReadOnlyClass):
    """Private Keys definition class.

    For internal purpose only.
    """

    MODCONF = "__MODULE_CONF__"
    SLEEP_PERIOD = "sleep_period"
    CHANNEL = "channel"


class _ModuleConf(BModuleConfig):
    """Module Config private class."""

    @property
    def channel(self) -> int:
        """Return channel var."""
        var = self._get(varname=_Keys.CHANNEL)
        if var is not None and not isinstance(var, int):
            raise Raise.error(
                "Expected int type.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        return var

    @property
    def sleep_period(self) -> Optional[float]:
        """Return sleep_period var."""
        var = self._get(varname=_Keys.SLEEP_PERIOD)
        if var is None:
            return None
        if not isinstance(var, (int, float)):
            raise Raise.error(
                "Expected float type.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        return float(var)


class MExample(Thread, ThBaseObject, BModule, IComModule):
    """Example alert module."""

    def __init__(
        self,
        conf: ConfigTool,
        qlog: LoggerQueue,
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

    def _apply_config(self) -> bool:
        """Apply config from module_conf"""
        if self.module_conf is None:
            return False

        try:
            if self.module_conf.sleep_period is not None:
                self.sleep_period = self.module_conf.sleep_period
            # channel
            if not self.module_conf.channel:
                self.logs.message_critical = (
                    f"required variable '{_Keys.CHANNEL}' not set, exiting..."
                )
                self.stop()

        except Exception as ex:
            self.logs.message_critical = f"[{self._f_name}] {ex}"
            return False
        if self._debug:
            self.logs.message_debug = "configuration processing complete"
        return True

    def __send_message(self, message: Message) -> bool:
        """Try to send message."""
        out = False

        return out

    def run(self) -> None:
        """Main loop."""
        self.logs.message_notice = "starting..."

        if self.module_conf is None or self.qcom is None:
            return None

        # initialize local vars

        # initialization variables from config file
        if not self._apply_config():
            self.logs.message_error = "configuration error"
            return

        if self.debug:
            self.logs.message_debug = "configuration processing complete"
            self.logs.message_debug = "entering to the main loop"

        # starting module loop
        while not self.stopped:
            # read from queue, process message if received
            try:
                message: Message = self.qcom.get(block=True, timeout=0.1)
                if message is None:
                    continue
                # try to process message
                try:
                    if not self.__send_message(message):
                        # TODO: not implemented
                        pass
                except Exception as ex:
                    self.logs.message_warning = "error processing message"
                    if self.debug:
                        self.logs.message_debug = f"[{self._f_name}] {ex}"
                finally:
                    self.qcom.task_done()

            except Empty:
                pass
            except Exception as ex:
                self.logs.message_critical = f'error while processing message: "{ex}"'

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
            self.logs.message_debug = "stop signal received"
        if self._stop_event:
            self._stop_event.set()

    @property
    def debug(self) -> bool:
        """Return debug flag."""
        if self._debug is not None:
            return self._debug
        return False

    @property
    def verbose(self) -> bool:
        """Return verbose flag."""
        return self._verbose

    @property
    def stopped(self) -> bool:
        """Return stop flag."""
        if self._stop_event:
            return self._stop_event.is_set()
        return True

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
        out.append(TemplateConfigItem(desc="Example alert configuration module."))
        out.append(TemplateConfigItem(desc="Variables:"))
        out.append(
            TemplateConfigItem(
                desc=f"{_Keys.CHANNEL} [int] - unique channel for communication method (for example: 100)"
            )
        )
        out.append(TemplateConfigItem(varname=_Keys.CHANNEL, value=100))

        return out


# #[EOF]#######################################################################
