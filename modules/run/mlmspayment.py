# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 23.11.2023

  Purpose: a module for generating notifications for LMS customers about the upcoming payment date.

  WWW: https://lms.org.pl/
"""

import time
from datetime import timedelta
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
from libs.templates.modules import TemplateConfigItem
from libs.com.message import Message, Multipart, AtChannel
from libs.tools.datetool import MDateTime

import libs.db_models.mlms as mlms
import libs.db_models.lms as lms


class _Keys(object, metaclass=ReadOnlyClass):
    """Private Keys definition class.

    For internal purpose only.
    """

    # for database class
    DPOOL: str = "__connection_pool__"
    # for configuration
    AT_CHANNEL: str = "at_channel"
    CUTOFF: str = "cutoff_time"
    DCHANNEL: str = "diagnostic_channel"
    DPAYTIME: str = "default_paytime"
    LMS_URL: str = "lms_url"
    MFOOTER: str = "message_footer"
    MNOTIFY: str = "payment_message"
    SQL_DATABASE: str = "sql_database"
    SQL_PASS: str = "sql_password"
    SQL_SERVER: str = "sql_server"
    SQL_USER: str = "sql_user"
    USER_URL: str = "user_url"
    SKIP_GROUPS: str = "skip_group_id"
    # contact types
    # email notification: 8|32=40, type&40==40 and type&16384==0
    # mobile notification: 1|32=33, type&33==33 and type&16384==0
    # type&16384|8|32==40 - True
    CONTACT_BANKACCOUNT: int = 64
    CONTACT_DISABLED: int = 16384
    CONTACT_DOCUMENTS: int = 32768
    CONTACT_EMAIL: int = 8
    CONTACT_FAX: int = 2
    CONTACT_IM: int = 7680
    CONTACT_IM_FACEBOOK: int = 4096
    CONTACT_IM_GG: int = 512
    CONTACT_IM_SKYPE: int = 2048
    CONTACT_IM_YAHOO: int = 1024
    CONTACT_INVOICES: int = 16
    CONTACT_LANDLINE: int = 4
    CONTACT_MOBILE: int = 1
    CONTACT_NOTIFICATIONS: int = 32
    CONTACT_TECHNICAL: int = 128
    CONTACT_URL: int = 256
    # diagnostic
    DCONT: str = "__cont__"
    DDEBT: str = "__debt__"
    DTARIFF: str = "__tariff__"


class _Database(BDebug, BLogs):
    """Database class."""

    def __init__(
        self,
        qlog: LoggerQueue,
        config: Dict,
        verbose: bool = False,
        debug: bool = False,
    ) -> None:
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
        """Create connection pool, second variant."""
        for dialect, fail in ("pymysql", False), ("mysqlconnector", True):
            if not fail:
                for ip in self._data[_Keys.SQL_SERVER]:
                    url: URL = URL.create(
                        f"mysql+{dialect}",
                        username=self._data[_Keys.SQL_USER],
                        password=self._data[_Keys.SQL_PASS],
                        host=ip,
                        database=self._data[_Keys.SQL_DATABASE],
                        port=3306,
                        query=immutabledict(
                            {
                                "charset": "utf8mb4",
                            }
                        ),
                    )
                    connection_args: Dict[str, Any] = {}
                    # connection_args["connect_timeout"] = 5
                    # create engine
                    engine: Engine = create_engine(
                        url=url,
                        connect_args=connection_args,
                        pool_recycle=3600,
                        poolclass=QueuePool,
                    )
                    try:
                        with engine.connect() as connection:
                            connection.execute(text("SELECT 1"))
                        if self._debug:
                            self.logs.message_notice = f"add connection to server: {ip} with backend: {dialect}"
                        self._data[_Keys.DPOOL].append(engine)
                    except Exception as ex:
                        self.logs.message_warning = f"connect to server: {ip} with backend: {dialect} error: {ex}"
            else:
                url: URL = URL.create(
                    f"mysql+{dialect}",
                    username=self._data[_Keys.SQL_USER],
                    password=self._data[_Keys.SQL_PASS],
                    host=self._data[_Keys.SQL_SERVER][0],
                    database=self._data[_Keys.SQL_DATABASE],
                    port=3306,
                    query=immutabledict(
                        {
                            "charset": "utf8mb4",
                        }
                    ),
                )
                connection_args: Dict[str, Any] = {}
                connection_args["connect_timeout"] = 600
                connection_args["failover"] = []
                for ip in self._data[_Keys.SQL_SERVER][1:]:
                    connection_args["failover"].append(
                        {
                            "user": self._data[_Keys.SQL_USER],
                            "password": self._data[_Keys.SQL_PASS],
                            "host": ip,
                            "port": 3306,
                            "database": self._data[_Keys.SQL_DATABASE],
                            "pool_size": 5,
                            "pool_name": ip,
                        }
                    )
                # create engine
                engine: Engine = create_engine(
                    url=url,
                    connect_args=connection_args,
                    pool_recycle=3600,
                    poolclass=QueuePool,
                )
                try:
                    with engine.connect() as connection:
                        connection.execute(text("SELECT 1"))
                    if self._debug:
                        self.logs.message_notice = f"add connection to server: {self._data[_Keys.SQL_SERVER][0]} with backend: {dialect}"
                    self._data[_Keys.DPOOL].append(engine)
                except Exception as ex:
                    self.logs.message_warning = f"connect to server: {self._data[_Keys.SQL_SERVER][0]} with backend: {dialect} error: {ex}"

        if self._data[_Keys.DPOOL] is not None and len(self._data[_Keys.DPOOL]) > 0:
            return True
        return False

    def create_connections_failover(self) -> bool:
        """Create connections pool.

        WARNING: incredible slow
        """
        config = {
            "db.url": None,
            "db.echo": False,
            "db.poolclass": QueuePool,
            "db.pool_pre_ping": True,
            "db.pool_size": 5,
            "db.max_overflow": 10,
            "db.pool_recycle": 120,
            "db.echo_pool": True,
            "db.query_cache_size": 500,
            "db.pool_timeout": 5,
            "db.pool_use_lifo": True,
        }

        for dialect, fail in ("mysqlconnector", True), ("pymysql", False):
            url = URL(
                f"mysql+{dialect}",
                username=self._data[_Keys.SQL_USER],
                password=self._data[_Keys.SQL_PASS],
                host=self._data[_Keys.SQL_SERVER][0],
                database=self._data[_Keys.SQL_DATABASE],
                port=3306,
                query=immutabledict(
                    {
                        "charset": "utf8mb4",
                    }
                ),
            )
            try:
                config["db.url"] = url

                if fail:
                    connection_args = {}
                    connection_args["connect_timeout"] = 600
                    # connection_args["raise_on_warnings"] = True
                    connection_args["failover"] = []
                    for ip in self._data[_Keys.SQL_SERVER][1:]:
                        connection_args["failover"].append(
                            {
                                "user": self._data[_Keys.SQL_USER],
                                "password": self._data[_Keys.SQL_PASS],
                                "host": ip,
                                "port": 3306,
                                "database": self._data[_Keys.SQL_DATABASE],
                                "pool_size": 5,
                                "pool_name": ip,
                            }
                        )

                    engine = engine_from_config(
                        config, prefix="db.", connect_args=connection_args
                    )
                else:
                    connection_args = {}
                    connection_args["connect_timeout"] = 600
                    engine = engine_from_config(
                        config, prefix="db.", connect_args=connection_args
                    )

                with engine.connect() as connection:
                    connection.execute(text("SELECT 1"))
                if self._debug:
                    self.logs.message_debug = f"add connection to server: {self._data[_Keys.SQL_SERVER][0]} with backend: {dialect}"
                self._data[_Keys.DPOOL].append(engine)
                break
            except Exception as ex:
                if self._debug:
                    self.logs.message_debug = f"Create engine thrown exception: {ex}"

        if len(self._data[_Keys.DPOOL]) > 0:
            return True

        return False

    @property
    def session(self) -> Optional[Session]:
        """Returns db session."""
        session = None
        for item in self._data[_Keys.DPOOL]:
            engine: Engine = item
            try:
                session = Session(engine)
                var = session.query(func.max(mlms.MCustomer.id)).first()
                # self.logs.message_notice = f"check query: {var}"
                if self._debug:
                    self.logs.message_debug = f"create session for {engine}"

            except:
                session = None
            else:
                break

        return session


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
    def cutoff_time(self) -> Optional[int]:
        """Returns cutoff time in days number."""
        var = self._get(varname=_Keys.CUTOFF)
        if var is not None and not isinstance(var, int):
            raise Raise.error(
                "Expected int type.", TypeError, self._c_name, currentframe()
            )
        return var

    @property
    def default_paytime(self) -> Optional[int]:
        """Returns default pay time in days number."""
        var = self._get(varname=_Keys.DPAYTIME)
        if var is not None and not isinstance(var, int):
            raise Raise.error(
                "Expected int type.", TypeError, self._c_name, currentframe()
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
    def lms_url(self) -> Optional[str]:
        """Return message channel list."""
        var = self._get(varname=_Keys.LMS_URL)
        if var is not None and not isinstance(var, str):
            raise Raise.error(
                "Expected string type.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        return var

    @property
    def user_url(self) -> Optional[str]:
        """Return message channel list."""
        var = self._get(varname=_Keys.USER_URL)
        if var is not None and not isinstance(var, str):
            raise Raise.error(
                "Expected string type.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        return var

    @property
    def message_footer(self) -> Optional[Union[List[str], str]]:
        """Return message footer list."""
        var = self._get(varname=_Keys.MFOOTER)
        if var is not None and not isinstance(var, (List, str)):
            raise Raise.error(
                "Expected string type.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        return var

    @property
    def payment_message(self) -> Optional[List[str]]:
        """Return message channel list."""
        var = self._get(varname=_Keys.MNOTIFY)
        if var is not None and not isinstance(var, List):
            raise Raise.error(
                "Expected list type.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        return var

    @property
    def skip_groups(self) -> Optional[List[int]]:
        """Returns groups id to skip."""
        var = self._get(varname=_Keys.SKIP_GROUPS)
        if var is not None and not isinstance(var, List):
            raise Raise.error(
                "Expected list type.", TypeError, self._c_name, currentframe()
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
        self._data[_ModuleConf.Keys.MODCONF] = _ModuleConf(self._cfh, self._section)

        # logging level
        self._debug = debug
        self._verbose = verbose

        # logger client initialization
        self.logs = LoggerClient(queue=qlog, name=self._c_name)

        # communication queue
        self.qcom = qcom

        # init internal buffer
        self._data[_Keys.DDEBT] = []
        self._data[_Keys.DCONT] = []
        self._data[_Keys.DTARIFF] = []

    def __clean_diagnostic(self) -> None:
        """Initialize diagnostic data buffer."""
        self._data[_Keys.DDEBT].clear()
        self._data[_Keys.DCONT].clear()
        self._data[_Keys.DTARIFF].clear()

    def _apply_config(self) -> bool:
        """Apply config from module_conf"""
        if self.module_conf is None:
            return False
        try:
            if self.module_conf.sleep_period:
                self.sleep_period = self.module_conf.sleep_period
            if not self.module_conf.lms_url:
                self.logs.message_critical = f"'{_Keys.LMS_URL}' not set"
                self.stop()
            if not self.module_conf.user_url:
                self.logs.message_critical = f"'{_Keys.USER_URL}' not set"
                self.stop()
            if not self.module_conf.payment_message:
                self.logs.message_critical = f"'{_Keys.MNOTIFY}' not set"
                self.stop()
            if not self.module_conf.default_paytime:
                self.logs.message_critical = f"'{_Keys.DPAYTIME}' not set"
                self.stop()
            if not self.module_conf.cutoff_time:
                self.logs.message_critical = f"'{_Keys.CUTOFF}' not set"
                self.stop()
            if not self.module_conf.at_channel:
                self.logs.message_critical = f"'{_Keys.AT_CHANNEL}' not configured"
                self.stop()
            if not self.module_conf.message_channel:
                self.logs.message_critical = (
                    f"'{_ModuleConf.Keys.MESSAGE_CHANNEL}' not configured"
                )
                self.stop()
            if not self.module_conf.skip_groups:
                self.logs.message_warning = f"'{_Keys.SKIP_GROUPS}' not configured, maybe it's not error, but check..."
            if not self.module_conf.diagnostic_channel:
                self.logs.message_warning = f"'{_Keys.DCHANNEL}' not configured, maybe it's not an error, but check..."
            if not self.module_conf.message_footer:
                self.logs.message_warning = f"'{_Keys.MFOOTER}' not configured, maybe it's not error, but check..."
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

    def __get_customers_for_verification(self, dbh: _Database, channel: int) -> None:
        """Get list of Customers to verification."""
        email: int = _Keys.CONTACT_EMAIL | _Keys.CONTACT_NOTIFICATIONS
        mobile: int = _Keys.CONTACT_MOBILE | _Keys.CONTACT_NOTIFICATIONS
        disabled: int = _Keys.CONTACT_DISABLED

        STEEP: int = 10

        skip_groups: List[int] = (
            self.module_conf.skip_groups
            if self.module_conf and self.module_conf.skip_groups
            else list()
        )

        if self.debug or self.verbose:
            self.logs.message_debug = "get customers for verification"
            self.logs.message_debug = f"skip group ids: {skip_groups}"

        # reset buffer
        self.__clean_diagnostic()

        session: Optional[Session] = dbh.session
        if session is None:
            self.logs.message_critical = "cannot make database operations"
            return

        # get customer max id
        row = session.query(func.max(mlms.MCustomer.id)).first()
        maxid: int = row[0] if row is not None else 0
        cfrom: int = 0
        cto = STEEP
        tstart: int = Timestamp.now

        # excluded group
        group: Subquery = (
            session.query(lms.CustomerAssignment.customerid)
            .filter(lms.CustomerAssignment.customergroupid.in_(skip_groups))
            .group_by(lms.CustomerAssignment.customerid)
            .subquery()
        )

        # customers query
        while cfrom < maxid:
            if self.debug:
                self.logs.message_notice = f"Check customers from id: {cfrom} to {cto}, elapsed time: {MDateTime.elapsed_time_from_seconds(Timestamp.now-tstart)}"
            customers: List[mlms.MCustomer] = (
                session.query(mlms.MCustomer)
                .outerjoin(
                    group,
                    mlms.MCustomer.id == group.c.customerid,
                )
                .filter(
                    mlms.MCustomer.deleted == 0,
                    mlms.MCustomer.id >= cfrom,
                    mlms.MCustomer.id < cto,
                    group.c.customerid == None,
                )
                .order_by(mlms.MCustomer.id)
                .all()
            )
            # increment search range
            cfrom = cto
            cto += STEEP

            # analysis
            for customer in customers:
                # build debt list
                if (
                    customer.balance < 0
                    and customer.debt_timestamp > 0
                    and MDateTime.elapsed_time_from_timestamp(customer.debt_timestamp)
                    > MDateTime.elapsed_time_from_seconds(60 * 60 * 24 * 30)
                ):
                    self.__add_diagnostic_debt(customer)
                # build contact list
                if customer.tariffs and customer.has_active_node is not None:
                    test = False
                    for contact in customer.contacts:
                        if (
                            contact.type & email == email
                            and contact.type & disabled == 0
                        ) or (
                            contact.type & mobile == mobile
                            and contact.type & disabled == 0
                        ):
                            test = True
                    if not test:
                        self.__add_diagnostic_contact(customer)
                elif not customer.tariffs:
                    self.__add_diagnostic_tariff(customer)
        if self.debug:
            self.logs.message_info = f"Customer verification time: {MDateTime.elapsed_time_from_seconds(Timestamp.now-tstart)}"

        self.__send_diagnostic(channel)

        # close session
        session.close()

    def __get_indebted_customers(self, dbh: _Database, channel: int) -> None:
        """Gets a list of Customers for sending notifications."""
        STEEP: int = 10
        if (
            self.module_conf is None
            or self.module_conf.default_paytime is None
            or self.module_conf.cutoff_time is None
            or self.module_conf.payment_message is None
        ):
            return None

        skip_groups: List[int] = (
            self.module_conf.skip_groups if self.module_conf.skip_groups else list()
        )

        if self.debug or self.verbose:
            self.logs.message_debug = "get indebted customers list"
            self.logs.message_debug = f"skip group ids: {skip_groups}"

        # create session
        session: Optional[Session] = dbh.session
        if session is None:
            self.logs.message_critical = "cannot make database operations"
            return

        row = session.query(func.max(mlms.MCustomer.id)).first()
        maxid: int = row[0] if row is not None else 0
        cfrom: int = 0
        cto: int = STEEP
        tstart: int = Timestamp.now

        # excluded group
        group: Subquery = (
            session.query(lms.CustomerAssignment.customerid)
            .filter(lms.CustomerAssignment.customergroupid.in_(skip_groups))
            .group_by(lms.CustomerAssignment.customerid)
            .subquery()
        )

        # customers query
        while cfrom < maxid:
            if self.debug:
                self.logs.message_notice = f"Check customers from id: {cfrom} to {cto}, elapsed time: {MDateTime.elapsed_time_from_seconds(Timestamp.now-tstart)}"
            customers: List[mlms.MCustomer] = (
                session.query(mlms.MCustomer)
                .join(mlms.MCash)
                .outerjoin(
                    group,
                    mlms.MCustomer.id == group.c.customerid,
                )
                .filter(
                    mlms.MCustomer.deleted == 0,
                    mlms.MCustomer.mailingnotice == 1,
                    mlms.MCustomer.id >= cfrom,
                    mlms.MCustomer.id < cto,
                    group.c.customerid == None,
                )
                .group_by(mlms.MCustomer.id)
                .having(func.sum(mlms.MCash.value) < 0)
                .order_by(mlms.MCustomer.id)
                .all()
            )
            # increment search range
            cfrom = cto
            cto += STEEP
            # analysis
            for customer in customers:
                if customer.balance >= 0 or customer.debt_timestamp == 0:
                    # positive balance or no last invoice skip
                    continue
                # cut off time
                # self.module_conf.cutoff_time
                debt_td: timedelta = MDateTime.elapsed_time_from_timestamp(
                    customer.debt_timestamp
                )
                # deadline - nr days to payment overdue
                deadline: int = (
                    customer.pay_time
                    if customer.pay_time > -1
                    else self.module_conf.default_paytime
                )
                if debt_td < MDateTime.elapsed_time_from_seconds(
                    deadline * 24 * 60 * 60
                ) or debt_td > MDateTime.elapsed_time_from_seconds(
                    (deadline + self.module_conf.cutoff_time) * 24 * 60 * 60
                ):
                    # debt over range, skip
                    continue
                # compare to payment_message
                pm = []
                for item in self.module_conf.payment_message:
                    pm.append(int(item))
                message_window_td: timedelta = (
                    debt_td
                    - MDateTime.elapsed_time_from_seconds(deadline * 24 * 60 * 60)
                )
                if message_window_td.days + 1 in pm:
                    # send message
                    self.__customer_message(customer, channel)
        if self.debug:
            self.logs.message_info = f"Customer verification time: {MDateTime.elapsed_time_from_seconds(Timestamp.now-tstart)}"

        # close session
        session.close()

    def __customer_message(self, customer: mlms.MCustomer, channel: int) -> None:
        """Prepare to send message."""
        email: int = _Keys.CONTACT_EMAIL | _Keys.CONTACT_NOTIFICATIONS
        # mobile = _Keys.CONTACT_MOBILE | _Keys.CONTACT_NOTIFICATIONS
        disabled: int = _Keys.CONTACT_DISABLED
        list_email = []
        # list_sms = []

        # skip customer on some reason
        if not customer.tariffs:
            return
        if customer.has_active_node is None:
            return

        # build contacts lists
        for item in customer.contacts:
            contact: mlms.MCustomerContact = item
            if contact.type & email == email and contact.type & disabled == 0:
                list_email.append(contact)
            # elif (
            # contact.type & mobile == mobile
            # and contact.type & disabled == 0
            # ):
            # list_sms.append(contact)

        # send emails
        if list_email:
            self.__send_customer_email(customer, list_email, channel)

        # # send sms on last notify window only
        # debt_td = MDateTime.elapsed_time_from_timestamp(
        # customer.debt_timestamp
        # )

        # if list_sms and debt_td.days == int(
        # max(self.module_conf.payment_message)
        # ):
        # self.__send_customer_sms(customer, list_sms, channel)

    def __send_customer_email(
        self,
        customer: mlms.MCustomer,
        contacts: List[mlms.CustomerContact],
        channel: int,
    ) -> None:
        """Prepare customer email and put it to communication queue."""

        if (
            self.module_conf is None
            or self.module_conf.default_paytime is None
            or self.module_conf.cutoff_time is None
            or self.module_conf.payment_message is None
            or self.qcom is None
        ):
            return None

        template = """Szanowni Państwo,

