# -*- coding: UTF-8 -*-
"""
Logging test module.

Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 2023-11-07

Purpose: Provide a simple test module that periodically writes log messages.
"""

import time
from inspect import currentframe
from typing import Dict, List, Optional, Any, Union
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
from libs.app import AppName


class _Keys(object, metaclass=ReadOnlyClass):
    """Define internal key names for the module."""


class _ModuleConf(ModuleConfigMixin):
    """Provide typed access to the module configuration."""


class MTest(Thread, ThBaseObject, ModuleMixin, IRunModule):
    """Emit periodic log messages for runtime testing."""

    def __init__(
        self,
        app_name: AppName,
        conf: ConfigTool,
        qlog: LoggerQueue,
        qcom: Queue,
        verbose: bool = False,
        debug: bool = False,
    ) -> None:
        """Initialize the logging test module.

        ### Arguments:
        * app_name: AppName - Application identity container.
        * conf: ConfigTool - Configuration handler bound to the module section.
        * qlog: LoggerQueue - Shared logging queue.
        * qcom: Queue - Shared communication queue.
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

    def _apply_config(self) -> bool:
        """Apply runtime configuration to the module.

        ### Returns:
        bool - `True` when configuration was applied successfully.
        """
        try:
            if self.module_conf and self.module_conf.sleep_period:
                self.sleep_period = self.module_conf.sleep_period
        except Exception as ex:
            self.logs.message_critical = f"{ex}"
            return False
        return True

    def run(self) -> None:
        """Run the periodic logging loop."""
        # initialization local variables
        count = 0

        # initialization variables from config file
        if not self._apply_config():
            self.logs.message_error = "configuration error."
            return

        # starting module loop
        while not self._stopped:
            # something
            count += 1
            self.logs.message_info = f"ping {count:>04d}"
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
            self.logs.message_debug = "stop signal received."
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
        out.append(TemplateConfigItem(desc="Example configuration module."))
        out.append(TemplateConfigItem(desc="This module is for testing purposes only."))
        out.append(
            TemplateConfigItem(
                desc="It works by periodically sending messages to the logger."
            )
        )
        out.append(TemplateConfigItem(desc="the module defines only one variable:"))
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
                varname=_ModuleConf.Keys.SLEEP_PERIOD, value=3.25, desc="[second]"
            )
        )
        return out


# #[EOF]#######################################################################
