#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
  create_engine_failover.py.py
  Author : Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 10.01.2024, 14:56:46
  
  Purpose: 
"""


import time, sys, gc
from inspect import currentframe
from typing import Dict, List, Optional, Tuple, Any
from threading import Thread, Event
from queue import Queue

from sqlalchemy import create_engine, or_, and_, text, func
from sqlalchemy.orm import (
    Session,
    sessionmaker,
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy.pool import QueuePool
from sqlalchemy.engine.base import Engine
from sqlalchemy.engine import URL, engine_from_config
from sqlalchemy.util import immutabledict

from jsktoolbox.libs.base_th import ThBaseObject
from jsktoolbox.logstool.logs import LoggerClient, LoggerQueue, LoggerEngine
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
    CUTOFF = "cutoff_time"
    DCHANNEL = "diagnostic_channel"
    DPAYTIME = "default_paytime"
    LMS_URL = "lms_url"
    MCHANNEL = "message_channel"
    MFOOTER = "message_footer"
    MNOTIFY = "payment_message"
    SLEEP_PERIOD = "sleep_period"
    SQL_DATABASE = "sql_database"
    SQL_PASS = "sql_password"
    SQL_SERVER = "sql_server"
    SQL_USER = "sql_user"
    USER_URL = "user_url"
    # contact types
    # email notification: 8|32=40, type&40==40 and type&16384==0
    # mobile notification: 1|32=33, type&33==33 and type&16384==0
    # type&16384|8|32==40 - True
    CONTACT_BANKACCOUNT = 64
    CONTACT_DISABLED = 16384
    CONTACT_DOCUMENTS = 32768
    CONTACT_EMAIL = 8
    CONTACT_FAX = 2
    CONTACT_IM = 7680
    CONTACT_IM_FACEBOOK = 4096
    CONTACT_IM_GG = 512
    CONTACT_IM_SKYPE = 2048
    CONTACT_IM_YAHOO = 1024
    CONTACT_INVOICES = 16
    CONTACT_LANDLINE = 4
    CONTACT_MOBILE = 1
    CONTACT_NOTIFICATIONS = 32
    CONTACT_TECHNICAL = 128
    CONTACT_URL = 256
    # diagnostic
    DCONT = "__cont__"
    DDEBT = "__debt__"
    DTARIFF = "__tariff__"


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

    def create_connections2(self) -> bool:
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
                        url=url, connect_args=connection_args
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
                engine: Engine = create_engine(url=url, connect_args=connection_args)
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

    def create_connections(self) -> bool:
        """Create connections pool."""
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
                self.logs.message_notice = f"check query: {var}"
                if self._debug:
                    self.logs.message_debug = f"create session for {engine}"

            except:
                session = None
            else:
                break

        return session


if __name__ == "__main__":
    salt = 387741
    lqueue = LoggerQueue()
    lengine = LoggerEngine()
    lengine.logs_queue = lqueue
    lc = LoggerClient(lqueue, "main")

    lc.message_info = "create database connection"
    # database connection
    dbh = _Database(
        lqueue,
        {
            _Keys.SQL_SERVER: ["10.5.0.39", "10.5.0.37", "10.5.0.36"],
            # _Keys.SQL_SERVER: ["10.5.0.36", "10.5.0.37", "10.5.0.39"],
            _Keys.SQL_DATABASE: "lmsv3",
            _Keys.SQL_USER: "lms3",
            _Keys.SQL_PASS: f"{SimpleCrypto.multiple_decrypt(salt, '//4AAHAAAABMAAAAagAAAEkAAAA1AAAAZAAAADcAAAB6AAAAbgAAAGcAAABtAAAANQAAAE0AAABlAAAASgAAAHUAAAA=')}",
        },
        verbose=True,
        debug=True,
    )

    dbh.create_connections2()
    lc.message_info = "getting session"
    session = dbh.session
    if session:
        lc.message_info = f"session object: {session}"
        start = Timestamp.now
        cfrom = 0
        cto = 100
        count = 0

        customers: List[mlms.MCustomer] = (
            session.query(mlms.MCustomer)
            .filter(
                mlms.MCustomer.deleted == 0,
                and_(mlms.MCustomer.id >= cfrom, mlms.MCustomer.id < cto),
            )
            .all()
        )
        for customer in customers:
            lc.message_info = f"cid={customer.id} elapsed time: {MDateTime.elapsed_time_from_seconds(Timestamp.now-start)}"
            if customer.balance < 0:
                count += 1
                lc.message_info = f"[{count}], balance: {customer.balance}"
            lengine.send()

        session.close()
        stop = Timestamp.now
        lc.message_notice = (
            f"Exec time: {MDateTime.elapsed_time_from_seconds(stop-start)}"
        )

    lengine.send()


# #[EOF]#######################################################################
