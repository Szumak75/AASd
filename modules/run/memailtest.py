# -*- coding: UTF-8 -*-
"""
Email subsystem test module.

Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 2023-11-23

Purpose: Provide a test module that generates sample multipart e-mail messages.
"""

import time
from inspect import currentframe
from typing import List, Optional, Any, Union
from threading import Thread, Event
from queue import Queue

from jsktoolbox.basetool.threads import ThBaseObject
from jsktoolbox.logstool.logs import LoggerClient, LoggerQueue
from jsktoolbox.configtool.main import Config as ConfigTool
from jsktoolbox.attribtool import ReadOnlyClass
from jsktoolbox.raisetool import Raise
from jsktoolbox.datetool import Timestamp

from libs.base import ModuleMixin
from libs.interfaces.modules import IRunModule
from libs.base import ModuleConfigMixin
from libs.templates.modules import TemplateConfigItem
from libs.com.message import Message, Multipart, Channel
from libs.app import AppName


class _Keys(object, metaclass=ReadOnlyClass):
    """Define internal key names for the module."""


class _ModuleConf(ModuleConfigMixin):
    """Provide typed access to the module configuration."""


class MEmailtest(Thread, ThBaseObject, ModuleMixin, IRunModule):
    """Generate sample multipart e-mail messages for communication tests."""

    def __init__(
        self,
        app_name: AppName,
        conf: ConfigTool,
        qlog: LoggerQueue,
        qcom: Queue,
        verbose: bool = False,
        debug: bool = False,
    ) -> None:
        """Initialize the test module.

        ### Arguments:
        * app_name: AppName - Application identity container.
        * conf: ConfigTool - Configuration handler bound to the module section.
        * qlog: LoggerQueue - Shared logging queue.
        * qcom: Queue - Shared communication queue for outbound messages.
        * verbose: bool - Initial verbose flag value.
        * debug: bool - Initial debug flag value.
        """
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
        self._bm_debug = debug
        self._verbose = verbose

        # logger client initialization
        self.logs = LoggerClient(queue=qlog, name=self._c_name)

        # communication queue
        self.qcom = qcom

    def _apply_config(self) -> bool:
        """Apply runtime configuration to the module.

        ### Returns:
        bool - `True` when configuration was applied successfully.
        """
        if self.module_conf is None:
            return False
        try:
            if self.module_conf.sleep_period:
                self.sleep_period = self.module_conf.sleep_period
        except Exception as ex:
            self.logs.message_critical = f"{ex}"
            return False
        return True

    def run(self) -> None:
        """Run the message generation loop for the test module."""
        self.logs.message_notice = "starting..."
        if (
            self.module_conf is None
            or self.module_conf.message_channel is None
            or self.qcom is None
        ):
            return None
        # initialization local variables
        channel = Channel(self.module_conf.message_channel)

        # initialization variables from config file
        if not self._apply_config():
            self.logs.message_error = "configuration error."
            return

        # starting module loop
        if self.debug:
            self.logs.message_debug = "entering to the main loop"
        while not self._stopped:
            if channel.check:
                if self.debug:
                    self.logs.message_debug = "expired channel found"
                for chan in channel.get:
                    if self.debug:
                        self.logs.message_debug = (
                            f"create message for channel: '{chan}'"
                        )
                    message = Message()
                    message.channel = int(chan)
                    message.subject = f"[{self.application.app_name}:{self._c_name}] This is example email from {self.application.app_host_name}."
                    message.footer = f"{self.application.app_name} {self.application.app_version} on {self.application.app_host_name}"
                    message.mmessages = {
                        Multipart.PLAIN: ["Test message."],
                        Multipart.HTML: [
                            "<html>",
                            "<head></head>",
                            "<body>",
                            "<p>This is a test message,<br>",
                            "presenting the possibilities of creating and sending<br>",
                            "<i>multipart alternative</i> email messages,<br>",
                            "using characters encoded in 'UTF-8'.</p>",
                            "<p><b>Please do not reply to this message.</b></p>",
                            "</body>",
                            "</html>",
                        ],
                    }

                    if self.debug:
                        self.logs.message_debug = f"put message to queue"
                    self.qcom.put(message)
            self.sleep()

        # exiting from loop
        if self.debug:
            self.logs.message_debug = "exiting from loop."

    def sleep(self) -> None:
        """Sleep until the next loop iteration."""
        sleep_break: float = Timestamp.now() + self.sleep_period
        while not self._stopped and sleep_break > Timestamp.now():
            time.sleep(0.2)

    def stop(self) -> None:
        """Request module shutdown."""
        if self.debug:
            self.logs.message_debug = "stop signal received"
        if self._stop_event:
            self._stop_event.set()

    @property
    def debug(self) -> bool:
        """Return the effective debug flag.

        ### Returns:
        bool - Debug flag value.
        """
        if self._bm_debug is not None:
            return self._bm_debug
        return False

    @property
    def verbose(self) -> bool:
        """Return the effective verbose flag.

        ### Returns:
        bool - Verbose flag value.
        """
        return self._verbose

    @property
    def _stopped(self) -> bool:
        """Return whether stop was requested.

        ### Returns:
        bool - `True` when stop was requested.
        """
        if self._stop_event:
            return self._stop_event.is_set()
        return True

    @property
    def module_stopped(self) -> bool:
        """Return whether the underlying thread is stopped.

        ### Returns:
        bool - `True` when the module thread is stopped.
        """
        return self._is_stopped  # type: ignore

    @property
    def module_conf(self) -> Optional[_ModuleConf]:
        """Return the typed module configuration.

        ### Returns:
        Optional[_ModuleConf] - Module configuration adapter.
        """
        return self._module_conf  # type: ignore

    @classmethod
    def template_module_name(cls) -> str:
        """Return the configuration section name for this module.

        ### Returns:
        str - Lowercase configuration section name.
        """
        return cls.__name__.lower()

    @classmethod
    def template_module_variables(cls) -> List[TemplateConfigItem]:
        """Return configuration template items for this module.

        ### Returns:
        List[TemplateConfigItem] - Configuration template items.
        """
        out: List[TemplateConfigItem] = []
        # item format:
        # TemplateConfigItem()
        out.append(TemplateConfigItem(desc="Email test configuration module."))
        out.append(
            TemplateConfigItem(
                desc=f"'{_ModuleConf.Keys.SLEEP_PERIOD}' [float], which determines the length of the break"
            )
        )
        out.append(
            TemplateConfigItem(
                desc="between subsequent executions of the program's main loop"
            )
        )
        out.append(
            TemplateConfigItem(
                desc=f"'{_ModuleConf.Keys.MESSAGE_CHANNEL}' [List[str]], comma separated communication channels list,"
            )
        )
        out.append(
            TemplateConfigItem(desc="['nr(:default delay=0)'|'nr1:delay', 'nr2:delay']")
        )
        out.append(
            TemplateConfigItem(desc="where 'delay' means the time between generating")
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
                varname=_ModuleConf.Keys.SLEEP_PERIOD,
                value=5.0,
                desc="[seconds]",
            )
        )
        out.append(
            TemplateConfigItem(
                varname=_ModuleConf.Keys.MESSAGE_CHANNEL,
                value=["1"],
            )
        )
        return out


# #[EOF]#######################################################################
