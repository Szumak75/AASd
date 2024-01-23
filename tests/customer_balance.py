#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 05.12.2023

  Purpose:
"""

import time
from inspect import currentframe
from typing import Dict, List, Optional, Tuple, Any
from threading import Thread, Event
from queue import Queue

from sqlalchemy import create_engine, or_, text, func
from sqlalchemy.orm import (
    Session,
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy.pool import QueuePool
from sqlalchemy.engine.base import Engine

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

salt = 387741

cstr = "mysql+{}://{}:{}@{}:{}/{}{}".format(
    "pymysql",
    "lms3",
    f"{SimpleCrypto.multiple_decrypt(salt, '//4AAHAAAABMAAAAagAAAEkAAAA1AAAAZAAAADcAAAB6AAAAbgAAAGcAAABtAAAANQAAAE0AAABlAAAASgAAAHUAAAA=')}",
    "10.5.0.37",
    "3306",
    "lmsv3",
    "?charset=utf8mb4",
)
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

session = None
try:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
        print(f"create session for {engine}")
    session = Session(engine)
    session.query(func.max(mlms.MCustomer.id))
except Exception as ex:
    print(f"Exception: '{ex}'")

#
if session is not None:
    customers: List[mlms.MCustomer] = (
        session.query(mlms.MCustomer)
        .filter(
            mlms.MCustomer.deleted == 0,
            # mlms.MCustomer.id == 7,
            # mlms.MCustomer.paytime != "-1",
        )
        .all()
    )
    count = 0
    for item1 in customers:
        customer: mlms.MCustomer = item1
        # print(customer.has_active_node)
        count += 1
        print(
            f"{count}: CID: {customer.id} Termin płatności: {customer.pay_time}, Bilans: {customer.balance}"
        )
        # for item2 in customer.cash_operations:
        # cash: mlms.MCash = item2
        # print(cash)
        # if True:
        # continue
        if customer.balance < 0:
            # if customer.tariffs and customer.has_active_node is not None:
            # print(customer)
            # continue
            # print(customer.cash_operations)
            balance = 0
            for item2 in customer.cash_operations:
                cash: mlms.MCash = item2
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
