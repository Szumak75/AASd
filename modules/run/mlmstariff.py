# -*- coding: utf-8 -*-
"""
  mlmstariff.py
  Author : Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 4.12.2024, 12:46:01
  
  Purpose: LMS module enabling checking of tariff assignment to nodes.
"""


import time
from inspect import currentframe
from typing import Dict, List, Optional, Any, Union
from threading import Thread, Event
from queue import Queue

from sqlalchemy import Subquery, create_engine, and_, or_, text, func
from sqlalchemy.orm import Session
from sqlalchemy.pool import QueuePool
from sqlalchemy.engine.base import Engine
from sqlalchemy.engine import URL, engine_from_config
from sqlalchemy.util import immutabledict

from jsktoolbox.basetool.threads import ThBaseObject
from jsktoolbox.basetool.data import BData
from jsktoolbox.logstool.logs import LoggerClient, LoggerQueue
from jsktoolbox.configtool.main import Config as ConfigTool
from jsktoolbox.attribtool import ReadOnlyClass
from jsktoolbox.raisetool import Raise
from jsktoolbox.datetool import Timestamp
from jsktoolbox.stringtool.crypto import SimpleCrypto


from libs.base.classes import BModule, BLogs, BDebug
from libs.interfaces.modules import IRunModule
from libs.base.classes import BModuleConfig
from libs.templates.modules import TemplateConfigItem
from libs.com.message import Message, Multipart, Channel, AtChannel
from libs.app import AppName

from libs.db_models.connectors import LmsMysqlDatabase
import libs.db_models.mlms as mlms
import libs.db_models.lms as lms


class _Keys(object, metaclass=ReadOnlyClass):
    """Private Keys definition class.

    For internal purpose only.
    """

    # for configuration
    AT_CHANNEL: str = "at_channel"
    SQL_DATABASE: str = "sql_database"
    SQL_PASS: str = "sql_password"
    SQL_SERVER: str = "sql_server"
    SQL_USER: str = "sql_user"


