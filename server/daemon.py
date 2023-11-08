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
from typing import Dict

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

from libs.base.classes import BProjectClass
from libs.keys import Keys
from libs.conf import Config


class AASd(BProjectClass):
    """AASd - Autonomous Administrative System daemon."""

    def __init__(self) -> None:
        """Constructor."""
        # self.c_name - class name property derived from BClasses
        # self.f_name - current method name property derived from BClasses

        # loop flag init
        self.loop = True

        # logger engines configuration
        lengine = LoggerEngine()

        # logger levels
        self.__init_log_levels(lengine)

        # logger client
        self.logs = LoggerClient()

        # logger processor
        thl = ThLoggerProcessor()
        thl.sleep_period = 1.5
        thl.logger_engine = lengine
        thl.logger_client = self.logs
        self.logs_processor = thl

        # add config handler
        self.conf = Config(qlog=lengine.logs_queue, app_name=self.c_name)
        self.conf.version = "1.0.0"
        self.conf.debug = False
        self.conf.config_file = (
            "/tmp/aasd.conf"
            if self.conf.version == "1.0.0"
            else "/etc/aasd.conf"
        )

        # command line parser
        self.__init_command_line()

        # config file
        if not self.conf.load():
            self.loop = False

        # test działa!
        # odczytuje c_name prywatnej klasy pomocniczej konfiguratora
        print(self.conf.module_conf.c_name)

        # update debug
        thl._debug = self.conf.debug

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

        # start communication modules

        # start running modules

        # main loop
        while self.loop:
            time.sleep(0.5)

        self.logs.message_info = "Exit from main loop."

        # stopping & joining running modules

        # logger processor
        self.logs_processor.stop()
        time.sleep(2.0)
        while self.logs_processor.is_stopped != True:
            self.logs_processor.join()
            time.sleep(0.1)
        sys.exit(0)

    def __help(self, command_conf: Dict) -> None:
        """Show help information and shutdown."""
        print(f"[{self.c_name}.{self.f_name}] {command_conf}")
        command_opts = ""
        desc_opts = []
        max_len = 0
        opt_value = []
        opt_novalue = []
        # stage 1
        for item in command_conf.keys():
            if max_len < len(item):
                max_len = len(item)
            if command_conf[item]["has_value"]:
                opt_value.append(item)
            else:
                opt_novalue.append(item)
        max_len += 7
        # stage 2
        for item in sorted(opt_novalue):
            tmp = ""
            if command_conf[item]["short"]:
                tmp = f"-{command_conf[item]['short']}|--{item} "
            else:
                tmp = f"--{item}    "
            desc_opts.append(
                f" {tmp:<{max_len}}- {command_conf[item]['description']}"
            )
            command_opts += tmp
        # stage 3
        for item in sorted(opt_value):
            tmp = ""
            if command_conf[item]["short"]:
                tmp = f"-{command_conf[item]['short']}|--{item}"
            else:
                tmp = f"--{item}   "
            desc_opts.append(
                f" {tmp:<{max_len}}- {command_conf[item]['description']}"
            )
            command_opts += tmp
            if command_conf[item]["example"]:
                command_opts += f"{command_conf[item]['example']}"
            command_opts += " "
        print("###[HELP]###")
        print(f"{sys.argv[0]} {command_opts}")
        print(f"")
        print("# Arguments:")
        for item in desc_opts:
            print(item)
        sys.exit(2)

    def __init_command_line(self) -> None:
        """Configure ConnamdLineParser and update config."""
        parser = CommandLineParser()

        # arguments configuration
        parser.configure_argument("h", "help", "this information")
        parser.configure_argument("v", "verbose", "verbose logging level")
        parser.configure_argument("d", "debug", "debug logging level")
        parser.configure_argument(
            "f",
            "file",
            "path to configuration file",
            has_value=True,
            example_value=self.conf.config_file,
        )

        # command line parsing
        parser.parse_arguments()

        # checking
        if parser.get_option("help") is not None:
            self.__help(parser.dump())
        if parser.get_option("debug") is not None:
            self.conf.debug = True
        if parser.get_option("verbose") is not None:
            self.conf.verbose = True
        if parser.get_option("file=") is not None:
            self.conf.config_file = parser.get_option("file=")

    def __init_log_levels(self, engine: LoggerEngine) -> None:
        """Set logging levels configuration for LoggerEngine."""
        # ALERT
        engine.add_engine(
            LogsLevelKeys.ALERT,
            LoggerEngineStdout(
                name=f"{self.c_name}->ALERT",
                formatter=LogFormatterDateTime(),
            ),
        )
        # DEBUG
        engine.add_engine(
            LogsLevelKeys.DEBUG,
            LoggerEngineStdout(
                name=f"{self.c_name}->DEBUG",
                formatter=LogFormatterDateTime(),
            ),
        )
        # ERROR
        engine.add_engine(
            LogsLevelKeys.ERROR,
            LoggerEngineStdout(
                name=f"{self.c_name}->ERROR",
                formatter=LogFormatterDateTime(),
            ),
        )
        # NOTICE
        engine.add_engine(
            LogsLevelKeys.NOTICE,
            LoggerEngineStdout(
                name=f"{self.c_name}->NOTICE",
                formatter=LogFormatterDateTime(),
            ),
        )
        # CRITICAL
        engine.add_engine(
            LogsLevelKeys.CRITICAL,
            LoggerEngineStdout(
                name=f"{self.c_name}->CRITICAL",
                formatter=LogFormatterDateTime(),
            ),
        )
        # EMERGENCY
        engine.add_engine(
            LogsLevelKeys.EMERGENCY,
            LoggerEngineStdout(
                name=f"{self.c_name}->EMERGENCY",
                formatter=LogFormatterDateTime(),
            ),
        )
        # INFO
        engine.add_engine(
            LogsLevelKeys.INFO,
            LoggerEngineStdout(
                name=self.c_name, formatter=LogFormatterDateTime()
            ),
        )
        # WARNING
        engine.add_engine(
            LogsLevelKeys.WARNING,
            LoggerEngineStdout(
                name=f"{self.c_name}->WARNING",
                formatter=LogFormatterDateTime(),
            ),
        )

    def __sig_exit(self, signum: int, frame):
        """Received TERM|INT signal."""
        if self.conf.debug:
            self.logs.message_debug = "TERM or INT signal received."
            self.logs.message_debug = self._data
        self.loop = False

    def __sig_hup(self, signum: int, frame):
        """Received HUP signal."""
        if self.conf.debug:
            self.logs.message_debug = "HUP signal received."
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
