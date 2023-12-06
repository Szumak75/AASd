# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 23.11.2023

  Purpose: module for generating notifications for customers about the upcoming
  payment date.
"""

import time
from inspect import currentframe
from typing import Dict, List, Optional, Tuple, Any
from threading import Thread, Event
from queue import Queue
from copy import deepcopy

from sqlalchemy import create_engine, and_, text, func
from sqlalchemy.orm import (
    Session,
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy.pool import QueuePool
from sqlalchemy.engine.base import Engine
from sqlalchemy.engine import URL, engine_from_config

from jsktoolbox.libs.base_th import ThBaseObject
from jsktoolbox.logstool.logs import LoggerClient, LoggerQueue
from jsktoolbox.configtool.main import Config as ConfigTool
from jsktoolbox.stringtool.crypto import SimpleCrypto
from jsktoolbox.netaddresstool.ipv4 import Address
from jsktoolbox.attribtool import ReadOnlyClass
from jsktoolbox.raisetool import Raise
from jsktoolbox.datetool import Timestamp

from libs.base.classes import BModule, BLogs, BDebug
from libs.interfaces.modules import IRunModule
from libs.base.classes import BModuleConfig
from libs.interfaces.conf import IModuleConfig
from libs.templates.modules import TemplateConfigItem
from libs.com.message import Message, Multipart, AtChannel
from libs.tools.datetool import MDateTime

import libs.db_models.mlms as mlms


class _Keys(object, metaclass=ReadOnlyClass):
    """Private Keys definition class.

    For internal purpose only.
    """

    # for database class
    DPOOL = "__connection_pool__"
    # for module class
    MODCONF = "__MODULE_CONF__"
    # for configuration
    AT_CHANNEL = "at_channel"
    DCHANNEL = "diagnostic_channel"
    MCHANNEL = "message_channel"
    SLEEP_PERIOD = "sleep_period"
    SQL_SERVER = "sql_server"
    SQL_DATABASE = "sql_database"
    SQL_USER = "sql_user"
    SQL_PASS = "sql_password"
    # contact types
    # email notification: 8|32=40, type&40==40 and type&16384==0
    # mobile notification: 1|32=33, type&33==33 and type&16384==0
    # type&16384|8|32==40 - True
    CONTACT_MOBILE = 1
    CONTACT_FAX = 2
    CONTACT_LANDLINE = 4
    CONTACT_EMAIL = 8
    CONTACT_INVOICES = 16
    CONTACT_NOTIFICATIONS = 32
    CONTACT_BANKACCOUNT = 64
    CONTACT_TECHNICAL = 128
    CONTACT_URL = 256
    CONTACT_IM = 7680
    CONTACT_IM_GG = 512
    CONTACT_IM_YAHOO = 1024
    CONTACT_IM_SKYPE = 2048
    CONTACT_IM_FACEBOOK = 4096
    CONTACT_DISABLED = 16384
    CONTACT_DOCUMENTS = 32768


class _Database(BDebug, BLogs):
    """Database class."""

    def __init__(
        self,
        qlog: LoggerQueue,
        config: Dict,
        verbose: bool = False,
        debug: bool = False,
    ):
        """Constructor."""
        self.logs = LoggerClient(queue=qlog, name=self._c_name)
        self._debug = debug
        self._verbose = verbose

        # config variables
        self._data[_Keys.SQL_SERVER] = config[_Keys.SQL_SERVER]
        self._data[_Keys.SQL_DATABASE] = config[_Keys.SQL_DATABASE]
        self._data[_Keys.SQL_USER] = config[_Keys.SQL_USER]
        self._data[_Keys.SQL_PASS] = config[_Keys.SQL_PASS]

        # connection pool
        self._data[_Keys.DPOOL] = []

    def create_connections(self) -> bool:
        """Create connections pool."""
        config = {
            "db.url": None,
            "db.echo": False,
            "db.poolclass": QueuePool,
            "db.pool_pre_ping": True,
            "db.pool_size": 5,
            "db.pool_recycle": 120,
            "db.pool_use_lifo": True,
            "db.echo_pool": True,
            "db.query_cache_size": 10,
            # "db.connect_timeout": 5,
        }
        for ip in self._data[_Keys.SQL_SERVER]:
            ipo = Address(ip)
            for dialect in ("pymysql", "mysqlconnector"):
                url = URL(
                    f"mysql+{dialect}",
                    username="lms3",
                    password=f"{SimpleCrypto.multiple_decrypt(salt, '//4AAHAAAABMAAAAagAAAEkAAAA1AAAAZAAAADcAAAB6AAAAbgAAAGcAAABtAAAANQAAAE0AAABlAAAASgAAAHUAAAA=')}",
                    host=ip,
                    database="lmsv3",
                    port=3306,
                    query={
                        "charset": "utf8mb4",
                    },
                )
                try:
                    config["db.url"] = url
                    engine = engine_from_config(config, prefix="db.")
                    with engine.connect() as connection:
                        connection.execute(text("SELECT 1"))
                    if self._debug:
                        self.logs.message_debug = f"add connection to server: {ipo} with backend: {backend}"
                    self._data[_Keys.DPOOL].append(engine)
                    break
                except Exception as ex:
                    if self._debug:
                        self.logs.message_debug = (
                            f"Create engine thrown exception: {ex}"
                        )
        if len(self._data[_Keys.DPOOL]) > 0:
            return True
        return False

    @property
    def session(self) -> Optional[Session]:
        """Returns db session."""
        for item in self._data[_Keys.DPOOL]:
            engine: Engine = item
            try:
                session = Session(engine)
                if session is not None:
                    if self._debug:
                        self.logs.message_debug = (
                            f"create session for {engine}"
                        )
                    return session
            except:
                continue
        return None


class _ModuleConf(IModuleConfig, BModuleConfig):
    """Module Config private class."""

    def _get(self, varname: str) -> Any:
        """Get variable from config."""
        return self._cfh.get(self._section, varname)

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
    def diagnostic_channel(self) -> Optional[List[str]]:
        """Return diagnostic channel list."""
        var = self._get(varname=_Keys.DCHANNEL)
        if var is not None and not isinstance(var, List):
            raise Raise.error(
                "Expected list type.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        return var

    @property
    def message_channel(self) -> Optional[List[str]]:
        """Return message channel list."""
        var = self._get(varname=_Keys.MCHANNEL)
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
        if var is None:
            return None
        if not isinstance(var, (int, float)):
            raise Raise.error(
                "Expected float type.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        return float(var)

    @property
    def sql_server(self) -> List[str]:
        """Return sql server address list."""
        var = self._get(varname=_Keys.SQL_SERVER)
        if var is not None and not isinstance(var, List):
            raise Raise.error(
                "Expected list type", TypeError, self._c_name, currentframe()
            )
        return var

    @property
    def sql_database(self) -> str:
        """Returns sql table name."""
        var = self._get(varname=_Keys.SQL_DATABASE)
        if var is not None and not isinstance(var, str):
            raise Raise.error(
                "Expected str type", self._c_name, currentframe()
            )
        return var

    @property
    def sql_user(self) -> str:
        """Returns sql user name."""
        var = self._get(varname=_Keys.SQL_USER)
        if var is not None and not isinstance(var, str):
            raise Raise.error(
                "Expected str type", self._c_name, currentframe()
            )
        return var

    @property
    def sql_pass(self) -> str:
        """Returns sql user password."""
        var = self._get(varname=_Keys.SQL_PASS)
        if var is not None and not isinstance(var, str):
            raise Raise.error(
                "Expected str type", self._c_name, currentframe()
            )
        return var


class MLmspayment(Thread, ThBaseObject, BModule, IRunModule):
    """LMS payment module.

    For generating notifications for customers about the upcoming
    payment date.
    """

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
        self.sleep_period = 45.0

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
            if not self.module_conf.at_channel:
                self.logs.message_critical = (
                    f"'{_Keys.AT_CHANNEL}' not configured"
                )
                self.stop()
            if not self.module_conf.message_channel:
                self.logs.message_critical = (
                    f"'{_Keys.MCHANNEL}' not configured"
                )
                self.stop()
            if not self.module_conf.diagnostic_channel:
                self.logs.message_warning = f"'{_Keys.DCHANNEL}' not configured, maybe it's not an error, but check..."
            if not self.module_conf.sql_server:
                self.logs.message_critical = (
                    f"'{_Keys.SQL_SERVER}' not configured"
                )
                self.stop()
            if not self.module_conf.sql_database:
                self.logs.message_critical = (
                    f"'{_Keys.SQL_DATABASE}' not configured"
                )
                self.stop()
            if not self.module_conf.sql_user:
                self.logs.message_critical = (
                    f"'{_Keys.SQL_USER}' not configured"
                )
                self.stop()
            if not self.module_conf.sql_pass:
                self.logs.message_critical = (
                    f"'{_Keys.SQL_PASS}' not configured"
                )
                self.stop()
        except Exception as ex:
            self.logs.message_critical = f"{ex}"
            return False
        return True

    def __get_customers_for_verification(
        self, dbh: _Database, channel: int
    ) -> None:
        """Get list of Customes to verification."""
        email = _Keys.CONTACT_EMAIL | _Keys.CONTACT_NOTIFICATIONS
        mobile = _Keys.CONTACT_MOBILE | _Keys.CONTACT_NOTIFICATIONS
        disabled = _Keys.CONTACT_DISABLED

        out_debt = []
        out_contact = []
        out_tariff = []

        session = dbh.session
        if session is None:
            self.logs.message_critical = "cannot make database operations"
            return

        # get customer max id
        maxid: int = session.query(func.max(mlms.MCustomer.id)).first()[0]
        cfrom = 0
        cto = 100
        # customers query
        while cfrom < maxid:
            customers: List[mlms.MCustomer] = (
                session.query(mlms.MCustomer)
                .filter(
                    mlms.MCustomer.deleted == 0,
                    and_(
                        mlms.MCustomer.id >= cfrom, mlms.MCustomer.id < cto
                    ),
                )
                .order_by(mlms.MCustomer.id)
                .all()
            )
            # increment search range
            cfrom = cto
            cto += 100

            # analysis
            for item1 in customers:
                customer: mlms.MCustomer = item1
                # build debt list
                if (
                    customer.balance < 0
                    and MDateTime.elapsed_time_from_timestamp(
                        customer.dept_timestamp
                    )
                    > MDateTime.elapsed_time_from_seconds(60 * 60 * 24 * 30)
                ):
                    out_debt.append(deepcopy(customer))
                # build contact list
                if customer.tariffs and customer.has_active_node is not None:
                    test = False
                    for item2 in customer.contacts:
                        contact: mlms.CustomerContact = item2
                        if (
                            contact.type & email == email
                            and contact.type & disabled == 0
                        ) or (
                            contact.type & mobile == mobile
                            and contact.type & disabled == 0
                        ):
                            test = True
                    if not test:
                        out_contact.append(deepcopy(customer))
                elif not customer.tariffs:
                    out_tariff.append(deepcopy(customer))

        self.__send_diagnostic(channel, [out_debt, out_contact, out_tariff])

    def __get_indebted_customers_list(
        self, dbh: _Database, channel: int
    ) -> None:
        """Gets a list of Customers for sending notifications."""
        out = []
        email = _Keys.CONTACT_EMAIL | _Keys.CONTACT_NOTIFICATIONS
        mobile = _Keys.CONTACT_MOBILE | _Keys.CONTACT_NOTIFICATIONS
        disabled = _Keys.CONTACT_DISABLED
        # create session
        if dbh.create_connections():
            session = dbh.session
            if session is None:
                self.logs.message_critical = (
                    "cannot make database operations"
                )
                self.stop()
        else:
            self.logs.message_critical = "cannot connect to the database"
            self.stop()

        if session:
            customers: mlms.MCustomer = (
                session.query(mlms.MCustomer)
                .filter(
                    mlms.MCustomer.deleted == 0,
                    mlms.MCustomer.mailingnotice == 1,
                    # mlms.MCustomer.id < 1000,
                )
                .all()
            )
            for item1 in customers:
                customer: mlms.MCustomer = item1
                if customer.balance < 0:
                    test = False

                    for item2 in customer.contacts:
                        contact: mlms.MCustomerContact = item2
                        if (
                            contact.type & email == email
                            and contact.type & disabled == 0
                        ) or (
                            contact.type & mobile == mobile
                            and contact.type & disabled == 0
                        ):
                            test = True
                    if (
                        customer.tariffs
                        and customer.has_active_node is not None
                        and test
                    ):
                        out.append(customer)

    def __send_diagnostic(self, channel: int, data: List) -> None:
        """Make email notification for diagnostic channel."""
        debt_check, contact_check, tariff_check = data
        nemail = _Keys.CONTACT_EMAIL | _Keys.CONTACT_NOTIFICATIONS
        email = _Keys.CONTACT_EMAIL
        mobile = _Keys.CONTACT_MOBILE | _Keys.CONTACT_NOTIFICATIONS
        disabled = _Keys.CONTACT_DISABLED
        style = """<style>
