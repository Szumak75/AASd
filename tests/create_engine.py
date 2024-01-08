#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 05.12.2023

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

# gc.set_debug(
# gc.DEBUG_COLLECTABLE
# gc.DEBUG_LEAK
# | gc.DEBUG_SAVEALL
# | gc.DEBUG_STATS
# | gc.DEBUG_UNCOLLECTABLE
# )


def heap_results():
    from guppy import hpy

    hp = hpy()
    h = hp.heap()
    print(h)


def get_session(dblist: List) -> Session:
    """."""
    session = None
    for dbh in dblist:
        try:
            session = Session(dbh)
            session.query(func.max(mlms.MCustomer.id))
        except:
            session = None
            continue

    return session


print(f"Garbage: {gc.collect()}")
salt = 387741

ips = ["10.5.0.37", "10.5.0.36", "10.5.0.39"]
engines = []
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

# heap_results()

for dialect in ("pymysql", "mysqlconnector"):
    for ip in ips:
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
        # print(url)
        config["db.url"] = url
        dbh = engine_from_config(config, prefix="db.")
        try:
            ctest = False
            with dbh.connect() as connection:
                connection.execute(text("SELECT 1"))
                print(f"Connected to: {dbh.url}")
                ctest = True
        except Exception as ex:
            print(f"exception: {ex}")
        if ctest:
            engines.append(dbh)

session = get_session(engines)

maxid = session.query(func.max(mlms.MCustomer.id)).first()[0]
cfrom = 9000
cto = 9100
count = 0
while cfrom < maxid:
    customers: List[mlms.MCustomer] = (
        session.query(mlms.MCustomer)
        .filter(
            mlms.MCustomer.deleted == 0,
            and_(mlms.MCustomer.id >= cfrom, mlms.MCustomer.id < cto),
        )
        .all()
    )
    for item in customers:
        customer: mlms.MCustomer = item
        if customer.balance < 0:
            count += 1
            print(
                f"[{count}] CID: {customer.id}, Balance: {customer.balance}, Pay Time: {customer.pay_time}"
            )
            # for item2 in customer.cash_operations:
            #     cash: mlms.MCash = item2
            #     if cash.docid:
            #         print(cash.doc)
    cfrom = cto
    cto += 100
    # heap_results()
    print(f"Garbage: {gc.collect()}")

# heap_results()
print(f"Garbage: {gc.collect()}")
session.close()
print(f"Garbage: {gc.collect()}")
# heap_results()
sys.exit(0)

##########################################################
sql_uri_template = "mysql+{}://{}:{}@{}:{}/{}{}".format(
    "pymysql",
    "lms3",
    f"{SimpleCrypto.multiple_decrypt(salt, '//4AAHAAAABMAAAAagAAAEkAAAA1AAAAZAAAADcAAAB6AAAAbgAAAGcAAABtAAAANQAAAE0AAABlAAAASgAAAHUAAAA=')}",
    ip,
    "3306",
    "lmsv3",
    "?charset=utf8mb4",
)


sql_engine_options = {
    "pool_recycle": 60,
}

engine = create_engine(
    cstr,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=10,
    pool_pre_ping=True,
    connect_args={
        "connect_timeout": 20,
    },
)
with engine.connect() as connection:
    connection.execute(text("SELECT 1"))

try:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
        print(f"create session for {engine}")
    session = Session(engine)
    if session is None:
        print("session is none")
except Exception as ex:
    print(f"Exception: '{ex}'")

#
if session:
    customers: mlms.MCustomer = (
        session.query(mlms.MCustomer)
        .filter(
            mlms.MCustomer.deleted == 0,
            mlms.MCustomer.id == 1679,
            mlms.MCustomer.paytime != "-1",
        )
        .all()
    )
    count = 0
    for item1 in customers:
        customer: mlms.MCustomer = item1
        # print(customer.has_active_node)
        count += 1
        print(f"{count}: CID: {customer.id} Termin płatności: {customer.paytime}")
        if True:
            continue
        if customer.balance < 0:
            if customer.tariffs and customer.has_active_node is not None:
                print(customer)
                continue
            # print(customer.cash_operations)
            balance = 0
            for item2 in customer.cash_operations:
                cash: mlms.Cash = item2
                # print(cash)
                balance += cash.value
                print(
                    "{time} {value}/{balance}  {doc}  {comment}".format(
                        time=MDateTime.datetime_from_timestamp(cash.time),
                        value=cash.value,
                        balance=balance,
                        doc=True if cash.docid else False,
                        comment=cash.comment,
                    )
                )

            print(customer.balance)
            print(customer.debt_timestamp)
            print(MDateTime.datetime_from_timestamp(customer.debt_timestamp))
            print(MDateTime.elapsed_time_from_timestamp(customer.debt_timestamp))
            print(
                f"consent date: {MDateTime.datetime_from_timestamp(customer.consentdate)}"
            )
            print(
                f"cutoff stop: {MDateTime.datetime_from_timestamp(customer.cutoffstop)}"
            )
            for item2 in customer.tariffs:
                tariff: mlms.Tariff = item2
                print(tariff)

# #[EOF]#######################################################################
