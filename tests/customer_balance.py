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

from sqlalchemy import create_engine, or_, text
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
from libs.interfaces.conf import IModuleConfig
from libs.templates.modules import TemplateConfigItem
from libs.com.message import Message, Multipart, AtChannel
from libs.tools.datetool import MDateTime

import libs.db_models.mlms as mlms

salt = 387741

cstr = "mysql+{}://{}:{}@{}:{}/{}{}".format(
    "pymysql",
    "lms3",
    f"{SimpleCrypto.multiple_decrypt(salt, '//4AAHAAAABMAAAAagAAAEkAAAA1AAAAZAAAADcAAAB6AAAAbgAAAGcAAABtAAAANQAAAE0AAABlAAAASgAAAHUAAAA=')}",
    "10.5.00.37",
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
        "connect_timeout": 2,
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
            mlms.MCustomer.id == 7236,
        )
        .all()
    )
    for item1 in customers:
        customer: mlms.MCustomer = item1
        if customer.balance < 0:
            if customer.tariffs and customer.has_active_node is not None:
                print(customer)
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
            print(customer.dept_timestamp)
            print(MDateTime.datetime_from_timestamp(customer.dept_timestamp))
            print(
                MDateTime.elapsed_time_from_timestamp(
                    customer.dept_timestamp
                )
            )

# #[EOF]#######################################################################
