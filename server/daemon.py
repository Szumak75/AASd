# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 06.11.2023

  Purpose: Daemon main class.
"""

import signal
import sys
import time

from inspect import currentframe


from jsktoolbox.raisetool import Raise
from jsktoolbox.logstool.logs import (
    LoggerEngine,
    LoggerClient,
    LoggerEngineFile,
    LoggerEngineStderr,
    LoggerEngineStdout,
    LoggerEngineSyslog,
    LoggerQueue,
    LogsLevelKeys,
)
from jsktoolbox.logstool.logs import ThLoggerProcessor
from jsktoolbox.logstool.formatters import LogFormatterDateTime
from jsktoolbox.libs.system import CommandLineParser

from libs.base.classes import BClasses
from libs.keys import Keys


class AASd(BClasses):
    """AASd - Autonomous Administrative System daemon."""

    def __init__(self) -> None:
        """Constructor."""
        # self.c_name - class name property derived from BClasses
        # self.f_name - current method name property derived from BClasses

        # loop flag init
        self.loop = True

        # logger engines configuration
        lengine = LoggerEngine()
        lengine.add_engine(
            LogsLevelKeys.INFO,
            LoggerEngineStdout(
                name=self.c_name, formatter=LogFormatterDateTime()
            ),
        )
        lengine.add_engine(
            LogsLevelKeys.NOTICE,
            LoggerEngineStdout(
                name=f"{self.c_name}->NOTICE",
                formatter=LogFormatterDateTime(),
            ),
        )
        lengine.add_engine(
            LogsLevelKeys.WARNING,
            LoggerEngineStdout(
                name=f"{self.c_name}->WARNING",
                formatter=LogFormatterDateTime(),
            ),
        )
        lengine.add_engine(
            LogsLevelKeys.DEBUG,
            LoggerEngineStdout(
                name=f"{self.c_name}->DEBUG",
                formatter=LogFormatterDateTime(),
            ),
        )

        # logger client
        self.logs = LoggerClient()

        # logger processor
        thl = ThLoggerProcessor()
        thl.sleep_period = 1.5
        thl.logger_engine = lengine
        thl.logger_client = self.logs
        self.logs_processor = thl

        # signal handling
        signal.signal(signal.SIGTERM, self.__sig_exit)
        signal.signal(signal.SIGHUP, self.__sig_hup)
        # interrupt [ctrl-c]
        signal.signal(signal.SIGINT, self.__sig_exit)

    def run(self) -> None:
        """Start project."""
        self.logs.message_info = "Start main loop."
        # logger processor
        self.logs_processor.start()

        # main loop
        while self.loop:
            time.sleep(0.5)

        self.logs.message_info = "Exit from main loop."

        # logger processor
        self.logs_processor.stop()
        time.sleep(2.0)
        while self.logs_processor.is_stopped != True:
            self.logs_processor.join()
            time.sleep(0.1)
        sys.exit(0)

    def __sig_exit(self, signum: int, frame):
        """Received TERM|INT signal."""
        self.logs.message_debug = self._data
        self.loop = False

    def __sig_hup(self, signum: int, frame):
        """Received HUP signal."""
        self.hup = True

    @property
    def hup(self) -> bool:
        """Return hup flag."""
        if Keys.HUP not in self._data:
            self._data[Keys.HUP] = False
        return self._data[Keys.HUP]

    @hup.setter
    def hup(self, value: bool) -> None:
        """Set loop flag."""
        if not isinstance(value, bool):
            raise Raise.error(
                f"Boolean expected, '{type(value)}' received.",
                TypeError,
                self.c_name,
                currentframe(),
            )
        self._data[Keys.HUP] = value

    @property
    def logs_processor(self) -> ThLoggerProcessor:
        """Return logs_processor."""
        if Keys.PROC_LOGS not in self._data:
            self._data[Keys.PROC_LOGS] = None
        return self._data[Keys.PROC_LOGS]

    @logs_processor.setter
    def logs_processor(self, value: ThLoggerProcessor) -> None:
        """Set logs_processor."""
        if not isinstance(value, ThLoggerProcessor):
            raise Raise.error(
                f"ThLoggerProcessor object expected, '{type(value)}' received.",
                TypeError,
                self.c_name,
                currentframe(),
            )
        self._data[Keys.PROC_LOGS] = value

    @property
    def loop(self) -> bool:
        """Return loop flag."""
        if Keys.LOOP not in self._data:
            self._data[Keys.LOOP] = False
        return self._data[Keys.LOOP]

    @loop.setter
    def loop(self, value: bool) -> None:
        """Set loop flag."""
        if not isinstance(value, bool):
            raise Raise.error(
                f"Boolean expected, '{type(value)}' received.",
                TypeError,
                self.c_name,
                currentframe(),
            )
        self._data[Keys.LOOP] = value


# #[EOF]#######################################################################
