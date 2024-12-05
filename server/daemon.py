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
from typing import Dict, List, Optional
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
from jsktoolbox.systemtool import CommandLineParser
from jsktoolbox.basetool.logs import LoggerQueue
from jsktoolbox.stringtool.crypto import SimpleCrypto

from libs.base.classes import BProjectClass, BImporter
from libs.interfaces.modules import IRunModule, IComModule
from libs.keys import Keys
from libs.conf import AppConfig
from libs.com.message import ThDispatcher
from libs.app import AppName

import server


class AASd(BProjectClass, BImporter):
    """AASd - Autonomous Administrative System daemon."""

    def __init__(self) -> None:
        """Constructor."""
        # self.c_name - class name property derived from BClasses
        # self.f_name - current method name property derived from BClasses

        # application name
        self.application = AppName(
            app_name=self._c_name, app_version=server.__version__
        )

        # loop flag init
        self.loop = True

        # logger engines configuration
        log_engine = LoggerEngine()
        log_queue: Optional[LoggerQueue] = log_engine.logs_queue
        if log_queue is None:
            log_queue = LoggerQueue()
            log_engine.logs_queue = log_queue

        # logger levels
        self.__init_log_levels(log_engine)

        # logger client
        self.logs = LoggerClient()

        # logger processor
        thl = ThLoggerProcessor()
        thl.sleep_period = 1.5
        thl.logger_engine = log_engine
        thl.logger_client = self.logs
        self.logs_processor = thl

        # add config handler
        if self.conf is None:
            self.conf = AppConfig(qlog=log_queue, app_name=self._c_name)
        self.conf.version = self.application.app_version
        self.conf.debug = False
        # the default config file path can be overwritten with the command line argument '-f'.
        conf_ver: Optional[str] = self.conf.version
        if conf_ver and conf_ver.find("DEV") > -1:
            self.conf.config_file = "/var/tmp/aasd.conf"
        else:
            self.conf.config_file = "/etc/aasd.conf"

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
        if self.conf.app_name:
            setproctitle.setproctitle(self.conf.app_name)

        # automatic garbage collector
        gc.enable()

    def __start_subsystem(self) -> List:
        """Start subsystems.

        Returns: List[ List[comms_mods], List[running_mods], ThDispatcher ]
        """
        self.logs.message_info = "starting..."

        if self.logs is None or self.conf is None or self.logs.logs_queue is None:
            return [None, None]

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

        # break for caffe
        time.sleep(1)

        # start communication modules
        com_mods: List[IComModule] = []
        for com_mod in self.conf.get_com_modules:
            try:
                obj_mod = com_mod(
                    app_name=self.application,
                    conf=self.conf.cf,
                    qlog=self.logs.logs_queue,
                    verbose=self.conf.verbose,
                    debug=self.conf.debug,
                )  # type: ignore
                obj_mod.qcom = dispatch.register_queue(obj_mod.module_conf.channel)
                obj_mod.start()
                com_mods.append(obj_mod)
            except Exception as ex:
                if self.conf.debug:
                    self.logs.message_debug = f"{ex}"

        # start running modules
        run_mods: List[IRunModule] = []
        for run_mod in self.conf.get_run_modules:
            try:
                obj_mod = run_mod(
                    app_name=self.application,
                    conf=self.conf.cf,
                    qlog=self.logs.logs_queue,
                    qcom=qcom,
                    verbose=self.conf.verbose,
                    debug=self.conf.debug,
                )  # type: ignore
                obj_mod.start()
                run_mods.append(obj_mod)
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
            while mod.module_stopped != True:
                mod.join()  # type: ignore
                time.sleep(0.1)
        # stopping & joining communication modules
        for mod in com_mods:
            mod.stop()
            while mod.module_stopped != True:
                mod.join()  # type: ignore
                time.sleep(0.1)

        # dispatcher processor
        dispatch.stop()
        while dispatch._is_stopped != True:
            dispatch.join()
            time.sleep(0.1)
        dispatch.join()

    def run(self) -> None:
        """Start daemon."""
        if self.conf is None:
            return None
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
        while self.logs_processor._is_stopped != True:
            self.logs_processor.join()
            time.sleep(0.1)

        sys.exit(0)

    def __help(self, command_conf: Dict) -> None:
        """Show help information and shutdown."""
        command_opts: str = ""
        desc_opts: List = []
        max_len: int = 0
        opt_value: List = []
        opt_no_value: List = []
        # stage 1
        for item in command_conf.keys():
            if max_len < len(item):
                max_len = len(item)
            if command_conf[item]["has_value"]:
                opt_value.append(item)
            else:
                opt_no_value.append(item)
        max_len += 7
        # stage 2
        for item in sorted(opt_no_value):
            tmp: str = ""
            if command_conf[item]["short"]:
                tmp = f"-{command_conf[item]['short']}|--{item} "
            else:
                tmp = f"--{item}    "
            desc_opts.append(f" {tmp:<{max_len}}- {command_conf[item]['description']}")
            command_opts += tmp
        # stage 3
        for item in sorted(opt_value):
            tmp: str = ""
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
        """Configure CommandLineParser and update config."""
        if self.conf is None:
            return None
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
            "",
            "section",
            "section name for encrypt password",
            has_value=True,
        )
        parser.configure_argument(
            "",
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
            self.conf.config_file = parser.get_option("file")  # type: ignore
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
            self.conf._password_section = parser.get_option("section")  # type: ignore
            self.conf._password_varname = parser.get_option("varname")  # type: ignore

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
        if self.conf is None or self.conf.cf is None or self.conf._section is None:
            return None
        # check salt, given section name and varname
        salt: Optional[int] = self.conf.cf.get(self.conf._section, "salt")
        if salt is None:
            print(
                "The 'salt' variable is missing from the main section of the configuration file."
            )
            sys.exit(2)
        if self.conf._password_section and not self.conf.cf.has_section(
            self.conf._password_section
        ):
            print(
                f"The specified section name '{self.conf._password_section}' was not found in the configuration file."
            )
            sys.exit(2)

        if (
            self.conf._password_section
            and self.conf._password_varname
            and not self.conf.cf.has_varname(
                self.conf._password_section, self.conf._password_varname
            )
        ):
            print(
                f"The specified variable name '{self.conf._password_varname}' was not found in the configuration section: '{self.conf._password_section}'."
            )
            sys.exit(2)
        # get password string from console
        while True:
            password: str = input("Enter password: ")
            if password == "":
                print('Type: "EXIT" to break.')
            elif password == "EXIT":
                return None
            else:
                break
        encrypt: str = SimpleCrypto.multiple_encrypt(salt, password)
        if self.conf._password_section:
            self.conf.cf.set(
                self.conf._password_section, self.conf._password_varname, encrypt
            )
            if self.conf.save():
                print(f'Config file "{self.conf.config_file}" updated.')
            else:
                print(f"Error updating config file.")

    def __sig_exit(self, signum: int, frame) -> None:
        """Received TERM|INT signal."""
        if self.conf and self.conf.debug:
            self.logs.message_debug = "TERM or INT signal received."
        self.loop = False

    def __sig_hup(self, signum: int, frame) -> None:
        """Received HUP signal."""
        if self.conf and self.conf.debug:
            self.logs.message_debug = "HUP signal received."
        self.hup = True

    @property
    def hup(self) -> bool:
        """Return hup flag."""
        return self._get_data(key=Keys.HUP, default_value=False)  # type: ignore

    @hup.setter
    def hup(self, value: bool) -> None:
        """Set loop flag."""
        self._set_data(key=Keys.HUP, value=value, set_default_type=bool)

    @property
    def logs_processor(self) -> ThLoggerProcessor:
        """Return logs_processor."""
        return self._get_data(key=Keys.PROC_LOGS, default_value=None)  # type:ignore

    @logs_processor.setter
    def logs_processor(self, value: ThLoggerProcessor) -> None:
        """Set logs_processor."""
        self._set_data(
            key=Keys.PROC_LOGS, value=value, set_default_type=ThLoggerProcessor
        )

    @property
    def loop(self) -> bool:
        """Return loop flag."""
        return self._get_data(key=Keys.LOOP, default_value=False)  # type:ignore

    @loop.setter
    def loop(self, value: bool) -> None:
        """Set loop flag."""
        self._set_data(key=Keys.LOOP, value=value, set_default_type=bool)


# #[EOF]#######################################################################
