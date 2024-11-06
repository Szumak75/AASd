# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 23.11.2023

  Purpose: Example communication module.
"""

import time

from inspect import currentframe
from typing import Dict, List, Optional, Union, Any
from threading import Thread, Event
from queue import Queue, Empty, Full
from email.message import EmailMessage
from email.utils import make_msgid

from jsktoolbox.basetool.threads import ThBaseObject
from jsktoolbox.basetool.data import BData
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
from libs.app import AppName


class _Keys(object, metaclass=ReadOnlyClass):
    """Private Keys definition class.

    For internal purpose only.
    """


class _ModuleConf(BModuleConfig):
    """Module Config private class."""


class MExample(Thread, ThBaseObject, BModule, IComModule):
    """Example alert module."""

    def __init__(
        self,
        app_name: AppName,
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
        self.application = app_name
        self._section = self._c_name
        self._cfh = conf
        self._module_conf = _ModuleConf(self._cfh, self._section)

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
                self.logs.message_critical = f"required variable '{_ModuleConf.Keys.CHANNEL}' not set, exiting..."
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
        while not self._stopped:
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
        sleep_break: float = Timestamp.now() + self.sleep_period
        while not self._stopped and sleep_break > Timestamp.now():
            self._sleep(0.2)

    def stop(self) -> None:
        """Set stop event."""
        if self._debug:
            self.logs.message_debug = "stop signal received"
        if self._stop_event:
            self._stop_event.set()

    @property
    def _stopped(self) -> bool:
        """Return stop flag."""
        if self._stop_event:
            return self._stop_event.is_set()
        return True

    @property
    def module_stopped(self) -> bool:
        """Return stop flag."""
        return self._is_stopped  # type: ignore

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
    def module_conf(self) -> Optional[_ModuleConf]:
        """Return module conf object."""
        return self._module_conf  # type: ignore

    @classmethod
    def template_module_name(cls) -> str:
        """Return module name for configuration builder."""
        return cls.__name__.lower()

    @classmethod
    def template_module_variables(cls) -> List[TemplateConfigItem]:
        """Return configuration variables template."""
        out: List[TemplateConfigItem] = []
        # item format:
        # TemplateConfigItem()
        out.append(TemplateConfigItem(desc="Example alert configuration module."))
        out.append(TemplateConfigItem(desc="Variables:"))
        out.append(
            TemplateConfigItem(
                desc=f"{_ModuleConf.Keys.CHANNEL} [int] - unique channel for communication method (for example: 100)"
            )
        )
        out.append(TemplateConfigItem(varname=_ModuleConf.Keys.CHANNEL, value=100))

        return out


# #[EOF]#######################################################################
