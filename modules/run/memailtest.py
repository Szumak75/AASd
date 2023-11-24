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

from libs.base.classes import BModule
from libs.interfaces.modules import IRunModule
from libs.base.classes import BModuleConfig
from libs.interfaces.conf import IModuleConfig
from libs.templates.modules import TemplateConfigItem
from libs.com.message import Message, Multipart, Priority
from libs.tools.datetool import DateTime, Timestamp, Intervals


class _Keys(object, metaclass=ReadOnlyClass):
    """Private Keys definition class.

    For internal purpose only.
    """

    MODCONF = "__MODULE_CONF__"
    SLEEP_PERIOD = "sleep_period"
    MESSAGE_PRIORITY = "message_priority"


class _ModuleConf(IModuleConfig, BModuleConfig):
    """Module Config private class."""

    def _get(self, varname: str) -> Any:
        """Get variable from config."""
        return self._cfh.get(self._section, varname)

    @property
    def message_priority(self) -> Optional[List[str]]:
        """Return message priority list."""
        var = self._get(varname=_Keys.MESSAGE_PRIORITY)
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


class MEmailtest(Thread, ThBaseObject, BModule, IRunModule):
    """Email test module."""

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
        priority = Priority(self.module_conf.message_priority)

        # initialization variables from config file
        if not self._apply_config():
            self.logs.message_error = "configuration error."
            return

        # starting module loop
        if self.debug:
            self.logs.message_debug = "entering to the main loop"
        while not self.stopped:
            if priority.check:
                if self.debug:
                    self.logs.message_debug = "expired priority found"
                for prio in priority.get:
                    if self.debug:
                        self.logs.message_debug = (
                            f"create message for priority: '{prio}'"
                        )
                    message = Message()
                    message.priority = int(prio)
                    message.subject = "This is example email."
                    message.reply_to = "marauder@virthost.pl"
                    message.to = "Szumak <szumak@virthost.pl>"
                    message.to = "Test <test@net-s.pl>"
                    message.to = "JK <jacek.kotlarski@air-net.gda.pl>"
                    # message.messages = (
                    # "To jest wiadomość testowa z polskimi znakami."
                    # )
                    # message.messages = "Życzymy miłego dnia!"
                    message.mmessages = {
                        Multipart.PLAIN: ["Wiadomość testowa."],
                        Multipart.HTML: [
                            "<html>",
                            "<head></head>",
                            "<body>",
                            "<p>To jest wiadomość testowa,<br>",
                            "prezentująca możliwości tworzenia i wysyłania<br>",
                            "wiadomości mailowych typu <i>multipart alternative</i>,<br>",
                            "z wykorzystaniem znaków kodowanych w 'UTF-8'.</p>",
                            "<p><b>Prosimy nie odpowiadać na tą wiadomość.</b></p>",
                            "</body>",
                            "</html>",
                        ],
                    }

                    if self.debug:
                        self.logs.message_debug = f"put message to queue"
                    self.qcom.put(message)
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
            TemplateConfigItem(desc="Emailtest configuration module.")
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
                desc="'message_priority' [List[str]], comma separated communication priority list,"
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
                desc="subsequent notifications for a given priority and can be given in"
            )
        )
        out.append(
            TemplateConfigItem(
                desc="seconds or a numerical value with the suffix 's|m|h|d|w'"
            )
        )
        out.append(
            TemplateConfigItem(
                varname=_Keys.SLEEP_PERIOD,
                value=5.0,
                desc="[seconds]",
            )
        )
        out.append(
            TemplateConfigItem(
                varname=_Keys.MESSAGE_PRIORITY,
                value=["1"],
            )
        )
        return out


# #[EOF]#######################################################################