body { font-size: 8pt; font-family: Tahoma, Verdana, Arial, Helvetica; background-color: #EBE4D6; margin: 0; padding: 0; vertical-align: middle; }
h1 { font-size: 14pt; font-family: Tahoma, Verdana, Arial, Helvetica; }
h2 { font-size: 12pt; font-family: Tahoma, Verdana, Arial, Helvetica; }
h3 { font-size: 10pt; font-family: Tahoma, Verdana, Arial, Helvetica; }
table { border-collapse: collapse; border-color: #000000 }
td { font-size: 8pt; font-family: Tahoma, Verdana, Arial, Helvetica; vertical-align: middle; border-color: black; }
th { background-color: black; color: white; }
th, td { text-align: left; padding: 2px; }
tr:nth-child(even){background-color: #DFD5BD}
a { text-decoration: none; vertical-align: baseline; }
a:link { color: #800000; }
a:active { color: #336600; }
a:visited { color: #800000; }
a.blend { color: #888888; }
a:hover { text-decoration: underline; color: #336600; }
div.centered { text-align: center; }
div.centered table { margin: 0 auto; text-align: left; }
</style>"""
        # debt
        if debt_check:
            template = "<tr><td>{nr}</td><td><a href='https://lms3.air-net.gda.pl/?m=customerinfo&id={cid}'>{cid}</a></td><td>{nazwa}</td><td>{bilans}</td><td>{od}</td><td>{info}</td></tr>"
            mes = Message()
            mes.channel = channel
            mes.subject = "[AIR-NET] Klienci zadłużeni powyżej 30 dni."
            # head
            mes.mmessages = {}
            mes.mmessages[Multipart.HTML] = [
                "<html>",
                "<head></head>",
                "<body>",
                style,
                "<div class='centered'><h1>Wykaz klientów z przedawnionym zadłużeniem.</h1></div>",
                "<div class='centered'>",
                "<table>",
                "<tr><th>nr:</th><th>cid:</th><th>nazwa:</th><th>bilans:</th><th>od:</th><th>uwagi:</th></tr>",
            ]
            count = 0
            for item in debt_check:
                info = ""
                count += 1
                customer: mlms.MCustomer = item
                # uwagi
                has_email = False
                has_nemail = False
                for item2 in customer.contacts:
                    contact: mlms.MCustomerContact = item2
                    if (
                        contact.type & email == email
                        and contact.type & disabled == 0
                    ):
                        has_email = True
                    if (
                        contact.type & nemail == nemail
                        and contact.type & disabled == 0
                    ):
                        has_nemail = True
                if not has_email:
                    info += "brak email, "
                elif not has_nemail:
                    info += "brak zgody email, "
                if not customer.has_active_node:
                    info += "blokada, "
                if not customer.tariffs:
                    info += "brak taryf, "
                info = info.strip()[:-1]

                mes.mmessages[Multipart.HTML].append(
                    template.format(
                        nr=count,
                        cid=customer.id,
                        nazwa=f"{customer.name} {customer.lastname}",
                        bilans=customer.balance,
                        od=f"{MDateTime.elapsed_time_from_timestamp(customer.dept_timestamp).days} dni, {MDateTime.elapsed_time_from_seconds(MDateTime.elapsed_time_from_timestamp(customer.dept_timestamp).seconds)}",
                        info=info,
                    )
                )
            # foot
            mes.mmessages[Multipart.HTML].extend(
                [
                    "<tr><td colspan='6'><hr></td></tr>",
                    "</table>",
                    "</div>",
                    "</body>",
                    "</html>",
                ]
            )
            # put message to communication queue
            self.qcom.put(mes)

        # contacts
        if contact_check:
            template = "<tr><td>{nr}</td><td><a href='https://lms3.air-net.gda.pl/?m=customerinfo&id={cid}'>{cid}</a></td><td>{nazwa}</td><td>{info}</td></tr>"
            mes = Message()
            mes.channel = channel
            mes.subject = "[AIR-NET] Klienci bez zgody na kontakt."
            # head
            mes.mmessages = {}
            mes.mmessages[Multipart.HTML] = [
                "<html>",
                "<head></head>",
                "<body>",
                style,
                "<div class='centered'><h1>Wykaz klientów do sprawdzenia zgód kontaktowych.</h1></div>",
                "<div class='centered'>",
                "<table>",
                "<tr><th>nr:</th><th>cid:</th><th>nazwa:</th><th>uwagi:</th></tr>",
            ]
            count = 0
            info = ""
            for item in contact_check:
                count += 1
                customer: mlms.MCustomer = item
                mes.mmessages[Multipart.HTML].append(
                    template.format(
                        nr=count,
                        cid=customer.id,
                        nazwa=f"{customer.name} {customer.lastname}",
                        info=info,
                    )
                )
            # foot
            mes.mmessages[Multipart.HTML].extend(
                [
                    "<tr><td colspan='4'><hr></td></tr>",
                    "</table>",
                    "</div>",
                    "</body>",
                    "</html>",
                ]
            )
            # put message to communication queue
            self.qcom.put(mes)

        # tariff
        if tariff_check:
            template = "<tr><td>{nr}</td><td><a href='https://lms3.air-net.gda.pl/?m=customerinfo&id={cid}'>{cid}</a></td><td>{nazwa}</td><td>{info}</td></tr>"
            mes = Message()
            mes.channel = channel
            mes.subject = "[AIR-NET] Klienci bez taryf."
            # head
            mes.mmessages = {}
            mes.mmessages[Multipart.HTML] = [
                "<html>",
                "<head></head>",
                "<body>",
                style,
                "<div class='centered'><h1>Wykaz klientów do bez przypisanych taryf.</h1></div>",
                "<div class='centered'>",
                "<table>",
                "<tr><th>nr:</th><th>cid:</th><th>nazwa:</th><th>uwagi:</th></tr>",
            ]
            count = 0
            for item in tariff_check:
                count += 1
                customer: mlms.MCustomer = item
                # uwagi
                info = ""
                if (
                    customer.has_active_node is not None
                    and customer.has_active_node == True
                ):
                    info += "aktywna usługa, "
                info = info.strip()[:-1]
                mes.mmessages[Multipart.HTML].append(
                    template.format(
                        nr=count,
                        cid=customer.id,
                        nazwa=f"{customer.name} {customer.lastname}",
                        info=info,
                    )
                )
            # foot
            mes.mmessages[Multipart.HTML].extend(
                [
                    "<tr><td colspan='4'><hr></td></tr>",
                    "</table>",
                    "</div>",
                    "</body>",
                    "</html>",
                ]
            )
            # put message to communication queue
            self.qcom.put(mes)

    def run(self) -> None:
        """Main loop."""
        self.logs.message_notice = "starting..."

        # initialization local variables
        try:
            channel = AtChannel(self.module_conf.at_channel)
        except Exception as ex:
            self.logs.message_critical = "channel configuration error"
            if self.debug:
                self.logs.message_debug = f"{ex}"
            self.stop()

        salt = self._cfh.get(self._cfh.main_section_name, "salt")
        if salt is not None:
            password = SimpleCrypto.multiple_decrypt(
                salt, self.module_conf.sql_pass
            )
        else:
            password = self.module_conf.sql_pass

        # initialization variables from config file
        if not self._apply_config():
            self.logs.message_error = "configuration error."
            return

        # database connection
        dbh = _Database(
            self.logs.logs_queue,
            {
                _Keys.SQL_SERVER: self.module_conf.sql_server,
                _Keys.SQL_DATABASE: self.module_conf.sql_database,
                _Keys.SQL_USER: self.module_conf.sql_user,
                _Keys.SQL_PASS: password,
            },
            verbose=self._verbose,
            debug=self._debug,
        )
        # set up connections
        if dbh.create_connections():
            self.logs.message_notice = "connected to database"
        else:
            self.logs.message_critical = (
                "connection to database error, cannot continue"
            )
            self.stop()

        if self.debug:
            self.logs.message_debug = "configuration processing complete"

        if self.debug:
            self.logs.message_debug = "entering to the main loop"

        # starting module loop
        while not self.stopped:
            if channel.check:
                if self.debug:
                    self.logs.message_debug = "expired channel found"
                for chan in channel.get:
                    # diagnostic channel
                    if (
                        self.module_conf.diagnostic_channel
                        and chan in self.module_conf.diagnostic_channel
                    ):
                        self.__get_customers_for_verification(
                            dbh, int(chan)
                        ),
                        # self.__send_diagnostic(
                        # int(chan),
                        # self.__get_customers_for_verification(dbh),
                        # )

                    # message channel
                    if (
                        self.module_conf.message_channel
                        and chan in self.module_conf.message_channel
                    ):
                        pass
            self.sleep()

        # exiting from loop
        self.logs.message_notice = "exit"

    def sleep(self) -> None:
        """Sleep interval for main loop."""
        sbreak = Timestamp.now + self.sleep_period
        while not self.stopped and sbreak > Timestamp.now:
            time.sleep(0.2)

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
            TemplateConfigItem(desc="LMS payment notification module.")
        )
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
            TemplateConfigItem(
                desc=" 'at' format: semicolon-separated numeric list"
            )
        )
        out.append(
            TemplateConfigItem(
                desc=" format: 'minute;hour;day-month;month;day-week'"
            )
        )
        out.append(
            TemplateConfigItem(
                desc=" It is allowed to use '*' character, the '-' range separator and lists separated"
            )
        )
        out.append(
            TemplateConfigItem(desc=" by '|' character as field values.")
        )
        out.append(TemplateConfigItem(desc=" All fields must be defined."))
        out.append(
            TemplateConfigItem(
                desc=f"'{_Keys.DCHANNEL}' [List[str]] - diagnostic channels for sending statistics."
            )
        )
        out.append(
            TemplateConfigItem(
                desc=f"'{_Keys.MCHANNEL}' [List[str]] - message channels for notifications sent to customers."
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
        out.append(TemplateConfigItem(varname=_Keys.DCHANNEL, value=[]))
        out.append(TemplateConfigItem(varname=_Keys.MCHANNEL, value=[1]))
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