saldo na koncie na dzień {current_date} wynosi: {debt} PLN.
Prosimy o pilną weryfikację salda oraz uregulowanie należności.

Informujemy, że w przypadku nieuregulowania należności lub braku
kontaktu z biurem obsługi klienta w sprawie przedłużenia terminu
płatności, usługa dostępu do internetu zostanie zablokowana
automatycznie za {cutoff} {cutoff_suffix}.

Późniejsze odblokowani usługi będzie możliwe po zaksięgowaniu
środków na naszym koncie bankowym.

Adres panelu użytkownika:
{user_url}

Dane do zalogowania dla '{customer_name}':
ID klienta: {customer_id}
PIN: {customer_pin}

{footer}
"""
        # local variable
        debt_td: timedelta = MDateTime.elapsed_time_from_timestamp(
            customer.debt_timestamp
        )
        # deadline - nr days to payment overdue
        deadline: int = (
            customer.pay_time
            if customer.pay_time > -1
            else self.module_conf.default_paytime
        )
        # dead_td = MDateTime.elapsed_time_from_seconds(
        # deadline * 24 * 60 * 60
        # )
        cutoff_td: timedelta = MDateTime.elapsed_time_from_seconds(
            (deadline + self.module_conf.cutoff_time) * 24 * 60 * 60
        )
        cutoff: timedelta = cutoff_td - debt_td
        # create message object
        mes = Message()
        mes.channel = channel
        mes.subject = "[AIR-NET] Informacja o zaległej płatności."
        mes.messages = template.format(
            current_date=MDateTime.datenow,
            debt=customer.balance,
            cutoff=cutoff.days,
            cutoff_suffix="dzień" if cutoff.days == 1 else "dni",
            user_url=self.module_conf.user_url,
            customer_name=f"{customer.name} {customer.lastname}"
            if customer.lastname
            else f"{customer.name}",
            customer_id=customer.id,
            customer_pin=customer.pin,
            footer="\n".join(self.module_conf.message_footer)
            if isinstance(self.module_conf.message_footer, list)
            else str(self.module_conf.message_footer).replace("<br>", "\n")
            if self.module_conf.message_footer
            else "",
        )

        # add To addresses
        # for item in contacts:
        # mes.to = item
        # put message to communication queue
        self.logs.message_notice = (
            f"add message for customer: {customer.id} about balance: {customer.balance}"
        )
        self.qcom.put(mes)

    # def __send_customer_sms(
    # self,
    # customer: mlms.MCustomer,
    # contacts: List[mlms.CustomerContact],
    # channel: int,
    # ) -> None:
    # """Prepare customer text message and put it to communication queue."""

    def __add_diagnostic_debt(self, customer: mlms.MCustomer) -> None:
        """Create diagnostic information about customer."""

        if self.module_conf is None:
            return None

        nemail: int = _Keys.CONTACT_EMAIL | _Keys.CONTACT_NOTIFICATIONS
        email: int = _Keys.CONTACT_EMAIL
        # mobile = _Keys.CONTACT_MOBILE | _Keys.CONTACT_NOTIFICATIONS
        disabled: int = _Keys.CONTACT_DISABLED
        template = "<tr><td>{nr}</td><td><a href='{url}{cid}'>{cid}</a></td><td>{nazwa}</td><td>{bilans}</td><td>{od}</td><td>{info}</td></tr>"
        info = ""
        count: int = len(self._data[_Keys.DDEBT]) + 1
        # uwagi
        has_email = False
        has_nemail = False
        for item2 in customer.contacts:
            contact: mlms.MCustomerContact = item2
            if contact.type & email == email and contact.type & disabled == 0:
                has_email = True
            if contact.type & nemail == nemail and contact.type & disabled == 0:
                has_nemail = True
        if not has_email:
            info += "brak email, "
        elif not has_nemail:
            info += "brak zgody email, "
        if not customer.has_active_node:
            info += "blokada, "
        if not customer.tariffs:
            info += "brak taryf, "
        info: str = info.strip()[:-1]

        self._data[_Keys.DDEBT].append(
            template.format(
                nr=count,
                cid=customer.id,
                nazwa=f"{customer.name} {customer.lastname}",
                bilans=customer.balance,
                od=f"{MDateTime.elapsed_time_from_timestamp(customer.debt_timestamp).days} dni, {MDateTime.elapsed_time_from_seconds(MDateTime.elapsed_time_from_timestamp(customer.debt_timestamp).seconds)}",
                info=info,
                url=self.module_conf.lms_url,
            )
        )

    def __add_diagnostic_contact(self, customer: mlms.MCustomer) -> None:
        """Create diagnostic information about customer."""

        if self.module_conf is None:
            return None

        template = "<tr><td>{nr}</td><td><a href='{url}{cid}'>{cid}</a></td><td>{nazwa}</td><td>{info}</td></tr>"
        count: int = len(self._data[_Keys.DCONT]) + 1
        info: str = ""
        self._data[_Keys.DCONT].append(
            template.format(
                nr=count,
                cid=customer.id,
                nazwa=f"{customer.name} {customer.lastname}",
                info=info,
                url=self.module_conf.lms_url,
            )
        )

    def __add_diagnostic_tariff(self, customer: mlms.MCustomer) -> None:
        """Create diagnostic information about customer."""

        if self.module_conf is None:
            return None

        template = "<tr><td>{nr}</td><td><a href='{url}{cid}'>{cid}</a></td><td>{nazwa}</td><td>{info}</td></tr>"
        count: int = len(self._data[_Keys.DTARIFF]) + 1
        # uwagi
        info: str = ""
        if customer.has_active_node is not None and customer.has_active_node == True:
            info += "aktywna usługa, "
        info = info.strip()[:-1]
        self._data[_Keys.DTARIFF].append(
            template.format(
                nr=count,
                cid=customer.id,
                nazwa=f"{customer.name} {customer.lastname}",
                info=info,
                url=self.module_conf.lms_url,
            )
        )

    def __send_diagnostic(self, channel: int) -> None:
        """Make email notification for diagnostic channel."""

        if self.qcom is None:
            return None

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
        if self._data[_Keys.DDEBT]:
            mes = Message()
            mes.channel = channel
            mes.subject = "[AIR-NET] Klienci zadłużeni powyżej 30 dni."
            # head
            tmp: Dict[str, List[str]] = {}
            tmp[Multipart.HTML] = [
                "<html>",
                "<head></head>",
                "<body>",
                style,
                "<div class='centered'><h1>Wykaz klientów z przedawnionym zadłużeniem.</h1></div>",
                "<div class='centered'>",
                "<table>",
                "<tr><th>nr:</th><th>cid:</th><th>nazwa:</th><th>bilans:</th><th>od:</th><th>uwagi:</th></tr>",
            ]
            for item in self._data[_Keys.DDEBT]:
                tmp[Multipart.HTML].append(item)
            # foot
            tmp[Multipart.HTML].extend(
                [
                    "<tr><td colspan='6'><hr></td></tr>",
                    "</table>",
                    "</div>",
                    "</body>",
                    "</html>",
                ]
            )
            mes.mmessages = tmp
            # put message to communication queue
            self.qcom.put(mes)

        # contacts
        if self._data[_Keys.DCONT]:
            mes = Message()
            mes.channel = channel
            mes.subject = "[AIR-NET] Klienci bez zgody na kontakt."
            # head
            tmp: Dict[str, List[str]] = {}
            tmp[Multipart.HTML] = [
                "<html>",
                "<head></head>",
                "<body>",
                style,
                "<div class='centered'><h1>Wykaz klientów do sprawdzenia zgód kontaktowych.</h1></div>",
                "<div class='centered'>",
                "<table>",
                "<tr><th>nr:</th><th>cid:</th><th>nazwa:</th><th>uwagi:</th></tr>",
            ]
            for item in self._data[_Keys.DCONT]:
                tmp[Multipart.HTML].append(item)
            # foot
            tmp[Multipart.HTML].extend(
                [
                    "<tr><td colspan='4'><hr></td></tr>",
                    "</table>",
                    "</div>",
                    "</body>",
                    "</html>",
                ]
            )
            mes.mmessages = tmp
            # put message to communication queue
            self.qcom.put(mes)

        # tariff
        if self._data[_Keys.DTARIFF]:
            mes = Message()
            mes.channel = channel
            mes.subject = "[AIR-NET] Klienci bez taryf."
            # head
            tmp: Dict[str, List[str]] = {}
            tmp[Multipart.HTML] = [
                "<html>",
                "<head></head>",
                "<body>",
                style,
                "<div class='centered'><h1>Wykaz klientów bez przypisanych taryf.</h1></div>",
                "<div class='centered'>",
                "<table>",
                "<tr><th>nr:</th><th>cid:</th><th>nazwa:</th><th>uwagi:</th></tr>",
            ]
            for item in self._data[_Keys.DTARIFF]:
                tmp[Multipart.HTML].append(item)
            # foot
            tmp[Multipart.HTML].extend(
                [
                    "<tr><td colspan='4'><hr></td></tr>",
                    "</table>",
                    "</div>",
                    "</body>",
                    "</html>",
                ]
            )
            mes.mmessages = tmp
            # put message to communication queue
            self.qcom.put(mes)
        # clean buffer
        self.__clean_diagnostic()

    def run(self) -> None:
        """Main loop."""
        self.logs.message_notice = "starting..."

        if (
            self.module_conf is None
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
        dbh = _Database(
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
        while not self.stopped:
            if channel and channel.check:
                if self.debug:
                    self.logs.message_debug = "expired channel found"
                for chan in channel.get:
                    # diagnostic channel
                    if (
                        self.module_conf.diagnostic_channel
                        and chan in self.module_conf.diagnostic_channel
                    ):
                        self.__get_customers_for_verification(dbh, int(chan))
                    # message channel
                    if (
                        self.module_conf.message_channel
                        and chan in self.module_conf.message_channel
                    ):
                        self.__get_indebted_customers(dbh, int(chan))
            self.sleep()

        # exiting from loop
        self.logs.message_notice = "exit"

    def sleep(self) -> None:
        """Sleep interval for main loop."""
        sbreak: float = Timestamp.now + self.sleep_period
        while not self.stopped and sbreak > Timestamp.now:
            time.sleep(0.2)

    def stop(self) -> None:
        """Set stop event."""
        if self._debug:
            self.logs.message_debug = "stop signal received"
        if self._stop_event:
            self._stop_event.set()

    @property
    def debug(self) -> bool:
        """Return debug flag."""
        if self._debug is not None:
            return self._debug
        return False

    @property
    def verbose(self) -> bool:
        """Return verbose flag."""
        return self._verbose

    @property
    def stopped(self) -> bool:
        """Return stop flag."""
        if self._stop_event:
            return self._stop_event.is_set()
        return True

    @property
    def module_conf(self) -> Optional[_ModuleConf]:
        """Return module conf object."""
        return self._data[_ModuleConf.Keys.MODCONF]

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
        out.append(TemplateConfigItem(desc="LMS payment notification module."))
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
                desc=f"'{_Keys.DCHANNEL}' [List[str]] - diagnostic channels for sending statistics."
            )
        )
        out.append(
            TemplateConfigItem(
                desc=f"'{_ModuleConf.Keys.MESSAGE_CHANNEL}' [List[str]] - message channels for notifications sent to customers."
            )
        )
        out.append(
            TemplateConfigItem(
                desc=f"'{_Keys.SKIP_GROUPS}' [List[int]] - list of lms group ids to skip."
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
                desc=f"'{_Keys.MNOTIFY}' [list] - list of days from the payment expiration"
            )
        )
        out.append(
            TemplateConfigItem(
                desc="in which notifications are to be sent to the customer."
            )
        )
        out.append(
            TemplateConfigItem(
                desc=f"'{_Keys.LMS_URL}' [str] - URL to customer information panel,"
            )
        )
        out.append(
            TemplateConfigItem(
                desc="usually: 'https://domain_name/?m=customerinfo&id='"
            )
        )
        out.append(
            TemplateConfigItem(
                desc=f"'{_Keys.USER_URL}' [str] - URL to individual customer panel,"
            )
        )
        out.append(
            TemplateConfigItem(
                varname=_Keys.AT_CHANNEL,
                value=["1:0;0;7|10|12|13;*;*", "1:0;8|12|16|21;14;*;*"],
            )
        )
        out.append(TemplateConfigItem(varname=_Keys.DCHANNEL, value=[]))
        out.append(
            TemplateConfigItem(varname=_ModuleConf.Keys.MESSAGE_CHANNEL, value=[1])
        )
        out.append(
            TemplateConfigItem(
                varname=_Keys.MNOTIFY,
                value=[],
                desc="days of sending the notification after the due date",
            )
        )
        out.append(
            TemplateConfigItem(
                varname=_Keys.DPAYTIME,
                value=7,
                desc="[int] - default payment date as the number of days from invoice issuance",
            )
        )
        out.append(
            TemplateConfigItem(
                varname=_Keys.CUTOFF,
                value=14,
                desc=f"[int] - number of days after {_Keys.DPAYTIME} after which the service will be disabled",
            )
        )
        out.append(
            TemplateConfigItem(
                varname=_Keys.SKIP_GROUPS, value=[], desc="List[int] - lms group ids"
            )
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
        out.append(TemplateConfigItem(varname=_Keys.LMS_URL, value=""))
        out.append(TemplateConfigItem(varname=_Keys.USER_URL, value=""))
        out.append(
            TemplateConfigItem(
                varname=_Keys.MFOOTER,
                value=[],
                desc="List[str] - personal footer added to the email.",
            )
        )
        return out


# #[EOF]#######################################################################
