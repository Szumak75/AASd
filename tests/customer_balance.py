#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 05.12.2023

  Purpose:
"""

import time
from datetime import timedelta

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
            mlms.MCustomer.id == 10068,
            # mlms.MCustomer.paytime != "-1",
        )
        .all()
    )
    count = 0
    for customer in customers:
        # print(customer.has_active_node)
        count += 1
        start = time.time()
        print(customer.sum_cash)
        stop = time.time()
        print(stop - start)

        start = time.time()
        print(customer.balance)
        stop = time.time()
        print(stop - start)
        print(
            f"{count}: CID: {customer.id} Termin płatności: {customer.pay_time}, Bilans: {customer.balance}"
        )
        debt_td: timedelta = MDateTime.elapsed_time_from_timestamp(
            customer.debt_timestamp
        )
        deadline: int = customer.pay_time

        print(
            f"debt_td: {debt_td} && deadline: {MDateTime.elapsed_time_from_seconds(deadline * 24 * 60 * 60)}"
        )
        if debt_td < MDateTime.elapsed_time_from_seconds(deadline * 24 * 60 * 60):
            print("skip")
        else:
            pm = [3, 11]
            message_window_td: timedelta = (
                debt_td - MDateTime.elapsed_time_from_seconds(deadline * 24 * 60 * 60)
            )
            print(f"message window: {message_window_td}")

            if message_window_td.days in pm:

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
                cutoff_td: timedelta = MDateTime.elapsed_time_from_seconds(
                    (deadline + 14 + 1) * 24 * 60 * 60
                )
                cutoff: timedelta = cutoff_td - debt_td
                print(f"cutoff_td: {cutoff_td}, cutoff: {cutoff}")
                messages = template.format(
                    current_date=MDateTime.datenow,
                    debt=customer.balance,
                    cutoff=cutoff.days,
                    cutoff_suffix="dzień" if cutoff.days == 1 else "dni",
                    user_url="self.module_conf.user_url",
                    customer_name=(
                        f"{customer.name} {customer.lastname}"
                        if customer.lastname
                        else f"{customer.name}"
                    ),
                    customer_id=customer.id,
                    customer_pin=customer.pin,
                    footer="",
                )

                print(messages)

# #[EOF]#######################################################################
