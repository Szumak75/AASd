# -*- coding: UTF-8 -*-
"""
Daemon runtime orchestration.

Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 2023-11-06

Purpose: Provide the main daemon class responsible for runtime orchestration.
"""

import signal
import sys
import time
import gc
import setproctitle

from typing import Any, Dict, List, Optional

from jsktoolbox.logstool import (
    LoggerEngine,
    LoggerClient,
    LoggerEngineFile,
    LoggerEngineStderr,
    LoggerEngineStdout,
    LoggerEngineSyslog,
    LoggerQueue,
    LogsLevelKeys,
)

from jsktoolbox.logstool import ThLoggerProcessor
from jsktoolbox.logstool import (
    LogFormatterDateTime,
    LogFormatterNull,
)
from jsktoolbox.systemtool import CommandLineParser, PathChecker
from jsktoolbox.stringtool import SimpleCrypto

from libs import AppConfig, AppName, Keys
from libs.base import ProjectClassMixin
from libs.plugins import (
    PluginRegistryService,
    PluginServiceReport,
)

import server


class AASd(ProjectClassMixin):
    """Orchestrate daemon startup, runtime supervision, and shutdown."""

    # #[CONSTRUCTOR]##################################################################
    def __init__(self) -> None:
        """Initialize the daemon runtime.

        The constructor prepares logging, configuration handling, command line
        options, process naming, and signal handlers before the main loop starts.
        """
        # self.c_name - class name property derived from BClasses
        # self.f_name - current method name property derived from BClasses

        # application name
        self.application = AppName(
            app_name=self._c_name, app_version=server.__version__
        )

        # loop flag init
        self.loop = True

        # logger engines configuration
        logger_engine = LoggerEngine()
        existing_queue: Optional[LoggerQueue] = logger_engine.logs_queue
        if existing_queue is None:
            logger_queue = LoggerQueue()
            logger_engine.logs_queue = logger_queue
        else:
            logger_queue = existing_queue

        # logger levels
        self.__init_log_levels(logger_engine)

        # logger client
        self.logs = LoggerClient()

        # logger processor
        thl = ThLoggerProcessor()
        thl.sleep_period = 1.5
        thl.logger_engine = logger_engine
        thl.logger_client = self.logs
        self.logs_processor = thl

        # add config handler
        if self.conf is None:
            self.conf = AppConfig(qlog=logger_queue, app_name=self._c_name)
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
        # interrupt [ctrl-c], the real processor should be set in the constructor
        signal.signal(signal.SIGINT, self.__sig_exit)

        # others
        if self.conf.app_name:
            setproctitle.setproctitle(self.conf.app_name)

        # check plugins directory
        self.__check_plugins_dir()

        # automatic garbage collector
        gc.enable()

    # #[PUBLIC PROPERTIES]#############################################################
    @property
    def hup(self) -> bool:
        """Return the configuration reload flag.

        ### Returns:
        bool - `True` when subsystem restart has been requested.
        """
        obj: Optional[bool] = self._get_data(key=Keys.HUP, default_value=False)
        if obj is None:
            return False
        return obj

    @hup.setter
    def hup(self, value: bool) -> None:
        """Store the configuration reload flag.

        ### Arguments:
        * value: bool - Reload request flag.
        """
        self._set_data(key=Keys.HUP, value=value, set_default_type=bool)

    @property
    def logs_processor(self) -> ThLoggerProcessor:
        """Return the background log processing thread.

        ### Returns:
        ThLoggerProcessor - Logger processing thread instance.

        ### Raises:
        * ValueError: If the logger processor has not been initialized.
        """
        processor: Optional[ThLoggerProcessor] = self._get_data(
            key=Keys.PROC_LOGS, default_value=None
        )
        if processor is None:
            # Fake processor to avoid type errors in first access.
            processor = ThLoggerProcessor()
        return processor

    @logs_processor.setter
    def logs_processor(self, value: ThLoggerProcessor) -> None:
        """Store the background log processing thread.

        ### Arguments:
        * value: ThLoggerProcessor - Logger processing thread instance.
        """
        self._set_data(
            key=Keys.PROC_LOGS, value=value, set_default_type=ThLoggerProcessor
        )

    @property
    def loop(self) -> bool:
        """Return the main loop flag.

        ### Returns:
        bool - `True` while the daemon main loop should continue.
        """
        obj: Optional[bool] = self._get_data(key=Keys.LOOP, default_value=False)
        if obj is None:
            return False
        return obj

    @loop.setter
    def loop(self, value: bool) -> None:
        """Store the main loop flag.

        ### Arguments:
        * value: bool - Main loop execution flag.
        """
        self._set_data(key=Keys.LOOP, value=value, set_default_type=bool)

    # #[PUBLIC METHODS]################################################################
    def run(self) -> None:
        """Run the daemon main loop until shutdown is requested."""
        if self.conf is None:
            return None
        # logger processor
        self.logs_processor.start()

        report: PluginServiceReport = self.__start_subsystem()

        # main loop
        self.logs.message_info = "entering to the main loop"
        while self.loop:
            if self.hup:
                # reload configuration and restart subsystems
                self.__stop_subsystem(report)
                self.hup = False
                if not self.conf.load():
                    # critical message
                    self.logs.message_critical = "cannot reload config file"
                    self.loop = False
                report = self.__start_subsystem()
            time.sleep(0.5)

        self.__stop_subsystem(report)

        # logger processor
        self.logs_processor.stop()
        time.sleep(2.0)
        while self.logs_processor._is_stopped != True:
            self.logs_processor.join()
            time.sleep(0.1)

        sys.exit(0)

    # #[PRIVATE METHODS]###############################################################
    def __check_plugins_dir(self) -> None:
        """Check if the plugins directory exists and is accessible."""
        if self.conf is None:
            return None
        if self.conf.plugins_dir is None:
            self.logs.message_critical = (
                "plugins directory is not set in the configuration."
            )
            return None
        pc = PathChecker(self.conf.plugins_dir + "/")
        if not pc.exists:
            self.logs.message_warning = (
                f"plugins directory '{self.conf.plugins_dir}' does not exist."
            )
            try:
                if pc.create():
                    self.logs.message_info = (
                        f"plugins directory '{self.conf.plugins_dir}' created."
                    )
            except Exception as ex:
                self.logs.message_critical = (
                    f"error creating plugins directory '{self.conf.plugins_dir}': {ex}"
                )
                self.loop = False
        elif not pc.is_dir:
            self.logs.message_critical = (
                f"plugins directory '{self.conf.plugins_dir}' is not a directory."
            )
            self.loop = False
        else:
            self.logs.message_info = (
                f"plugins directory '{self.conf.plugins_dir}' is ready."
            )

    def __help(self, command_conf: Dict) -> None:
        """Render command line help and terminate the process.

        ### Arguments:
        * command_conf: Dict - Parsed command configuration dumped by the CLI parser.
        """
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
        """Configure command line arguments and map them to runtime settings."""
        if self.conf is None:
            return None
        parser = CommandLineParser()

        # arguments configuration
        parser.configure_argument("h", "help", "this information")
        parser.configure_argument("v", "verbose", "verbose logging level")
        parser.configure_argument("d", "debug", "debug logging level")
        parser.configure_argument("U", "updateconf", "update configuration file")
        parser.configure_argument(
            "P",
            "plugins_dir",
            "directory for plugins",
            has_value=True,
            example_value="./plugins",
        )
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
        if parser.get_option("plugins_dir") is not None:
            self.conf.plugins_dir = parser.get_option("plugins_dir")  # type: ignore
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
        """Register logger engines for all log levels used by the daemon.

        ### Arguments:
        * engine: LoggerEngine - Logger engine to configure.
        """
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
        """Encrypt a password entered on stdin and store it in the config file."""
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

    def __sig_exit(self, signum: int, frame: Any) -> None:
        """Handle `SIGTERM` and `SIGINT` by requesting daemon shutdown.

        ### Arguments:
        * signum: int - Received signal number.
        * frame: Any - Current frame passed by the signal handler.
        """
        if self.conf and self.conf.debug:
            self.logs.message_debug = "TERM or INT signal received."
        self.loop = False

    def __sig_hup(self, signum: int, frame: Any) -> None:
        """Handle `SIGHUP` by requesting subsystem restart and config reload.

        ### Arguments:
        * signum: int - Received signal number.
        * frame: Any - Current frame passed by the signal handler.
        """
        if self.conf and self.conf.debug:
            self.logs.message_debug = "HUP signal received."
        self.hup = True

    def __start_subsystem(self) -> PluginServiceReport:
        """Start dispatcher and plugin instances through the registry service.

        ### Returns:
        PluginServiceReport - Supervision report for the startup cycle.
        """
        if self.conf is None:
            return PluginServiceReport()
        return PluginRegistryService.start(
            conf=self.conf,
            app_meta=self.application,
            logs=self.logs,
        )

    def __stop_subsystem(self, report: PluginServiceReport) -> None:
        """Stop all started plugin subsystems through the registry service.

        ### Arguments:
        * report: PluginServiceReport - Supervision report with active runtimes.
        """
        PluginRegistryService.stop(report=report, logs=self.logs)


# #[EOF]#######################################################################
