# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 06.11.2023

  Purpose: Daemon main class.
"""

import signal
import sys
import time
import gc
import setproctitle

from inspect import currentframe
from typing import Dict, List
from queue import Queue

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
from jsktoolbox.logstool.formatters import (
    LogFormatterDateTime,
    LogFormatterNull,
)
from jsktoolbox.libs.system import CommandLineParser
from jsktoolbox.stringtool.crypto import SimpleCrypto

from libs.base.classes import BProjectClass, BImporter
from libs.interfaces.modules import IRunModule, IComModule
from libs.keys import Keys
from libs.conf import Config
from libs.com.message import ThDispatcher


class AASd(BProjectClass, BImporter):
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
        self.conf = Config(qlog=lengine.logs_queue, app_name=self._c_name)
        self.conf.version = "1.0.DEV"
        self.conf.debug = False
        # the default config file path can be overwritten with the command line argument '-f'.
        self.conf.config_file = (
            "/var/tmp/aasd.conf"
            if (self.conf.version and self.conf.version.find("DEV") > -1)
            or not self.conf.version
            else "/etc/aasd.conf"
        )

        # command line parser
        self.__init_command_line()

        # config file
        if not self.conf.load():
            self.logs.message_critical = "cannot load config file"
            self.loop = False

        # check single run options
        # password
        if self.conf.password:
            print("Receive password encoder options.")
            self.__password_encoding()
            sys.exit(0)

        # update debug
        thl._debug = self.conf.debug

        # update config file
        if self.loop and self.conf.update:
            self.logs.message_notice = "trying to update config file"
            if not self.conf.save():
                self.logs.message_critical = "cannot update config file"

        # signal handling
        signal.signal(signal.SIGTERM, self.__sig_exit)
        signal.signal(signal.SIGHUP, self.__sig_hup)
        # interrupt [ctrl-c]
        signal.signal(signal.SIGINT, self.__sig_exit)

        # others
        setproctitle.setproctitle(self.conf.app_name)
        gc.enable()

    def __start_subsystem(self) -> List:
        """Start subsystems.

        Returns: List[ List[comms_mods], List[running_mods], ThDispatcher ]
        """
        self.logs.message_info = "starting..."

        # communication queue
        qcom = Queue()

        # dispatcher processor
        dispatch = ThDispatcher(
            qlog=self.logs.logs_queue,
            qcom=qcom,
            verbose=self.conf.verbose,
            debug=self.conf.debug,
        )

        # start dispatcher
        dispatch.start()

        # break for coffe
        time.sleep(1)

        # start communication modules
        com_mods: List[IComModule] = []
        for c_mod in self.conf.get_com_modules:
            try:
                o_mod = c_mod(
                    self.conf.cf,
                    self.logs.logs_queue,
                    self.conf.verbose,
                    self.conf.debug,
                )
                o_mod.qcom = dispatch.register_queue(o_mod.module_conf.channel)
                o_mod.start()
                com_mods.append(o_mod)
            except Exception as ex:
                if self.conf.debug:
                    self.logs.message_debug = f"{ex}"

        # start running modules
        run_mods: List[IRunModule] = []
        for r_mod in self.conf.get_run_modules:
            try:
                o_mod = r_mod(
                    self.conf.cf,
                    self.logs.logs_queue,
                    qcom,
                    self.conf.verbose,
                    self.conf.debug,
                )
                o_mod.start()
                run_mods.append(o_mod)
            except Exception as ex:
                if self.conf.debug:
                    self.logs.message_debug = f"{ex}"
        return [com_mods, run_mods, dispatch]

    def __stop_subsystem(
        self,
        com_mods: List[IComModule],
        run_mods: List[IRunModule],
        dispatch: ThDispatcher,
    ) -> None:
        """Stop subsystems."""
        # stopping & joining running modules
        for mod in run_mods:
            mod.stop()
            while mod.is_stopped != True:
                mod.join()
                time.sleep(0.1)

        for mod in com_mods:
            mod.stop()
            while mod.is_stopped != True:
                mod.join()
                time.sleep(0.1)

        # dispatcher processor
        dispatch.stop()
        while dispatch.is_stopped != True:
            dispatch.join()
            time.sleep(0.1)

    def run(self) -> None:
        """Start daemon."""
        # logger processor
        self.logs_processor.start()

        [com_mods, run_mods, dispatch] = self.__start_subsystem()

        # main loop
        self.logs.message_info = "entering to the main loop"
        while self.loop:
            if self.hup:
                # reload configuration and restart subsystems
                self.__stop_subsystem(com_mods, run_mods, dispatch)
                self.hup = False
                if not self.conf.load():
                    # critical message
                    self.logs.message_critical = "cannot reload config file"
                    self.loop = False
                [com_mods, run_mods, dispatch] = self.__start_subsystem()
            time.sleep(0.5)

        self.__stop_subsystem(com_mods, run_mods, dispatch)

        # logger processor
        self.logs_processor.stop()
        time.sleep(2.0)
        while self.logs_processor.is_stopped != True:
            self.logs_processor.join()
            time.sleep(0.1)

        sys.exit(0)

    def __help(self, command_conf: Dict) -> None:
        """Show help information and shutdown."""
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
            desc_opts.append(f" {tmp:<{max_len}}- {command_conf[item]['description']}")
            command_opts += tmp
        # stage 3
        for item in sorted(opt_value):
            tmp = ""
            if command_conf[item]["short"]:
                tmp = f"-{command_conf[item]['short']}|--{item}"
            else:
                tmp = f"--{item}   "
            desc_opts.append(f" {tmp:<{max_len}}- {command_conf[item]['description']}")
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
        parser.configure_argument("U", "updateconf", "update configuration file")
        parser.configure_argument(
            "f",
            "file",
            "path to configuration file",
            has_value=True,
            example_value=self.conf.config_file,
        )
        parser.configure_argument(
            "p",
            "password",
            "password encryptor, valid only with [--section=] and [--varname=] option",
        )
        parser.configure_argument(
            None,
            "section",
            "section name for encrypt password",
            has_value=True,
        )
        parser.configure_argument(
            None,
            "varname",
            "varname in section to encrypt password",
            has_value=True,
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
        if parser.get_option("updateconf") is not None:
            self.conf.update = True
        if parser.get_option("file") is not None:
            self.conf.config_file = parser.get_option("file")
        if parser.get_option("password") is not None:
            if (
                parser.get_option("section") is None
                or parser.get_option("varname") is None
            ):
                print("Error:")
                print(
                    "The '-p|--password' option should be used with the '--section=' and '--varname=' options"
                )
                print("")
                self.__help(parser.dump())
            self.conf.password = True
            self.conf._password_section = parser.get_option("section")
            self.conf._password_varname = parser.get_option("varname")

    def __init_log_levels(self, engine: LoggerEngine) -> None:
        """Set logging levels configuration for LoggerEngine."""
        # ALERT
        engine.add_engine(
            LogsLevelKeys.ALERT,
            LoggerEngineStdout(
                name=f"{self._c_name}->ALERT",
                # formatter=LogFormatterDateTime(),
                formatter=LogFormatterNull(),
            ),
        )
        # DEBUG
        engine.add_engine(
            LogsLevelKeys.DEBUG,
            LoggerEngineStdout(
                name=f"{self._c_name}->DEBUG",
                # formatter=LogFormatterDateTime(),
                formatter=LogFormatterNull(),
            ),
        )
        # ERROR
        engine.add_engine(
            LogsLevelKeys.ERROR,
            LoggerEngineStdout(
                name=f"{self._c_name}->ERROR",
                # formatter=LogFormatterDateTime(),
                formatter=LogFormatterNull(),
            ),
        )
        # NOTICE
        engine.add_engine(
            LogsLevelKeys.NOTICE,
            LoggerEngineStdout(
                name=f"{self._c_name}->NOTICE",
                # formatter=LogFormatterDateTime(),
                formatter=LogFormatterNull(),
            ),
        )
        # CRITICAL
        engine.add_engine(
            LogsLevelKeys.CRITICAL,
            LoggerEngineStdout(
                name=f"{self._c_name}->CRITICAL",
                # formatter=LogFormatterDateTime(),
                formatter=LogFormatterNull(),
            ),
        )
        # EMERGENCY
        engine.add_engine(
            LogsLevelKeys.EMERGENCY,
            LoggerEngineStdout(
                name=f"{self._c_name}->EMERGENCY",
                # formatter=LogFormatterDateTime(),
                formatter=LogFormatterNull(),
            ),
        )
        # INFO
        engine.add_engine(
            LogsLevelKeys.INFO,
            LoggerEngineStdout(
                name=self._c_name,
                # formatter=LogFormatterDateTime(),
                formatter=LogFormatterNull(),
            ),
        )
        # WARNING
        engine.add_engine(
            LogsLevelKeys.WARNING,
            LoggerEngineStdout(
                name=f"{self._c_name}->WARNING",
                # formatter=LogFormatterDateTime(),
                formatter=LogFormatterNull(),
            ),
        )

    def __password_encoding(self) -> None:
        """Encode given password."""
        # check salt, given section name and varname
        salt = self.conf.cf.get(self.conf._section, "salt")
        if salt is None:
            print(
                "The 'salt' variable is missing from the main section of the configuration file."
            )
            sys.exit(2)
        if not self.conf.cf.has_section(self.conf._password_section):
            print(
                f"The specified section name '{self.conf._password_section}' was not found in the configuration file."
            )
            sys.exit(2)

        if not self.conf.cf.has_varname(
            self.conf._password_section, self.conf._password_varname
        ):
            print(
                f"The specified variable name '{self.conf._password_varname}' was not found in the configuration section: '{self.conf._password_section}'."
            )
            sys.exit(2)
        # get password string from console
        while True:
            password = input("Enter password: ")
            if password == "":
                print('Type: "EXIT" to break.')
            elif password == "EXIT":
                return
            else:
                break
        encrypt = SimpleCrypto.multiple_encrypt(salt, password)
        self.conf.cf.set(
            self.conf._password_section, self.conf._password_varname, encrypt
        )
        if self.conf.save():
            print(f'Config file "{self.conf.config_file}" updated.')
        else:
            print(f"Error updating config file.")

    def __sig_exit(self, signum: int, frame) -> None:
        """Received TERM|INT signal."""
        if self.conf.debug:
            self.logs.message_debug = "TERM or INT signal received."
        self.loop = False

    def __sig_hup(self, signum: int, frame) -> None:
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
                f"Expected Boolean type, received: '{type(value)}'.",
                TypeError,
                self._c_name,
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
                f"Expected ThLoggerProcessor type, received: '{type(value)}'.",
                TypeError,
                self._c_name,
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
                f"Expected Boolean type, received: '{type(value)}'.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        self._data[Keys.LOOP] = value


# #[EOF]#######################################################################