class _ModuleConf(BModuleConfig):
    """Module Config private class."""

    @property
    def at_channel(self) -> Optional[List[str]]:
        """Return message channel configuration list."""
        var = self._get(varname=_Keys.AT_CHANNEL)
        if var is not None and not isinstance(var, List):
            raise Raise.error(
                "Expected list type.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        return var

    @property
    def sql_server(self) -> List[str]:
        """Return sql server address list."""
        var = self._get(varname=_Keys.SQL_SERVER)
        if var is not None and not isinstance(var, List):
            raise Raise.error(
                "Expected list type.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        return var

    @property
    def sql_database(self) -> str:
        """Returns sql table name."""
        var = self._get(varname=_Keys.SQL_DATABASE)
        if var is not None and not isinstance(var, str):
            raise Raise.error(
                "Expected str type.", TypeError, self._c_name, currentframe()
            )
        return var

    @property
    def sql_user(self) -> str:
        """Returns sql user name."""
        var = self._get(varname=_Keys.SQL_USER)
        if var is not None and not isinstance(var, str):
            raise Raise.error(
                "Expected str type.", TypeError, self._c_name, currentframe()
            )
        return var

    @property
    def sql_pass(self) -> str:
        """Returns sql user password."""
        var = self._get(varname=_Keys.SQL_PASS)
        if var is not None and not isinstance(var, str):
            raise Raise.error(
                "Expected str type", TypeError, self._c_name, currentframe()
            )
        return var


class MLmsTariff(Thread, ThBaseObject, BModule, IRunModule):
    """Example module."""

    def __init__(
        self,
        app_name: AppName,
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
        """Apply config from module_conf"""
        if self.module_conf is None:
            return False

        try:
            if self.module_conf.sleep_period:
                self.sleep_period = self.module_conf.sleep_period
            # check module configuration
            if not self.module_conf.at_channel:
                self.logs.message_critical = f"'{_Keys.AT_CHANNEL}' not configured"
                self.stop()
            if not self.module_conf.message_channel:
                self.logs.message_critical = (
                    f"'{_ModuleConf.Keys.MESSAGE_CHANNEL}' not configured"
                )
                self.stop()
            if not self.module_conf.sql_server:
                self.logs.message_critical = f"'{_Keys.SQL_SERVER}' not configured"
                self.stop()
            if not self.module_conf.sql_database:
                self.logs.message_critical = f"'{_Keys.SQL_DATABASE}' not configured"
                self.stop()
            if not self.module_conf.sql_user:
                self.logs.message_critical = f"'{_Keys.SQL_USER}' not configured"
                self.stop()
            if not self.module_conf.sql_pass:
                self.logs.message_critical = f"'{_Keys.SQL_PASS}' not configured"
                self.stop()
        except Exception as ex:
            self.logs.message_critical = f"{ex}"
            return False
        return True

    def run(self) -> None:
        """Main loop."""
        self.logs.message_notice = "starting..."

        if (
            self.module_conf is None
            or self.module_conf.message_channel is None
            or self.module_conf.at_channel is None
            or self._cfh is None
            or self._cfh.main_section_name is None
            or self.logs is None
            or self.logs.logs_queue is None
        ):
            return None

        # initialization local variables
        channel: Optional[AtChannel] = None
        try:
            channel = AtChannel(self.module_conf.at_channel)
        except Exception as ex:
            self.logs.message_critical = "channel configuration error"
            if self.debug:
                self.logs.message_debug = f"{ex}"
            self.stop()

        salt = self._cfh.get(self._cfh.main_section_name, "salt")
        password: str = ""
        if salt is not None:
            password: str = SimpleCrypto.multiple_decrypt(
                salt, self.module_conf.sql_pass
            )
        else:
            password = self.module_conf.sql_pass

        # initialization variables from config file
        if not self._apply_config():
            self.logs.message_error = "configuration error."
            return

        # database connection
        dbh = LmsMysqlDatabase(
            self.logs.logs_queue,
            {
                _Keys.SQL_SERVER: self.module_conf.sql_server,
                _Keys.SQL_DATABASE: self.module_conf.sql_database,
                _Keys.SQL_USER: self.module_conf.sql_user,
                _Keys.SQL_PASS: password,
            },
            verbose=self._verbose,
            debug=self.debug,
        )
        # set up connections
        if dbh.create_connections():
            self.logs.message_notice = "connected to database"
        else:
            self.logs.message_critical = "connection to database error, cannot continue"
            self.stop()

        if self.debug:
            self.logs.message_debug = "configuration processing complete"
            self.logs.message_debug = "entering to the main loop"

        # starting module loop
        while not self._stopped:
            if channel and channel.check:
                if self.debug:
                    self.logs.message_debug = "expired channel found"
                for chan in channel.get:
                    # message channel
                    if (
                        self.module_conf.message_channel
                        and chan in self.module_conf.message_channel
                    ):
                        # TODO: do something, build a message if necessary, put it in the qcom queue
                        pass

            # sleep time
            self.sleep()

        # exiting from loop
        self.logs.message_notice = "exit"

    def sleep(self) -> None:
        """Sleep interval for main loop."""
        sleep_break: float = Timestamp.now() + self.sleep_period
        while not self._stopped and sleep_break > Timestamp.now():
            time.sleep(0.2)

    def stop(self) -> None:
        """Set stop event."""
        if self.debug:
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
        if self._bm_debug is not None:
            return self._bm_debug
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
        out.append(TemplateConfigItem(desc="LMS tariff and node checker module."))
        out.append(TemplateConfigItem(desc="Variables:"))
        out.append(
            TemplateConfigItem(
                desc=f"'{_Keys.AT_CHANNEL}' [List[str]], comma separated communication channels list ['nr1:at', 'nr2:at']"
            )
        )
        out.append(
            TemplateConfigItem(
                desc=" where 'at' means the date/time generating notifications for given channel"
            )
        )
        out.append(
            TemplateConfigItem(desc=" 'at' format: semicolon-separated numeric list")
        )
        out.append(
            TemplateConfigItem(desc=" format: 'minute;hour;day-month;month;day-week'")
        )
        out.append(
            TemplateConfigItem(
                desc=" It is allowed to use '*' character, the '-' range separator and lists separated"
            )
        )
        out.append(TemplateConfigItem(desc=" by '|' character as field values."))
        out.append(TemplateConfigItem(desc=" All fields must be defined."))
        out.append(
            TemplateConfigItem(
                desc=f"'{_ModuleConf.Keys.MESSAGE_CHANNEL}' [List[str]] - message channels for notifications sent to customers."
            )
        )
        out.append(
            TemplateConfigItem(
                desc=f"'{_Keys.SQL_SERVER}' [List[str]] - list of SQL servers IP addresses"
            )
        )
        out.append(
            TemplateConfigItem(
                desc=f"'{_Keys.SQL_DATABASE}' [str] - name of lms database."
            )
        )
        out.append(
            TemplateConfigItem(
                desc=f"'{_Keys.SQL_USER}' [str] - username for database connection."
            )
        )
        out.append(
            TemplateConfigItem(
                desc=f"'{_Keys.SQL_PASS}' [str] - password for database connection."
            )
        )
        out.append(
            TemplateConfigItem(
                varname=_Keys.AT_CHANNEL,
                value=["1:0;0;7|10|12|13;*;*", "1:0;8|12|16|21;14;*;*"],
            )
        )
        out.append(
            TemplateConfigItem(varname=_ModuleConf.Keys.MESSAGE_CHANNEL, value=[1])
        )
        out.append(
            TemplateConfigItem(
                varname=_Keys.SQL_SERVER,
                value=[],
            )
        )
        out.append(
            TemplateConfigItem(
                varname=_Keys.SQL_DATABASE,
                value=None,
            )
        )
        out.append(
            TemplateConfigItem(
                varname=_Keys.SQL_USER,
                value=None,
            )
        )
        out.append(
            TemplateConfigItem(
                varname=_Keys.SQL_PASS,
                value=None,
            )
        )
        return out


# #[EOF]#######################################################################
